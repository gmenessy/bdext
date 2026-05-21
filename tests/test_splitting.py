import pytest

from prompt_optimizer.models import TaskBundle, PromptGroup, TestCase
from prompt_optimizer.splitting import split_task_bundle


@pytest.fixture
def sample_bundle():
    cases_g1 = [
        TestCase(case_id=f"c1_{i}", group_id="g1", input=f"in1_{i}", expected_output=f"out1_{i}")
        for i in range(10)
    ]
    cases_g2 = [
        TestCase(case_id=f"c2_{i}", group_id="g2", input=f"in2_{i}", expected_output=f"out2_{i}")
        for i in range(5)
    ]

    return TaskBundle(
        system_prompt="Sys",
        groups=[
            PromptGroup(group_id="g1", user_prompt="User1", test_cases=cases_g1),
            PromptGroup(group_id="g2", user_prompt="User2", test_cases=cases_g2),
        ]
    )

def test_split_sizes(sample_bundle):
    train_bundle, test_bundle = split_task_bundle(sample_bundle, train_ratio=0.7, seed=42)

    train_g1 = next(g for g in train_bundle.groups if g.group_id == "g1")
    test_g1 = next(g for g in test_bundle.groups if g.group_id == "g1")

    assert len(train_g1.test_cases) == 7
    assert len(test_g1.test_cases) == 3

    train_g2 = next(g for g in train_bundle.groups if g.group_id == "g2")
    test_g2 = next(g for g in test_bundle.groups if g.group_id == "g2")

    assert len(train_g2.test_cases) == 3
    assert len(test_g2.test_cases) == 2

def test_reproducibility(sample_bundle):
    train1, test1 = split_task_bundle(sample_bundle, 0.7, 42)
    train2, test2 = split_task_bundle(sample_bundle, 0.7, 42)

    train1_c1_ids = [c.case_id for c in train1.groups[0].test_cases]
    train2_c1_ids = [c.case_id for c in train2.groups[0].test_cases]

    assert train1_c1_ids == train2_c1_ids

def test_different_seeds_different_splits(sample_bundle):
    train1, _ = split_task_bundle(sample_bundle, 0.7, 42)
    train2, _ = split_task_bundle(sample_bundle, 0.7, 99)

    train1_c1_ids = [c.case_id for c in train1.groups[0].test_cases]
    train2_c1_ids = [c.case_id for c in train2.groups[0].test_cases]

    assert train1_c1_ids != train2_c1_ids

def test_no_overlap(sample_bundle):
    train, test = split_task_bundle(sample_bundle, 0.7, 42)

    train_g1_ids = set(c.case_id for c in train.groups[0].test_cases)
    test_g1_ids = set(c.case_id for c in test.groups[0].test_cases)

    assert len(train_g1_ids.intersection(test_g1_ids)) == 0

def test_small_group_at_least_one_test_case():
    cases = [
        TestCase(case_id="c1", group_id="g1", input="i1", expected_output="o1"),
        TestCase(case_id="c2", group_id="g1", input="i2", expected_output="o2"),
    ]
    bundle = TaskBundle(
        system_prompt="Sys",
        groups=[PromptGroup(group_id="g1", user_prompt="U", test_cases=cases)]
    )

    # 0.9 would normally put both in train, but we force at least 1 test case
    train, test = split_task_bundle(bundle, 0.9, 42)
    assert len(train.groups[0].test_cases) == 1
    assert len(test.groups[0].test_cases) == 1
