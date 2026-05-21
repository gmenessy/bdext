import random
from typing import Tuple

from prompt_optimizer.models import TaskBundle, PromptGroup


def split_task_bundle(bundle: TaskBundle, train_ratio: float, seed: int) -> Tuple[TaskBundle, TaskBundle]:
    random.seed(seed)

    train_groups = []
    test_groups = []

    for group in bundle.groups:
        cases = group.test_cases.copy()

        # Determine sizes
        n_total = len(cases)
        if n_total == 0:
            continue

        n_train = int(n_total * train_ratio)
        if n_train == n_total and n_total > 1:
            n_train = n_total - 1 # force at least 1 test case if possible
        elif n_train == 0 and n_total > 1:
            n_train = 1 # force at least 1 train case if possible

        # Shuffle deterministically
        cases_sorted = sorted(cases, key=lambda c: c.case_id) # ensure stable initial order
        random.shuffle(cases_sorted)

        train_cases = cases_sorted[:n_train]
        test_cases = cases_sorted[n_train:]

        if train_cases:
            train_groups.append(PromptGroup(
                group_id=group.group_id,
                user_prompt=group.user_prompt,
                test_cases=train_cases
            ))

        if test_cases:
            test_groups.append(PromptGroup(
                group_id=group.group_id,
                user_prompt=group.user_prompt,
                test_cases=test_cases
            ))

    train_bundle = TaskBundle(system_prompt=bundle.system_prompt, groups=train_groups)
    test_bundle = TaskBundle(system_prompt=bundle.system_prompt, groups=test_groups)

    return train_bundle, test_bundle
