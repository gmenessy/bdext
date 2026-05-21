import logging
import asyncio
from typing import List, Dict

from prompt_optimizer.models import TaskBundle, ModelConfig
from prompt_optimizer.prompt_state import PromptState
from prompt_optimizer.target_runner import TargetRunner
from prompt_optimizer.judge import JudgeCommittee
from prompt_optimizer.config import AppConfig

class TournamentOrchestrator:
    def __init__(self, config: AppConfig, target_runner: TargetRunner, judge_committee: JudgeCommittee):
        self.config = config
        self.target_runner = target_runner
        self.judge_committee = judge_committee
        self.logger = logging.getLogger(__name__)

    async def run_grand_finale(
        self,
        test_bundle: TaskBundle,
        final_states: Dict[str, PromptState]
    ) -> str:
        """
        Runs a pairwise tournament on the test bundle between all optimized models.
        Returns the name of the absolute winning model.
        """
        model_names = list(final_states.keys())
        if len(model_names) < 2:
            self.logger.warning("Zu wenige Modelle für ein Tournament. Benötige mindestens 2.")
            return model_names[0] if model_names else ""

        self.logger.info(f"Starte Grand Finale Tournament mit {len(model_names)} Modellen.")

        # Simple Round-Robin
        scores = {name: 0 for name in model_names}

        for i in range(len(model_names)):
            for j in range(i + 1, len(model_names)):
                model_a_name = model_names[i]
                model_b_name = model_names[j]

                model_a_config = next(m for m in self.config.target_models if m.name == model_a_name)
                model_b_config = next(m for m in self.config.target_models if m.name == model_b_name)

                state_a = final_states[model_a_name]
                state_b = final_states[model_b_name]

                wins_a, wins_b = await self._run_pairwise_battle(
                    model_a_config, state_a,
                    model_b_config, state_b,
                    test_bundle
                )

                if wins_a > wins_b:
                    scores[model_a_name] += 3
                elif wins_b > wins_a:
                    scores[model_b_name] += 3
                else:
                    scores[model_a_name] += 1
                    scores[model_b_name] += 1

        self.logger.info(f"Tournament Finale Ergebnisse: {scores}")

        # Sort by points
        winner = max(scores, key=scores.get)
        self.logger.info(f"GRAND CHAMPION: {winner} mit {scores[winner]} Punkten!")

        return winner

    async def _run_pairwise_battle(self, config_a: ModelConfig, state_a: PromptState, config_b: ModelConfig, state_b: PromptState, bundle: TaskBundle) -> tuple[int, int]:
        self.logger.info(f"Battle: {config_a.name} VS {config_b.name}")
        wins_a = 0
        wins_b = 0

        # Run on a sample to save money (e.g. max 10 cases from test set)
        cases_to_test = []
        for group in bundle.groups:
            cases_to_test.extend(group.test_cases)

        cases_to_test = cases_to_test[:10]

        for case in cases_to_test:
            try:
                # Resolve group prompts
                user_prompt_a = state_a.user_prompts_by_group.get(case.group_id, "")
                user_prompt_b = state_b.user_prompts_by_group.get(case.group_id, "")

                # Fetch Outputs
                out_a = await self.target_runner.run(config_a, state_a.system_prompt, user_prompt_a, case)
                out_b = await self.target_runner.run(config_b, state_b.system_prompt, user_prompt_b, case)

                # Pairwise Judge
                res_a, res_b = await self.judge_committee.evaluate_pairwise(out_a, out_b, case)

                score_a = res_a.mean_scores.overall
                score_b = res_b.mean_scores.overall

                if score_a > score_b:
                    wins_a += 1
                elif score_b > score_a:
                    wins_b += 1
            except Exception as e:
                self.logger.error(f"Fehler in Battle {config_a.name} vs {config_b.name}: {e}")

        return wins_a, wins_b
