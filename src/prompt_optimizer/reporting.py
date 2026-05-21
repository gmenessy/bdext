import os
import json
from datetime import datetime
from typing import Dict, List

from prompt_optimizer.config import AppConfig

class Reporter:
    def __init__(self, config: AppConfig):
        self.config = config
        self.output_dir = config.run.output_dir
        os.makedirs(self.output_dir, exist_ok=True)
        self.timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        self.run_name = config.run.name

    def write_artifacts(self, all_model_results: List[Dict]):
        base_filename = f"{self.run_name}_{self.timestamp}"

        # Save final prompts
        final_prompts = {
            r["target_model_name"]: r["final_state"]
            for r in all_model_results
        }
        with open(os.path.join(self.output_dir, f"{base_filename}.final_prompts.json"), "w", encoding="utf-8") as f:
            json.dump(final_prompts, f, indent=2, ensure_ascii=False)

        # Save steps
        with open(os.path.join(self.output_dir, f"{base_filename}.optimization_steps.jsonl"), "w", encoding="utf-8") as f:
            for r in all_model_results:
                for step in r["optimization_steps"]:
                    f.write(json.dumps(step, ensure_ascii=False) + "\n")

        # Save train results
        with open(os.path.join(self.output_dir, f"{base_filename}.train_results.jsonl"), "w", encoding="utf-8") as f:
            for r in all_model_results:
                for tr in r["baseline_train_results"]:
                    f.write(json.dumps(tr, ensure_ascii=False) + "\n")

        # Save test results
        with open(os.path.join(self.output_dir, f"{base_filename}.test_results.jsonl"), "w", encoding="utf-8") as f:
            for r in all_model_results:
                for ts in r["test_results"]:
                    f.write(json.dumps(ts, ensure_ascii=False) + "\n")

        # Generate Markdown
        md_content = self._generate_markdown(all_model_results)
        with open(os.path.join(self.output_dir, f"{base_filename}.md"), "w", encoding="utf-8") as f:
            f.write(md_content)

    def _generate_markdown(self, all_model_results: List[Dict]) -> str:
        md = [
            f"# Prompt Optimization Report",
            f"\n## 1. Run Metadata",
            f"- **Name**: {self.run_name}",
            f"- **Timestamp**: {self.timestamp}",
            f"\n## 2. Configuration",
            f"```yaml",
            f"{self.config.model_dump_json(indent=2)}",
            f"```",
            f"\n## 3. Baseline vs Final Test Scores (Mean Overall)",
        ]

        md.append("| Model | Baseline Train | Final Test |")
        md.append("|-------|----------------|------------|")

        for r in all_model_results:
            b_train = r["baseline_train_results"]
            b_mean = sum(x["committee"]["mean_scores"]["overall"] for x in b_train) / len(b_train) if b_train else 0

            f_test = r["test_results"]
            f_mean = sum(x["committee"]["mean_scores"]["overall"] for x in f_test) / len(f_test) if f_test else 0

            md.append(f"| {r['target_model_name']} | {b_mean:.2f} | {f_mean:.2f} |")

        md.append(f"\n## 4. Final Prompts\n")
        for r in all_model_results:
            md.append(f"### Modell: {r['target_model_name']}")
            state = r["final_state"]
            md.append(f"**System Prompt:**\n```text\n{state['system_prompt']}\n```")
            for gid, p in state['user_prompts_by_group'].items():
                md.append(f"**User Prompt ({gid}):**\n```text\n{p}\n```")

        return "\n".join(md)
