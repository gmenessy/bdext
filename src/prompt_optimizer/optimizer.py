import json
import logging
from typing import List

from prompt_optimizer.models import ModelConfig, Phase, PromptCandidate, EvalResult
from prompt_optimizer.llm_client import LLMClient


OPTIMIZER_PROMPT = """Du optimierst Prompts für ein Zielmodell.

Aufgabe:
Verbessere den folgenden {phase}-Prompt.
Fokussiere dich besonders auf die schwächste Dimension: {weakest_dimension}.

Aktueller Prompt:
{current_prompt}

Fehlerfälle und Scores:
{error_cases}

Regeln:
- Gib genau einen konkreten neuen Prompt zurück.
- Der Prompt muss direkt ausführbar sein.
- Erhalte alle fachlichen Anforderungen.
- Vermeide Überanpassung auf einzelne Beispiele.
- Verschlechtere keine andere Bewertungsdimension.

Gib ausschließlich valides JSON zurück:
{{
  "prompt_text": "...",
  "rationale": "..."
}}"""


class OptimizerCommittee:
    def __init__(self, client: LLMClient, models: List[ModelConfig]):
        self.client = client
        self.models = models
        self.logger = logging.getLogger(__name__)

    def _parse_output(self, raw_output: str) -> dict:
        try:
            return json.loads(raw_output)
        except json.JSONDecodeError:
            # Simple repair attempt: find json block
            if "```json" in raw_output:
                block = raw_output.split("```json")[1].split("```")[0].strip()
                try:
                    return json.loads(block)
                except json.JSONDecodeError:
                    pass
            elif "```" in raw_output:
                block = raw_output.split("```")[1].split("```")[0].strip()
                try:
                    return json.loads(block)
                except json.JSONDecodeError:
                    pass

            # If still fails, throw error
            raise ValueError("Ungültiges JSON vom Optimizer-Modell.")

    def _format_error_cases(self, eval_results: List[EvalResult], max_cases: int = 5) -> str:
        # Sort by worst overall score
        sorted_results = sorted(eval_results, key=lambda r: r.committee.mean_scores.overall)
        worst_cases = sorted_results[:max_cases]

        formatted = []
        for r in worst_cases:
            formatted.append(
                f"Case ID: {r.case_id}\n"
                f"Output: {r.output}\n"
                f"Score: {r.committee.mean_scores.overall:.2f}\n"
                f"Disagreement: {r.committee.disagreement}"
            )
        return "\n\n".join(formatted)

    def generate_candidates(
        self,
        phase: Phase,
        current_prompt: str,
        weakest_dimension: str,
        eval_results: List[EvalResult],
        temperature: float = 0.5
    ) -> List[PromptCandidate]:

        error_cases_str = self._format_error_cases(eval_results)

        user_prompt = OPTIMIZER_PROMPT.format(
            phase=phase.value,
            weakest_dimension=weakest_dimension,
            current_prompt=current_prompt,
            error_cases=error_cases_str
        )

        candidates = []

        for model_config in self.models:
            try:
                raw_output = self.client.complete(
                    model_config=model_config,
                    messages=[{"role": "user", "content": user_prompt}],
                    temperature=temperature
                )

                parsed = self._parse_output(raw_output)

                candidates.append(PromptCandidate(
                    candidate_id=f"{model_config.name}_{phase.value}_{hash(raw_output)}",
                    phase=phase,
                    optimizer_name=model_config.name,
                    prompt_text=parsed["prompt_text"],
                    rationale=parsed["rationale"]
                ))
            except Exception as e:
                self.logger.error(f"Fehler bei Optimizer {model_config.name}: {e}")

        return candidates
