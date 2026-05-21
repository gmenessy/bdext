import logging
from typing import List, Dict, Optional

from prompt_optimizer.models import TaskBundle, ModelConfig, EvalResult, Phase, OptimizationStep, CandidateEvaluation
from prompt_optimizer.config import AppConfig
from prompt_optimizer.target_runner import TargetRunner
from prompt_optimizer.judge import JudgeCommittee
from prompt_optimizer.optimizer import OptimizerCommittee
from prompt_optimizer.acceptance import AcceptanceLogic
from prompt_optimizer.prompt_state import PromptState
from prompt_optimizer.scoring import mean_overall, mean_by_group, weakest_dimension

class OptimizationLoop:
    def __init__(
        self,
        config: AppConfig,
        target_runner: TargetRunner,
        judge_committee: JudgeCommittee,
        optimizer_committee: OptimizerCommittee,
        acceptance_logic: AcceptanceLogic
    ):
        self.config = config
        self.target_runner = target_runner
        self.judge_committee = judge_committee
        self.optimizer_committee = optimizer_committee
        self.acceptance_logic = acceptance_logic
        self.logger = logging.getLogger(__name__)

    def _evaluate_state(
        self,
        state: PromptState,
        bundle: TaskBundle,
        target_model: ModelConfig
    ) -> List[EvalResult]:

        results = []
        for group in bundle.groups:
            user_prompt = state.user_prompts_by_group[group.group_id]
            for case in group.test_cases:
                try:
                    output = self.target_runner.run(
                        model_config=target_model,
                        system_prompt=state.system_prompt,
                        user_prompt=user_prompt,
                        test_case=case,
                        temperature=self.config.temperatures.target
                    )

                    committee_result = self.judge_committee.evaluate(
                        target_output=output,
                        test_case=case,
                        temperature=self.config.temperatures.judge
                    )

                    results.append(EvalResult(
                        target_model_name=target_model.name,
                        group_id=group.group_id,
                        case_id=case.case_id,
                        output=output.output,
                        committee=committee_result
                    ))
                except Exception as e:
                    self.logger.error(f"Fehler bei Evaluierung {case.case_id}: {e}")

        return results

    def _optimize_phase(
        self,
        phase: Phase,
        iteration: int,
        state: PromptState,
        bundle: TaskBundle,
        target_model: ModelConfig,
        baseline_results: List[EvalResult],
        group_id: Optional[str] = None
    ) -> OptimizationStep:

        baseline_mean = mean_overall(baseline_results)
        baseline_groups = mean_by_group(baseline_results)
        weakest_dim = weakest_dimension(baseline_results)

        if phase == Phase.SYSTEM:
            current_prompt = state.system_prompt
        else:
            current_prompt = state.user_prompts_by_group[group_id]

        candidates = self.optimizer_committee.generate_candidates(
            phase=phase,
            current_prompt=current_prompt,
            weakest_dimension=weakest_dim,
            eval_results=baseline_results,
            temperature=self.config.temperatures.optimizer
        )

        evaluations: List[CandidateEvaluation] = []
        best_eval: Optional[CandidateEvaluation] = None

        for candidate in candidates:
            # Test candidate
            test_state = state.model_copy(deep=True)
            if phase == Phase.SYSTEM:
                test_state.system_prompt = candidate.prompt_text
            else:
                test_state.user_prompts_by_group[group_id] = candidate.prompt_text

            candidate_results = self._evaluate_state(test_state, bundle, target_model)
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

            if evaluation.accepted:
                if best_eval is None or evaluation.delta > best_eval.delta:
                    best_eval = evaluation

        accepted_id = None
        if best_eval:
            accepted_id = best_eval.candidate.candidate_id
            # Apply changes to state
            if phase == Phase.SYSTEM:
                state.system_prompt = best_eval.candidate.prompt_text
            else:
                state.user_prompts_by_group[group_id] = best_eval.candidate.prompt_text

        return OptimizationStep(
            iteration=iteration,
            phase=phase,
            target_model_name=target_model.name,
            group_id=group_id,
            candidates=evaluations,
            accepted_candidate_id=accepted_id
        )

    def run_for_model(
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

        baseline_train_results = self._evaluate_state(state, train_bundle, target_model)

        patience_counter = 0
        max_iterations = min(self.config.run.max_iterations, 10)

        steps = []

        for iteration in range(1, max_iterations + 1):
            self.logger.info(f"Iteration {iteration} für Modell {target_model.name}")
            any_improvement = False
            max_improvement_this_iter = 0.0

            # Phase A: System Prompt
            step_a = self._optimize_phase(
                phase=Phase.SYSTEM,
                iteration=iteration,
                state=state,
                bundle=train_bundle,
                target_model=target_model,
                baseline_results=self._evaluate_state(state, train_bundle, target_model)
            )
            steps.append(step_a)
            if step_a.accepted_candidate_id:
                any_improvement = True
                best_cand = next(c for c in step_a.candidates if c.candidate.candidate_id == step_a.accepted_candidate_id)
                max_improvement_this_iter = max(max_improvement_this_iter, best_cand.delta)

            # Phase B: User Prompts per Group
            for group in train_bundle.groups:
                # Evaluate specifically for this group to focus optimizer
                current_results = self._evaluate_state(state, train_bundle, target_model)
                group_results = [r for r in current_results if r.group_id == group.group_id]

                step_b = self._optimize_phase(
                    phase=Phase.USER,
                    iteration=iteration,
                    state=state,
                    bundle=train_bundle,
                    target_model=target_model,
                    baseline_results=group_results,
                    group_id=group.group_id
                )
                steps.append(step_b)
                if step_b.accepted_candidate_id:
                    any_improvement = True
                    best_cand = next(c for c in step_b.candidates if c.candidate.candidate_id == step_b.accepted_candidate_id)
                    # For relative improvement check, we might want to scale group delta but using absolute delta for now
                    max_improvement_this_iter = max(max_improvement_this_iter, best_cand.delta)

            # Early stopping check: patience and 5% improvement rule
            # Rule: if after 2 iterations no > 5% improvement occurs, stop.
            # Delta is absolute (1-10 scale), 5% improvement is roughly > 0.5 points
            # For simplicity, we interpret "5% Änderung" relative to mean_score, or hardcoded min_delta if larger
            if not any_improvement or max_improvement_this_iter < 0.5:
                patience_counter += 1
            else:
                patience_counter = 0

            if patience_counter >= self.config.run.patience:
                self.logger.info(f"Early stopping nach Iteration {iteration} ausgelöst (patience={self.config.run.patience}).")
                break

        # Final Test Evaluation
        test_results = self._evaluate_state(state, test_bundle, target_model)

        return {
            "target_model_name": target_model.name,
            "final_state": state.model_dump(),
            "baseline_train_results": [r.model_dump() for r in baseline_train_results],
            "optimization_steps": [s.model_dump() for s in steps],
            "test_results": [r.model_dump() for r in test_results]
        }
