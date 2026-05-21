import pandas as pd
from typing import List

from prompt_optimizer.models import TaskBundle, PromptGroup, TestCase


class DatasetLoader:
    def __init__(self, path: str):
        self.path = path

    def load(self) -> TaskBundle:
        try:
            df = pd.read_csv(self.path)
        except Exception as e:
            raise ValueError(f"Fehler beim Laden der CSV-Datei {self.path}: {e}")

        required_columns = {"system_prompt", "prompt", "input", "expected_output"}
        missing = required_columns - set(df.columns)
        if missing:
            raise ValueError(f"Fehlende Pflichtspalten in der CSV-Datei: {missing}")

        # Fill missing optional columns if needed
        if "group_id" not in df.columns:
            # We can use the user prompt text to group cases
            df["group_id"] = "group_" + df.groupby("prompt").ngroup().astype(str)
        if "case_id" not in df.columns:
            df["case_id"] = "case_" + df.reset_index().index.astype(str)

        # Check if multiple system prompts exist - for MVP, raise error or take first
        unique_sys_prompts = df["system_prompt"].unique()
        if len(unique_sys_prompts) > 1:
            raise ValueError("MVP unterstützt aktuell nur einen globalen system_prompt pro Datensatz.")
        elif len(unique_sys_prompts) == 0:
            raise ValueError("Datensatz ist leer.")

        sys_prompt = unique_sys_prompts[0]

        groups: List[PromptGroup] = []
        for group_id, group_df in df.groupby("group_id"):
            if len(group_df) < 2:
                import warnings
                warnings.warn(f"Warnung: Gruppe {group_id} hat weniger als 2 Testfälle. Ein Train/Test Split ist nicht sinnvoll.")

            cases = []
            for _, row in group_df.iterrows():
                # validate empty inputs/expected outputs
                if pd.isna(row["input"]) or str(row["input"]).strip() == "":
                    raise ValueError(f"Leerer Input bei case_id: {row['case_id']}")
                if pd.isna(row["expected_output"]) or str(row["expected_output"]).strip() == "":
                    raise ValueError(f"Leerer expected_output bei case_id: {row['case_id']}")

                cases.append(TestCase(
                    case_id=str(row["case_id"]),
                    group_id=str(row["group_id"]),
                    input=str(row["input"]),
                    expected_output=str(row["expected_output"])
                ))

            user_prompt = group_df["prompt"].iloc[0]
            groups.append(PromptGroup(
                group_id=str(group_id),
                user_prompt=str(user_prompt),
                test_cases=cases
            ))

        return TaskBundle(
            system_prompt=str(sys_prompt),
            groups=groups
        )
