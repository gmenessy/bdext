# Tutorial: LLM Prompt Optimization Pipeline MVP

Willkommen beim Tutorial für die LLM Prompt Optimization Pipeline! Dieses System nutzt fortschrittliche Methoden wie **LLM-as-a-Judge**, ein **Optimizer-Komitee**, **Chain-of-Thought (CoT) Injection**, **In-Context Routing** und einen **Tournament-Modus**, um deine Prompts für kleine und große Modelle zu perfektionieren.

Dieses Tutorial führt dich in 5 einfachen Schritten vom Setup bis zum finalen Grand Champion-Prompt.

---

## Schritt 1: Installation und Setup

1. **Repository klonen** und in den Ordner wechseln.
2. **Abhängigkeiten installieren** (wir nutzen `pip` im Developer-Modus):
   ```bash
   pip install -e .[dev]
   ```
3. **Umgebungsvariablen konfigurieren**:
   Kopiere die `.env.example` zu `.env`:
   ```bash
   cp .env.example .env
   ```
   Öffne die `.env`-Datei und trage die API-Schlüssel für deine Modelle ein (z. B. OpenAI, LiteLLM, vLLM oder Ollama).

---

## Schritt 2: Den Datensatz vorbereiten (CSV)

Die Pipeline benötigt Freitext-Aufgaben, um zu lernen. Erstelle eine `.csv`-Datei (z. B. `data/sample.csv`) mit folgendem Format:

| system_prompt | prompt | input | expected_output | group_id | case_id | golden_score |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| Du bist ein Assistent. | Übersetze: {input} | Hallo | Hello | translation | case_1 | 10.0 |
| Du bist ein Assistent. | Rechne: {input} | 5+5 | 10 | math | case_2 | 10.0 |

* **Pflichtfelder**: `system_prompt`, `prompt`, `input`, `expected_output`
* **Wichtig**: Der Text in `prompt` **muss** den Platzhalter `{input}` enthalten.
* **`golden_score` (Optional)**: Wenn du einen Wert von 1-10 angibst, kalibriert sich das Judge-Komitee vor dem Lauf selbst auf diesen Score!

---

## Schritt 3: Die Konfiguration (YAML) anpassen

Öffne `configs/example.yaml`. Hier kannst du die Magie der Pipeline steuern:

```yaml
run:
  name: "mein_erster_testlauf"
  max_iterations: 10
  patience: 2
  mode: "hard" # "fast" = schnellster Weg, "hard" = Nutzt Fallback-Queues (Beam Search)
  db_path: "reports/history.db" # Hier speichert das WIKI seine Anti-Patterns

optimization:
  min_delta: 0.05
  early_exit_chunk_size: 5
  calibrate_judges: true
  calibrate_optimizers: true

api:
  concurrency_limit: 10 # Verhindert HTTP 429 Rate Limits bei deinem Provider
```

Unter `target_models`, `judge_models` und `optimizer_models` kannst du definieren, welche Modelle welche Aufgabe übernehmen. (Tipp: Nimm ein starkes Modell wie GPT-4 oder Claude-3.5 für die Judges/Optimizer und kleine Modelle für die Targets).

---

## Schritt 4: Die Pipeline starten

Sobald Daten und Konfiguration stehen, kannst du den Lauf starten:

```bash
prompt-optimizer run --config configs/example.yaml
```

**Was passiert jetzt unter der Haube?**
1. **Calibration (Phase 0)**: Das System prüft die Judges gegen deine `golden_scores` und lässt den Optimizer eine Strategie für das Zielmodell generieren.
2. **Iteration (Phase A & B)**: System- und User-Prompts werden optimiert.
3. **In-Context Routing & CoT**: Bei komplexen Aufgaben injiziert der Optimizer `<scratchpad>`-Logiken oder generiert spezialisierte Profile (z.B. analytisch vs. kreativ).
4. **Early Exit**: Ist ein Kandidaten-Prompt völlig unbrauchbar, bricht die Evaluierung nach den ersten 5 Testfällen sofort ab (spart API-Kosten).
5. **WIKI-Speicherung**: Erfolgreiche Prompts und gescheiterte "Sackgassen" werden in der SQLite-Datenbank (`history.db`) gespeichert und beim nächsten Versuch als Kontext mitgegeben.

---

## Schritt 5: Das Tournament (Grand Finale) 🏆

Willst du das absolute Maximum herausholen und hast mehrere `target_models` konfiguriert? Nutze den Tournament-Befehl:

```bash
prompt-optimizer tournament --config configs/example.yaml
```

Dies führt die Optimierung aus und startet danach ein **Grand Finale**.
Hier treten die jeweils besten fertig optimierten Modelle (inkl. *Mixture of Prompts* / Ensembling) auf dem zurückgehaltenen Test-Datensatz im **Pairwise-Battle** (Jeder gegen Jeden) an.
Das Modell mit den meisten Siegen wird zum **Grand Champion** gekrönt!

---

## Resultate ansehen

Alle Ergebnisse findest du im Ordner `reports/`:
* **`.md` Report**: Ein schöner Markdown-Bericht über alle Phasen, Scores und Begründungen.
* **`final_prompts.json`**: Die fertig optimierten Prompts (inklusive spezialisierter Routen).
* **`.jsonl` Dateien**: Rohdaten für detaillierte Auswertungen (Deltas, Rationale, Guardrail-Verletzungen).

Viel Spaß beim Optimieren!
