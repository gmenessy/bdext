from pydantic import BaseModel
from typing import List

class PromptState(BaseModel):
    target_model_name: str
    system_prompt: str
    user_prompts_by_group: dict[str, str]
    # Ensembling: We can optionally store top N alternative system prompts
    ensemble_system_prompts: List[str] = []
