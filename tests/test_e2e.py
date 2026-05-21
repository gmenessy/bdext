import pytest
import os
import shutil

from prompt_optimizer.config import AppConfig
from prompt_optimizer.dataset import DatasetLoader
from prompt_optimizer.splitting import split_task_bundle
from prompt_optimizer.cache import PromptCache
from prompt_optimizer.llm_client import MockLLMClient
from prompt_optimizer.target_runner import TargetRunner
from prompt_optimizer.judge import JudgeCommittee
from prompt_optimizer.optimizer import OptimizerCommittee
from prompt_optimizer.acceptance import AcceptanceLogic
from prompt_optimizer.loop import OptimizationLoop
from prompt_optimizer.reporting import Reporter


@pytest.mark.asyncio
async def test_e2e_optimization_loop():
    config_path = "configs/example.yaml"
    app_config = AppConfig.load_from_yaml(config_path)

    # Overwrite max_iterations for test
    app_config.run.max_iterations = 2
    app_config.run.patience = 1
    # We want absolute mock paths just in case
    app_config.run.output_dir = "tests/test_reports"
    app_config.run.db_path = "tests/test_reports/history.db"
    os.makedirs(app_config.run.output_dir, exist_ok=True)

    loader = DatasetLoader(app_config.dataset.path)
    bundle = loader.load()
    train_bundle, test_bundle = split_task_bundle(bundle, app_config.dataset.train_test_split, app_config.run.random_seed)

    # Mock specific things
    cache = PromptCache(app_config.cache)
    client = MockLLMClient()

    target_runner = TargetRunner(client, cache)
    judge_committee = JudgeCommittee(client, app_config.judge_models, cache, app_config.optimization.disagreement_std_threshold)
    optimizer_committee = OptimizerCommittee(client, app_config.optimizer_models)
    acceptance_logic = AcceptanceLogic(app_config.optimization)

    loop = OptimizationLoop(
        config=app_config,
        target_runner=target_runner,
        judge_committee=judge_committee,
        optimizer_committee=optimizer_committee,
        acceptance_logic=acceptance_logic
    )

    await loop.init()

    all_results = []
    try:
        # Run just for the first model to save time
        target_model = app_config.target_models[0]
        result = await loop.run_for_model(target_model, train_bundle, test_bundle)
        all_results.append(result)

        reporter = Reporter(app_config)
        reporter.write_artifacts(all_results)

        # Verify
        assert len(all_results) == 1
        assert "baseline_train_results" in result
        assert "optimization_steps" in result

        # We expect some steps if mock generated an accepted candidate
        assert len(result["optimization_steps"]) > 0

        # Check output directory files
        files = os.listdir(app_config.run.output_dir)
        md_files = [f for f in files if f.endswith(".md")]
        json_files = [f for f in files if f.endswith(".json")]
        jsonl_files = [f for f in files if f.endswith(".jsonl")]
        db_files = [f for f in files if f.endswith(".db")]

        assert len(md_files) > 0
        assert len(json_files) > 0
        assert len(jsonl_files) > 0
        assert len(db_files) > 0

    finally:
        cache.close()
        shutil.rmtree(app_config.run.output_dir, ignore_errors=True)
        shutil.rmtree(app_config.cache.path, ignore_errors=True)
