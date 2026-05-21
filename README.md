# Prompt Optimizer

Ein MVP für eine LLM-Prompt-Optimierungspipeline mit Auto-Research, Optimizer-Komitee und LLM-as-a-Judge-Komitee.

## Installation

```bash
pip install -e .[dev]
```

## Nutzung

Konfiguration vorbereiten:
```bash
cp .env.example .env
```
Passe in der `.env` Datei die Keys und URLs zu deinen LLM-Providern an (z.B. Ollama, vLLM, LiteLLM, OpenAI).

Datensatz validieren:
```bash
prompt-optimizer validate --config configs/example.yaml
```

Optimierungslauf starten:
```bash
prompt-optimizer run --config configs/example.yaml
```

Für den ultimativen Kreuz-Vergleich (Tournament) zwischen Modellen:
```bash
prompt-optimizer tournament --config configs/example.yaml
```

## Dokumentation & Tutorial
Ein vollständiges, detailliertes Tutorial zur Nutzung aller erweiterten Funktionen (inklusive Golden Scores, WIKI, CoT-Injection und In-Context Routing) findest du hier:
👉 **[Tutorial lesen](docs/tutorial.md)**

## Übersicht
Die Pipeline verbessert iterativ System- und User-Prompts auf Basis eines bereitgestellten Datensatzes. Ein Optimizer-Modell schlägt Änderungen vor, die von einem Judge-Komitee bewertet werden. Akzeptierte Änderungen werden in einem detaillierten Markdown-Report gespeichert.
