from typing import List, Dict

from prompt_optimizer.models import EvalResult

def mean_overall(results: List[EvalResult]) -> float:
    if not results:
        return 0.0
    return sum(r.committee.mean_scores.overall for r in results) / len(results)


def mean_by_group(results: List[EvalResult]) -> Dict[str, float]:
    group_scores = {}
    group_counts = {}

    for r in results:
        g = r.group_id
        if g not in group_scores:
            group_scores[g] = 0.0
            group_counts[g] = 0

        group_scores[g] += r.committee.mean_scores.overall
        group_counts[g] += 1

    return {g: group_scores[g] / group_counts[g] for g in group_scores}


def dimension_profile(results: List[EvalResult]) -> Dict[str, float]:
    if not results:
        return {"overall": 0.0, "content": 0.0, "style": 0.0, "structure": 0.0}

    n = len(results)
    return {
        "overall": sum(r.committee.mean_scores.overall for r in results) / n,
        "content": sum(r.committee.mean_scores.content for r in results) / n,
        "style": sum(r.committee.mean_scores.style for r in results) / n,
        "structure": sum(r.committee.mean_scores.structure for r in results) / n,
    }


def weakest_dimension(results: List[EvalResult]) -> str:
    profile = dimension_profile(results)
    # Ignore overall, find min of specific dimensions
    dims = {"content": profile["content"], "style": profile["style"], "structure": profile["structure"]}
    return min(dims, key=dims.get)
