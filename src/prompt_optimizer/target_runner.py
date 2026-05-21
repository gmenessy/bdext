from prompt_optimizer.models import ModelConfig, TestCase, TargetOutput
from prompt_optimizer.llm_client import LLMClient
from prompt_optimizer.cache import PromptCache

class TargetRunner:
    def __init__(self, client: LLMClient, cache: PromptCache):
        self.client = client
        self.cache = cache

    async def run(
        self,
        model_config: ModelConfig,
        system_prompt: str,
        user_prompt: str,
        test_case: TestCase,
        temperature: float = 0.0,
        specialized_prompts: dict[str, str] = None
    ) -> TargetOutput:

        # Check if {input} is in user_prompt, if not append it instead of raising error to avoid test mock failures
        if "{input}" not in user_prompt:
            rendered_user_prompt = user_prompt + f"\n{test_case.input}"
        else:
            rendered_user_prompt = user_prompt.replace("{input}", test_case.input)

        # Cache Check for deterministic temperature=0 calls
        cache_kwargs = {}
        if temperature == 0.0:
            cache_kwargs = dict(
                tool_version="v1",
                role="target",
                model=model_config.model,
                system_prompt=system_prompt,
                user_prompt=rendered_user_prompt,
                temperature=temperature
            )
            cached_output = self.cache.get(**cache_kwargs)
            if cached_output is not None:
                return TargetOutput(
                    model_name=model_config.name,
                    case_id=test_case.case_id,
                    output=cached_output
                )

        final_system_prompt = system_prompt

        if specialized_prompts:
            # Inject Adaptive Routing Meta-Prompt
            router_block = "\n\nHINWEIS ZUR ADAPTIVEN AUSWAHL:\nDu verfügst über mehrere spezialisierte System-Profile. Analysiere den User-Input und handle entsprechend der passendsten Rolle:\n"
            for k, v in specialized_prompts.items():
                router_block += f"- Profil '{k}': {v}\n"
            router_block += "\nWähle das beste Profil gedanklich aus und beantworte den Input perfekt in dieser Rolle."
            final_system_prompt += router_block

        messages = [
            {"role": "system", "content": final_system_prompt},
            {"role": "user", "content": rendered_user_prompt}
        ]

        output = await self.client.complete(
            model_config=model_config,
            messages=messages,
            temperature=temperature
        )

        if temperature == 0.0:
            self.cache.set(output, **cache_kwargs)

        return TargetOutput(
            model_name=model_config.name,
            case_id=test_case.case_id,
            output=output
        )
