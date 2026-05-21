import os
import yaml
from pydantic import BaseModel, Field

from prompt_optimizer.models import ModelConfig


class RunConfig(BaseModel):
    name: str
    random_seed: int
    output_dir: str
    max_iterations: int
    patience: int


class DatasetConfig(BaseModel):
    path: str
    train_test_split: float


class OptimizationConfig(BaseModel):
    objective: str
    min_delta: float
    max_group_regression: float
    disagreement_std_threshold: float


class TemperaturesConfig(BaseModel):
    target: float
    judge: float
    optimizer: float


class ApiConfig(BaseModel):
    timeout_seconds: int
    retry_attempts: int
    retry_initial_seconds: int
    retry_max_seconds: int


class CacheConfig(BaseModel):
    enabled: bool
    path: str


class AppConfig(BaseModel):
    run: RunConfig
    dataset: DatasetConfig
    optimization: OptimizationConfig
    temperatures: TemperaturesConfig
    api: ApiConfig
    cache: CacheConfig
    target_models: list[ModelConfig]
    judge_models: list[ModelConfig]
    optimizer_models: list[ModelConfig]

    @classmethod
    def load_from_yaml(cls, path: str) -> "AppConfig":
        with open(path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)

        def expand_env_vars(d: dict | list | str | float | int | bool | None) -> dict | list | str | float | int | bool | None:
            if isinstance(d, dict):
                return {k: expand_env_vars(v) for k, v in d.items()}
            elif isinstance(d, list):
                return [expand_env_vars(i) for i in d]
            elif isinstance(d, str):
                return os.path.expandvars(d)
            return d

        expanded_data = expand_env_vars(data)
        return cls(**expanded_data)  # type: ignore
