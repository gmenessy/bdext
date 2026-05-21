from enum import Enum
from pydantic import BaseModel, Field


class Phase(str, Enum):
    SYSTEM = "system"
    USER = "user"


class ScoreSet(BaseModel):
    overall: float = Field(ge=1, le=10)
    content: float = Field(ge=1, le=10)
    style: float = Field(ge=1, le=10)
    structure: float = Field(ge=1, le=10)


class TestCase(BaseModel):
    case_id: str
    group_id: str
    input: str
    expected_output: str


class PromptGroup(BaseModel):
    group_id: str
    user_prompt: str
    test_cases: list[TestCase]


class TaskBundle(BaseModel):
    system_prompt: str
    groups: list[PromptGroup]


class ModelConfig(BaseModel):
    name: str
    base_url: str
    api_key: str
    model: str


class TargetOutput(BaseModel):
    model_name: str
    case_id: str
    output: str


class JudgeScore(BaseModel):
    judge_name: str
    scores: ScoreSet
    rationale: str


class CommitteeResult(BaseModel):
    mean_scores: ScoreSet
    std_scores: ScoreSet
    disagreement: bool
    judge_scores: list[JudgeScore]


class EvalResult(BaseModel):
    target_model_name: str
    group_id: str
    case_id: str
    output: str
    committee: CommitteeResult


class PromptCandidate(BaseModel):
    candidate_id: str
    phase: Phase
    optimizer_name: str
    prompt_text: str
    rationale: str
    parent_id: str | None = None


class CandidateEvaluation(BaseModel):
    candidate: PromptCandidate
    mean_score_before: float
    mean_score_after: float
    delta: float
    group_deltas: dict[str, float]
    accepted: bool
    rejection_reason: str | None = None


class OptimizationStep(BaseModel):
    iteration: int
    phase: Phase
    target_model_name: str
    group_id: str | None = None
    candidates: list[CandidateEvaluation]
    accepted_candidate_id: str | None = None
