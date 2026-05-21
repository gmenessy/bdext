import logging
import asyncio
from typing import List, Tuple

from prompt_optimizer.models import TaskBundle, ModelConfig, EvalResult, TestCase
from prompt_optimizer.config import AppConfig
from prompt_optimizer.target_runner import TargetRunner
from prompt_optimizer.judge import JudgeCommittee
from prompt_optimizer.llm_client import LLMClient
from prompt_optimizer.scoring import mean_overall

class Calibrator:
    def __init__(self, config: AppConfig, target_runner: TargetRunner, judge_committee: JudgeCommittee, client: LLMClient):
        self.config = config
        self.target_runner = target_runner
        self.judge_committee = judge_committee
        self.client = client
        self.logger = logging.getLogger(__name__)

    def _get_golden_cases(self, bundle: TaskBundle) -> List[TestCase]:
        golden_cases = []
        for group in bundle.groups:
            for case in group.test_cases:
                if case.golden_score is not None:
                    golden_cases.append(case)
        return golden_cases

    async def calibrate_judges(self, bundle: TaskBundle, target_model: ModelConfig, system_prompt: str, user_prompts_by_group: dict[str, str]) -> str:
        golden_cases = self._get_golden_cases(bundle)
        if not golden_cases:
            self.logger.info("Keine Golden Cases für Judge-Kalibrierung gefunden. Überspringe Phase 0.a.")
            return ""

        self.logger.info(f"Starte Phase 0.a (Judge Calibration) mit {len(golden_cases)} Golden Cases.")

        async def evaluate_golden(case):
            user_prompt = user_prompts_by_group[case.group_id]
            try:
                output = await self.target_runner.run(
                    model_config=target_model,
                    system_prompt=system_prompt,
                    user_prompt=user_prompt,
                    test_case=case,
                    temperature=0.0
                )
                committee_result = await self.judge_committee.evaluate(
                    target_output=output,
                    test_case=case,
                    temperature=0.0
                )
                return case, output.output, committee_result.mean_scores.overall
            except Exception as e:
                self.logger.error(f"Fehler bei Golden Eval für Case {case.case_id}: {e}")
                return None

        results = await asyncio.gather(*(evaluate_golden(c) for c in golden_cases))

        few_shot_examples = []
        for r in results:
            if r is not None:
                case, model_output, predicted_score = r
                golden_score = case.golden_score
                # Check for significant deviation (e.g. difference > 1.5)
                if abs(predicted_score - golden_score) > 1.5:
                    self.logger.warning(f"Judge Abweichung bei Case {case.case_id}: Golden={golden_score}, Predicted={predicted_score:.2f}")
                    few_shot_examples.append(
                        f"Expected Output: {case.expected_output}\n"
                        f"Model Output: {model_output}\n"
                        f"Korrektes Overall-Rating: {golden_score}"
                    )

        if not few_shot_examples:
            self.logger.info("Judges sind bereits gut kalibriert.")
            return ""

        # Formulate Few-Shot context
        few_shot_str = "\n\n".join(few_shot_examples)
        calibration_guideline = (
            "\n\nWICHTIGE KALIBRIERUNGS-RICHTLINIE:\n"
            "Bei vorherigen Tests haben Sie folgende Ausgaben falsch bewertet. Bitte orientieren Sie sich ab sofort "
            "an diesen Referenzbewertungen (Golden Scores), um Ihre Strenge anzupassen:\n"
            f"{few_shot_str}"
        )
        self.logger.info("Judge Calibration Guideline generiert.")
        return calibration_guideline

    async def calibrate_optimizer(self, bundle: TaskBundle, target_model: ModelConfig, baseline_results: List[EvalResult], optimizer_model: ModelConfig) -> str:
        golden_cases = self._get_golden_cases(bundle)
        if not golden_cases:
            self.logger.info("Keine Golden Cases für Optimizer-Kalibrierung gefunden. Überspringe Phase 0.b.")
            return ""

        self.logger.info("Starte Phase 0.b (Optimizer Calibration).")

        # We find baseline failures among golden cases
        failures = []
        for r in baseline_results:
            case = next((c for c in golden_cases if c.case_id == r.case_id), None)
            if case and case.golden_score is not None:
                # If the score is significantly worse than golden
                if r.committee.mean_scores.overall < case.golden_score - 1.0:
                    failures.append(r)

        if not failures:
            self.logger.info("Keine signifikanten Baseline-Fehler bei Golden Cases. Keine Optimizer-Strategie nötig.")
            return ""

        # Ask the optimizer to build a strategy
        error_context = ""
        for r in failures[:3]: # Send up to 3 errors to avoid huge contexts
            error_context += f"Case ID: {r.case_id}\nOutput: {r.output}\nScore: {r.committee.mean_scores.overall:.2f}\n\n"

        meta_prompt = f"""Du analysierst Fehler des Zielmodells '{target_model.name}'.
Hier sind Ausgaben des Modells, die schlecht bewertet wurden:

{error_context}

Deine Aufgabe:
Schreibe eine kurze 'Optimierungs-Strategie' (Maximal 3 Sätze).
Welche systematischen Fehler macht das Modell und worauf solltest du als Prompt-Optimizer bei diesem speziellen Modell in Zukunft achten?
Gib nur die Strategie als reinen Text zurück."""

        try:
            strategy = await self.client.complete(
                model_config=optimizer_model,
                messages=[{"role": "user", "content": meta_prompt}],
                temperature=0.5
            )
            self.logger.info(f"Optimizer Strategy generiert: {strategy}")

            return f"\n\nSPEZIELLE STRATEGIE FÜR MODELL {target_model.name}:\n{strategy}"
        except Exception as e:
            self.logger.error(f"Fehler bei Optimizer Calibration: {e}")
            return ""
