import json
import logging
from typing import List
import statistics
import asyncio

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
{{
  "overall": 1,
  "content": 1,
  "style": 1,
  "structure": 1,
  "rationale": "..."
}}"""

PAIRWISE_JUDGE_PROMPT = """Du bist ein strenger Evaluator für LLM-Ausgaben.

Vergleiche zwei Ausgaben (A und B) basierend auf der erwarteten Ausgabe.
Bewerte BEIDE Ausgaben absolut (1 bis 10) in verschiedenen Dimensionen.
Gib ausschließlich valides JSON zurück.

Erwartete Ausgabe:
{expected_output}

Ausgabe A (Baseline):
{model_output_a}

Ausgabe B (Kandidat):
{model_output_b}

JSON-Schema:
{{
  "scores_a": {{
    "overall": 1,
    "content": 1,
    "style": 1,
    "structure": 1
  }},
  "scores_b": {{
    "overall": 1,
    "content": 1,
    "style": 1,
    "structure": 1
  }},
  "rationale": "Kurze Begründung, warum A oder B besser ist."
}}"""


class JudgeCommittee:
    def __init__(self, client: LLMClient, models: List[ModelConfig], cache: PromptCache, disagreement_std_threshold: float = 1.5):
        self.client = client
        self.models = models
        self.cache = cache
        self.disagreement_std_threshold = disagreement_std_threshold
        self.logger = logging.getLogger(__name__)

    def _parse_json_output(self, raw_output: str) -> dict:
        try:
            return json.loads(raw_output)
        except json.JSONDecodeError:
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
            raise ValueError("Ungültiges JSON vom Judge-Modell.")

    async def evaluate(self, target_output: TargetOutput, test_case: TestCase, temperature: float = 0.0) -> CommitteeResult:
        user_prompt = JUDGE_PROMPT.format(expected_output=test_case.expected_output, model_output=target_output.output)

        async def eval_model(model_config):
            cache_kwargs = {}
            raw_output = None

            if temperature == 0.0:
                cache_kwargs = dict(
                    tool_version="v1.1",
                    role="judge_single",
                    model=model_config.model,
                    expected_output=test_case.expected_output,
                    model_output=target_output.output,
                    temperature=temperature
                )
                raw_output = self.cache.get(**cache_kwargs)

            if raw_output is None:
                try:
                    raw_output = await self.client.complete(
                        model_config=model_config,
                        messages=[{"role": "user", "content": user_prompt}],
                        temperature=temperature
                    )
                    if temperature == 0.0:
                        self.cache.set(raw_output, **cache_kwargs)
                except Exception as e:
                    self.logger.error(f"Fehler bei Judge {model_config.name}: {e}")
                    return None

            try:
                parsed = self._parse_json_output(raw_output)
                score_set = ScoreSet(
                    overall=float(parsed.get("overall", 1.0)),
                    content=float(parsed.get("content", 1.0)),
                    style=float(parsed.get("style", 1.0)),
                    structure=float(parsed.get("structure", 1.0))
                )
                return JudgeScore(
                    judge_name=model_config.name,
                    scores=score_set,
                    rationale=str(parsed.get("rationale", ""))
                )
            except Exception as e:
                self.logger.error(f"Fehler beim Parsen der Judge-Ausgabe {model_config.name}: {e}")
                return None

        results = await asyncio.gather(*(eval_model(m) for m in self.models))
        judge_scores = [r for r in results if r is not None]

        if not judge_scores:
            raise ValueError("Alle Judges sind fehlgeschlagen oder haben ungültiges JSON geliefert.")

        return self._aggregate(judge_scores)

    async def evaluate_pairwise(self, target_output_a: TargetOutput, target_output_b: TargetOutput, test_case: TestCase, temperature: float = 0.0) -> tuple[CommitteeResult, CommitteeResult]:
        """
        Gibt (ResultA, ResultB) zurück.
        """
        user_prompt = PAIRWISE_JUDGE_PROMPT.format(
            expected_output=test_case.expected_output,
            model_output_a=target_output_a.output,
            model_output_b=target_output_b.output
        )

        async def eval_model(model_config):
            cache_kwargs = {}
            raw_output = None

            if temperature == 0.0:
                cache_kwargs = dict(
                    tool_version="v1.1",
                    role="judge_pairwise",
                    model=model_config.model,
                    expected_output=test_case.expected_output,
                    model_output_a=target_output_a.output,
                    model_output_b=target_output_b.output,
                    temperature=temperature
                )
                raw_output = self.cache.get(**cache_kwargs)

            if raw_output is None:
                try:
                    raw_output = await self.client.complete(
                        model_config=model_config,
                        messages=[{"role": "user", "content": user_prompt}],
                        temperature=temperature
                    )
                    if temperature == 0.0:
                        self.cache.set(raw_output, **cache_kwargs)
                except Exception as e:
                    self.logger.error(f"Fehler bei Pairwise Judge {model_config.name}: {e}")
                    return None

            try:
                parsed = self._parse_json_output(raw_output)

                s_a = parsed.get("scores_a", {})
                s_b = parsed.get("scores_b", {})

                score_set_a = ScoreSet(
                    overall=float(s_a.get("overall", 1.0)),
                    content=float(s_a.get("content", 1.0)),
                    style=float(s_a.get("style", 1.0)),
                    structure=float(s_a.get("structure", 1.0))
                )

                score_set_b = ScoreSet(
                    overall=float(s_b.get("overall", 1.0)),
                    content=float(s_b.get("content", 1.0)),
                    style=float(s_b.get("style", 1.0)),
                    structure=float(s_b.get("structure", 1.0))
                )

                rationale = str(parsed.get("rationale", ""))

                js_a = JudgeScore(judge_name=model_config.name, scores=score_set_a, rationale=rationale)
                js_b = JudgeScore(judge_name=model_config.name, scores=score_set_b, rationale=rationale)

                return (js_a, js_b)

            except Exception as e:
                self.logger.error(f"Fehler beim Parsen der Pairwise Judge-Ausgabe {model_config.name}: {e}")
                return None

        results = await asyncio.gather(*(eval_model(m) for m in self.models))
        valid_results = [r for r in results if r is not None]

        if not valid_results:
            raise ValueError("Alle Pairwise Judges sind fehlgeschlagen.")

        js_a_list = [r[0] for r in valid_results]
        js_b_list = [r[1] for r in valid_results]

        return self._aggregate(js_a_list), self._aggregate(js_b_list)


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
