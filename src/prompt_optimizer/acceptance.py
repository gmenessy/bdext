from prompt_optimizer.models import CandidateEvaluation, PromptCandidate
from prompt_optimizer.config import OptimizationConfig

class AcceptanceLogic:
    def __init__(self, config: OptimizationConfig):
        self.config = config

    def evaluate_candidate(
        self,
        candidate: PromptCandidate,
        baseline_mean: float,
        baseline_groups: dict[str, float],
        candidate_mean: float,
        candidate_groups: dict[str, float]
    ) -> CandidateEvaluation:

        delta = candidate_mean - baseline_mean

        group_deltas = {}
        for group_id, score in candidate_groups.items():
            base_score = baseline_groups.get(group_id, score)
            group_deltas[group_id] = score - base_score

        accepted = True
        rejection_reason = None

        if delta < self.config.min_delta:
            accepted = False
            rejection_reason = f"Delta ({delta:.3f}) kleiner als min_delta ({self.config.min_delta})."
        else:
            for group_id, g_delta in group_deltas.items():
                if g_delta < -self.config.max_group_regression:
                    accepted = False
                    rejection_reason = f"Regression in Gruppe {group_id} ({g_delta:.3f}) überschreitet max_group_regression ({self.config.max_group_regression})."
                    break

        return CandidateEvaluation(
            candidate=candidate,
            mean_score_before=baseline_mean,
            mean_score_after=candidate_mean,
            delta=delta,
            group_deltas=group_deltas,
            accepted=accepted,
            rejection_reason=rejection_reason
        )
