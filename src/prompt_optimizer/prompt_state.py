from pydantic import BaseModel

class PromptState(BaseModel):
    target_model_name: str
    system_prompt: str
    user_prompts_by_group: dict[str, str]
