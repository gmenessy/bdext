import typer
import logging
import sys
from rich.console import Console

from prompt_optimizer.config import AppConfig
from prompt_optimizer.dataset import DatasetLoader
from prompt_optimizer.splitting import split_task_bundle
from prompt_optimizer.cache import PromptCache
from prompt_optimizer.llm_client import OpenAILikeClient, MockLLMClient
from prompt_optimizer.target_runner import TargetRunner
from prompt_optimizer.judge import JudgeCommittee
from prompt_optimizer.optimizer import OptimizerCommittee
from prompt_optimizer.acceptance import AcceptanceLogic
from prompt_optimizer.loop import OptimizationLoop
from prompt_optimizer.reporting import Reporter
from dotenv import load_dotenv

load_dotenv()

app = typer.Typer(help="LLM Prompt Optimization Pipeline MVP")
console = Console()

def setup_logging():
    logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")

@app.command("validate")
def validate_cmd(config: str = typer.Option(..., help="Pfad zur YAML-Konfiguration")):
    setup_logging()
    console.print(f"Lade Konfiguration: {config}")
    try:
        app_config = AppConfig.load_from_yaml(config)
        console.print("[green]Konfiguration erfolgreich geladen.[/green]")

        loader = DatasetLoader(app_config.dataset.path)
        bundle = loader.load()
        console.print(f"[green]Datensatz erfolgreich geladen. {len(bundle.groups)} Gruppen gefunden.[/green]")

        train, test = split_task_bundle(bundle, app_config.dataset.train_test_split, app_config.run.random_seed)
        console.print(f"[green]Train/Test-Split erfolgreich erstellt.[/green]")

    except Exception as e:
        console.print(f"[red]Fehler bei der Validierung: {e}[/red]")
        sys.exit(1)


import asyncio

@app.command("run")
def run_cmd(
    config: str = typer.Option(..., help="Pfad zur YAML-Konfiguration"),
    mock: bool = typer.Option(False, help="Verwende MockLLMClient für lokale Tests")
):
    setup_logging()
    app_config = AppConfig.load_from_yaml(config)

    loader = DatasetLoader(app_config.dataset.path)
    bundle = loader.load()
    train_bundle, test_bundle = split_task_bundle(bundle, app_config.dataset.train_test_split, app_config.run.random_seed)

    cache = PromptCache(app_config.cache)

    if mock:
        client = MockLLMClient()
    else:
        client = OpenAILikeClient(app_config.api)

    target_runner = TargetRunner(client, cache)
    judge_committee = JudgeCommittee(client, app_config.judge_models, cache, app_config.optimization.disagreement_std_threshold)
    optimizer_committee = OptimizerCommittee(client, app_config.optimizer_models)
    acceptance_logic = AcceptanceLogic(app_config.optimization)

    from prompt_optimizer.calibration import Calibrator
    calibrator = Calibrator(app_config, target_runner, judge_committee, client)

    loop = OptimizationLoop(
        config=app_config,
        target_runner=target_runner,
        judge_committee=judge_committee,
        optimizer_committee=optimizer_committee,
        acceptance_logic=acceptance_logic,
        calibrator=calibrator
    )

    async def async_run():
        await loop.init()
        all_results = []
        for target_model in app_config.target_models:
            console.print(f"\n[bold blue]Starte Optimierung für Modell: {target_model.name}[/bold blue]")
            result = await loop.run_for_model(target_model, train_bundle, test_bundle)
            all_results.append(result)
        return all_results

    try:
        all_results = asyncio.run(async_run())

        reporter = Reporter(app_config)
        reporter.write_artifacts(all_results)
        console.print(f"\n[bold green]Lauf abgeschlossen. Reports in {app_config.run.output_dir} gespeichert.[/bold green]")

    finally:
        cache.close()

@app.command("tournament")
def tournament_cmd(
    config: str = typer.Option(..., help="Pfad zur YAML-Konfiguration"),
    mock: bool = typer.Option(False, help="Verwende MockLLMClient für lokale Tests")
):
    setup_logging()
    app_config = AppConfig.load_from_yaml(config)

    loader = DatasetLoader(app_config.dataset.path)
    bundle = loader.load()
    train_bundle, test_bundle = split_task_bundle(bundle, app_config.dataset.train_test_split, app_config.run.random_seed)

    cache = PromptCache(app_config.cache)

    if mock:
        client = MockLLMClient()
    else:
        client = OpenAILikeClient(app_config.api)

    target_runner = TargetRunner(client, cache)
    judge_committee = JudgeCommittee(client, app_config.judge_models, cache, app_config.optimization.disagreement_std_threshold)
    optimizer_committee = OptimizerCommittee(client, app_config.optimizer_models)
    acceptance_logic = AcceptanceLogic(app_config.optimization)

    from prompt_optimizer.calibration import Calibrator
    calibrator = Calibrator(app_config, target_runner, judge_committee, client)

    from prompt_optimizer.tournament import TournamentOrchestrator
    tournament_orchestrator = TournamentOrchestrator(app_config, target_runner, judge_committee)

    loop = OptimizationLoop(
        config=app_config,
        target_runner=target_runner,
        judge_committee=judge_committee,
        optimizer_committee=optimizer_committee,
        acceptance_logic=acceptance_logic,
        calibrator=calibrator
    )

    async def async_run():
        await loop.init()
        all_results = []
        final_states = {}
        for target_model in app_config.target_models:
            console.print(f"\n[bold blue]Starte Optimierung für Modell: {target_model.name}[/bold blue]")
            result = await loop.run_for_model(target_model, train_bundle, test_bundle)
            all_results.append(result)

            # Reconstruct PromptState from result dict
            from prompt_optimizer.prompt_state import PromptState
            final_states[target_model.name] = PromptState(**result["final_state"])

        console.print(f"\n[bold magenta]MÖGE DAS TURNIER BEGINNEN![/bold magenta]")
        champion = await tournament_orchestrator.run_grand_finale(test_bundle, final_states)

        console.print(f"\n[bold green]⭐⭐⭐ DER GRAND CHAMPION IST: {champion} ⭐⭐⭐[/bold green]")
        return all_results

    try:
        all_results = asyncio.run(async_run())

        reporter = Reporter(app_config)
        reporter.write_artifacts(all_results)
        console.print(f"\n[bold green]Tournament abgeschlossen. Reports in {app_config.run.output_dir} gespeichert.[/bold green]")

    finally:
        cache.close()

@app.command("evaluate")
def evaluate_cmd(
    config: str = typer.Option(..., help="Pfad zur YAML-Konfiguration"),
    prompts: str = typer.Option(..., help="Pfad zur final_prompts.json")
):
    setup_logging()
    console.print("[yellow]Die Evaluate-Funktion wird im MVP als Platzhalter bereitgestellt.[/yellow]")

if __name__ == "__main__":
    app()
