import json
import statistics
from typing import List
import logging

from prompt_optimizer.models import ModelConfig, TargetOutput, TestCase, JudgeScore, ScoreSet, CommitteeResult
from prompt_optimizer.llm_client import LLMClient
from prompt_optimizer.cache import PromptCache


JUDGE_PROMPT = """Du bist ein strenger Evaluator für LLM-Ausgaben.

Bewerte die Modellausgabe im Vergleich zur erwarteten Ausgabe.
Gib ausschließlich valides JSON zurück.

Kriterien:
- overall: Gesamtqualität, 1 bis 10
- content: Genauigkeit und Faktentreue, 1 bis 10
- style: sprachlicher Ausdruck und Ton, 1 bis 10
- structure: Logik, Aufbau und Formatierung, 1 bis 10
- rationale: kurze Begründung

Erwartete Ausgabe:
{expected_output}

Modellausgabe:
{model_output}

JSON-Schema:
{
  "overall": 1,
  "content": 1,
  "style": 1,
  "structure": 1,
  "rationale": "..."
}"""


class JudgeCommittee:
    def __init__(self, client: LLMClient, models: List[ModelConfig], cache: PromptCache, disagreement_std_threshold: float = 1.5):
        self.client = client
        self.models = models
        self.cache = cache
        self.disagreement_std_threshold = disagreement_std_threshold
        self.logger = logging.getLogger(__name__)

    def _parse_judge_output(self, raw_output: str) -> dict:
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
            raise ValueError("Ungültiges JSON vom Judge-Modell.")

    def evaluate(self, target_output: TargetOutput, test_case: TestCase, temperature: float = 0.0) -> CommitteeResult:
        user_prompt = JUDGE_PROMPT.replace("{expected_output}", test_case.expected_output).replace("{model_output}", target_output.output)

        judge_scores = []

        for model_config in self.models:
            cache_kwargs = {}
            raw_output = None

            if temperature == 0.0:
                cache_kwargs = dict(
                    tool_version="v1",
                    role="judge",
                    model=model_config.model,
                    expected_output=test_case.expected_output,
                    model_output=target_output.output,
                    temperature=temperature
                )
                raw_output = self.cache.get(**cache_kwargs)

            if raw_output is None:
                try:
                    raw_output = self.client.complete(
                        model_config=model_config,
                        messages=[{"role": "user", "content": user_prompt}],
                        temperature=temperature
                    )
                    if temperature == 0.0:
                        self.cache.set(raw_output, **cache_kwargs)
                except Exception as e:
                    self.logger.error(f"Fehler bei Judge {model_config.name}: {e}")
                    continue

            try:
                parsed = self._parse_judge_output(raw_output)

                # Build score set
                score_set = ScoreSet(
                    overall=float(parsed.get("overall", 1.0)),
                    content=float(parsed.get("content", 1.0)),
                    style=float(parsed.get("style", 1.0)),
                    structure=float(parsed.get("structure", 1.0))
                )

                judge_scores.append(JudgeScore(
                    judge_name=model_config.name,
                    scores=score_set,
                    rationale=str(parsed.get("rationale", ""))
                ))
            except Exception as e:
                self.logger.error(f"Fehler beim Parsen der Judge-Ausgabe {model_config.name}: {e}")
                continue

        if not judge_scores:
            raise ValueError("Alle Judges sind fehlgeschlagen oder haben ungültiges JSON geliefert.")

        return self._aggregate(judge_scores)

    def _aggregate(self, scores: List[JudgeScore]) -> CommitteeResult:
        n = len(scores)

        if n == 1:
            return CommitteeResult(
                mean_scores=scores[0].scores,
                std_scores=ScoreSet(overall=0, content=0, style=0, structure=0),
                disagreement=False,
                judge_scores=scores
            )

        overall_vals = [s.scores.overall for s in scores]
        content_vals = [s.scores.content for s in scores]
        style_vals = [s.scores.style for s in scores]
        structure_vals = [s.scores.structure for s in scores]

        mean_scores = ScoreSet(
            overall=statistics.mean(overall_vals),
            content=statistics.mean(content_vals),
            style=statistics.mean(style_vals),
            structure=statistics.mean(structure_vals)
        )

        std_scores = ScoreSet(
            overall=statistics.stdev(overall_vals),
            content=statistics.stdev(content_vals),
            style=statistics.stdev(style_vals),
            structure=statistics.stdev(structure_vals)
        )

        disagreement = any(std > self.disagreement_std_threshold for std in [
            std_scores.overall, std_scores.content, std_scores.style, std_scores.structure
        ])

        return CommitteeResult(
            mean_scores=mean_scores,
            std_scores=std_scores,
            disagreement=disagreement,
            judge_scores=scores
        )
