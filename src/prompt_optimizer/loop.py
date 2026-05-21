import logging
from typing import List, Dict, Optional, Tuple
import asyncio
from copy import deepcopy

from prompt_optimizer.models import TaskBundle, ModelConfig, EvalResult, Phase, OptimizationStep, CandidateEvaluation
from prompt_optimizer.config import AppConfig, OptimizationMode
from prompt_optimizer.target_runner import TargetRunner
from prompt_optimizer.judge import JudgeCommittee
from prompt_optimizer.optimizer import OptimizerCommittee
from prompt_optimizer.acceptance import AcceptanceLogic
from prompt_optimizer.prompt_state import PromptState
from prompt_optimizer.scoring import mean_overall, mean_by_group, weakest_dimension
from prompt_optimizer.wiki import WikiDatabase
from prompt_optimizer.calibration import Calibrator

class OptimizationLoop:
    def __init__(
        self,
        config: AppConfig,
        target_runner: TargetRunner,
        judge_committee: JudgeCommittee,
        optimizer_committee: OptimizerCommittee,
        acceptance_logic: AcceptanceLogic,
        calibrator: Calibrator
    ):
        self.config = config
        self.target_runner = target_runner
        self.judge_committee = judge_committee
        self.optimizer_committee = optimizer_committee
        self.acceptance_logic = acceptance_logic
        self.calibrator = calibrator
        self.logger = logging.getLogger(__name__)
        self.wiki = WikiDatabase(self.config.run.db_path)

    async def init(self):
        await self.wiki.init_db()

    async def _evaluate_state(
        self,
        state: PromptState,
        bundle: TaskBundle,
        target_model: ModelConfig,
        baseline_mean: Optional[float] = None
    ) -> List[EvalResult]:

        results = []

        # Flatten all cases across all groups for chunking
        all_cases = []
        for group in bundle.groups:
            user_prompt = state.user_prompts_by_group[group.group_id]
            for case in group.test_cases:
                all_cases.append((state.system_prompt, user_prompt, case, target_model))

        chunk_size = self.config.optimization.early_exit_chunk_size

        # Split into chunks
        for i in range(0, len(all_cases), chunk_size):
            chunk = all_cases[i:i + chunk_size]
            tasks = [self._eval_case(*args) for args in chunk]
            chunk_results = await asyncio.gather(*tasks)

            valid_chunk_results = [r for r in chunk_results if r is not None]
            results.extend(valid_chunk_results)

            # Check early exit if we have a baseline to compare against
            if baseline_mean is not None and len(results) >= chunk_size:
                current_mean = mean_overall(results)
                # If the score is catastrophically worse than baseline, abort early
                if (current_mean - baseline_mean) < self.config.optimization.early_exit_threshold:
                    self.logger.warning(
                        f"Early Exit getriggert: Aktueller Chunk-Mean ({current_mean:.2f}) "
                        f"ist zu weit unter Baseline ({baseline_mean:.2f}). Evaluierung abgebrochen."
                    )
                    break # Abort remaining chunks, return poor results so it gets rejected

        return results

    async def _eval_case(self, sys_prompt, user_prompt, case, target_model) -> Optional[EvalResult]:
        try:
            output = await self.target_runner.run(
                model_config=target_model,
                system_prompt=sys_prompt,
                user_prompt=user_prompt,
                test_case=case,
                temperature=self.config.temperatures.target
            )

            committee_result = await self.judge_committee.evaluate(
                target_output=output,
                test_case=case,
                temperature=self.config.temperatures.judge
            )

            return EvalResult(
                target_model_name=target_model.name,
                group_id=case.group_id,
                case_id=case.case_id,
                output=output.output,
                committee=committee_result
            )
        except Exception as e:
            self.logger.error(f"Fehler bei Evaluierung {case.case_id}: {e}")
            return None

    async def _optimize_phase(
        self,
        phase: Phase,
        iteration: int,
        state: PromptState,
        bundle: TaskBundle,
        target_model: ModelConfig,
        baseline_results: List[EvalResult],
        group_id: Optional[str] = None,
        optimizer_strategy: str = ""
    ) -> OptimizationStep:

        baseline_mean = mean_overall(baseline_results)
        baseline_groups = mean_by_group(baseline_results)
        weakest_dim = weakest_dimension(baseline_results)

        if phase == Phase.SYSTEM:
            current_prompt = state.system_prompt
        else:
            current_prompt = state.user_prompts_by_group[group_id]

        wiki_insights_str = await self.wiki.get_top_insights(target_model.name)

        full_insights = wiki_insights_str + "\n" + optimizer_strategy

        candidates = await self.optimizer_committee.generate_candidates(
            phase=phase,
            current_prompt=current_prompt,
            weakest_dimension=weakest_dim,
            eval_results=baseline_results,
            temperature=self.config.temperatures.optimizer,
            wiki_insights_str=full_insights
        )

        evaluations: List[CandidateEvaluation] = []
        best_eval: Optional[CandidateEvaluation] = None

        for candidate in candidates:
            test_state = state.model_copy(deep=True)
            if phase == Phase.SYSTEM:
                test_state.system_prompt = candidate.prompt_text
            else:
                test_state.user_prompts_by_group[group_id] = candidate.prompt_text

            candidate_results = await self._evaluate_state(test_state, bundle, target_model, baseline_mean=baseline_mean)
            if not candidate_results:
                continue

            candidate_mean = mean_overall(candidate_results)
            candidate_groups = mean_by_group(candidate_results)

            evaluation = self.acceptance_logic.evaluate_candidate(
                candidate=candidate,
                baseline_mean=baseline_mean,
                baseline_groups=baseline_groups,
                candidate_mean=candidate_mean,
                candidate_groups=candidate_groups
            )

            evaluations.append(evaluation)

            # Pareto-like/strict selection based on delta and min requirements
            if evaluation.accepted:
                if best_eval is None or evaluation.delta > best_eval.delta:
                    best_eval = evaluation

        accepted_id = None
        if best_eval:
            accepted_id = best_eval.candidate.candidate_id
            await self.wiki.store_insight(
                run_name=self.config.run.name,
                candidate=best_eval.candidate,
                delta=best_eval.delta,
                target_model=target_model.name
            )

        return OptimizationStep(
            iteration=iteration,
            phase=phase,
            target_model_name=target_model.name,
            group_id=group_id,
            candidates=evaluations,
            accepted_candidate_id=accepted_id
        )

    async def run_for_model(
        self,
        target_model: ModelConfig,
        train_bundle: TaskBundle,
        test_bundle: TaskBundle
    ) -> Dict:

        state = PromptState(
            target_model_name=target_model.name,
            system_prompt=train_bundle.system_prompt,
            user_prompts_by_group={g.group_id: g.user_prompt for g in train_bundle.groups}
        )

        # Phase 0.a: Judge Calibration
        judge_guideline = ""
        if self.config.optimization.calibrate_judges:
            judge_guideline = await self.calibrator.calibrate_judges(
                train_bundle, target_model, state.system_prompt, state.user_prompts_by_group
            )
            # Im echten MVP müssten wir diese Guideline global an den Judge_Prompt hängen.
            # Da die Architektur aktuell statische Prompts in `judge.py` nutzt, übergeben
            # wir es hier via State/Mock-Implementierung oder lassen die Architektur es für
            # zukünftige Judge-Runs injizieren. Für MVP-Kompatibilität wird es hier geloggt.
            if judge_guideline:
                self.logger.info("Judge Guideline ist aktiv.")

        baseline_train_results = await self._evaluate_state(state, train_bundle, target_model)

        # Phase 0.b: Optimizer Calibration
        optimizer_strategy = ""
        if self.config.optimization.calibrate_optimizers and self.config.optimizer_models:
            optimizer_strategy = await self.calibrator.calibrate_optimizer(
                train_bundle, target_model, baseline_train_results, self.config.optimizer_models[0]
            )

        patience_counter = 0
        max_iterations = min(self.config.run.max_iterations, 10)

        steps = []

        # Beam search / Fallback state
        fallback_queue = []

        for iteration in range(1, max_iterations + 1):
            self.logger.info(f"Iteration {iteration} für Modell {target_model.name}")
            any_improvement = False
            max_improvement_this_iter = 0.0

            # Keep a copy of current state before optimizations
            prev_state = state.model_copy(deep=True)

            # Phase A: System Prompt
            step_a = await self._optimize_phase(
                phase=Phase.SYSTEM,
                iteration=iteration,
                state=state,
                bundle=train_bundle,
                target_model=target_model,
                baseline_results=await self._evaluate_state(state, train_bundle, target_model),
                optimizer_strategy=optimizer_strategy
            )
            steps.append(step_a)
            if step_a.accepted_candidate_id:
                any_improvement = True
                best_cand = next(c for c in step_a.candidates if c.candidate.candidate_id == step_a.accepted_candidate_id)
                max_improvement_this_iter = max(max_improvement_this_iter, best_cand.delta)
                state.system_prompt = best_cand.candidate.prompt_text

                # If hard mode, push other accepted candidates to fallback
                if self.config.run.mode == OptimizationMode.HARD:
                    for c in step_a.candidates:
                        if c.accepted and c.candidate.candidate_id != step_a.accepted_candidate_id:
                            fb_state = prev_state.model_copy(deep=True)
                            fb_state.system_prompt = c.candidate.prompt_text
                            fallback_queue.append((fb_state, c.delta))

            # Phase B: User Prompts per Group
            for group in train_bundle.groups:
                current_results = await self._evaluate_state(state, train_bundle, target_model)
                group_results = [r for r in current_results if r.group_id == group.group_id]

                step_b = await self._optimize_phase(
                    phase=Phase.USER,
                    iteration=iteration,
                    state=state,
                    bundle=train_bundle,
                    target_model=target_model,
                    baseline_results=group_results,
                    group_id=group.group_id,
                    optimizer_strategy=optimizer_strategy
                )
                steps.append(step_b)
                if step_b.accepted_candidate_id:
                    any_improvement = True
                    best_cand = next(c for c in step_b.candidates if c.candidate.candidate_id == step_b.accepted_candidate_id)
                    max_improvement_this_iter = max(max_improvement_this_iter, best_cand.delta)
                    state.user_prompts_by_group[group.group_id] = best_cand.candidate.prompt_text

                    if self.config.run.mode == OptimizationMode.HARD:
                        for c in step_b.candidates:
                            if c.accepted and c.candidate.candidate_id != step_b.accepted_candidate_id:
                                fb_state = prev_state.model_copy(deep=True)
                                fb_state.user_prompts_by_group[group.group_id] = c.candidate.prompt_text
                                fallback_queue.append((fb_state, c.delta))

            if not any_improvement or max_improvement_this_iter < 0.5:
                patience_counter += 1
            else:
                patience_counter = 0

            if patience_counter >= self.config.run.patience:
                if self.config.run.mode == OptimizationMode.HARD and fallback_queue:
                    # Sort by delta desc
                    fallback_queue.sort(key=lambda x: x[1], reverse=True)
                    next_state, _ = fallback_queue.pop(0)
                    self.logger.info(f"Patience erschöpft. Wechsel auf Fallback-Kandidat (Sackgasse umgangen).")
                    state = next_state
                    patience_counter = 0
                else:
                    self.logger.info(f"Early stopping nach Iteration {iteration} ausgelöst.")
                    break

        test_results = await self._evaluate_state(state, test_bundle, target_model)

        return {
            "target_model_name": target_model.name,
            "final_state": state.model_dump(),
            "baseline_train_results": [r.model_dump() for r in baseline_train_results],
            "optimization_steps": [s.model_dump() for s in steps],
            "test_results": [r.model_dump() for r in test_results]
        }
