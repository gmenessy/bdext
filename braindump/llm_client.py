# 🧠 BrainDump (v3) - Flexible LLM Client
import os
import json
from typing import Dict, Any, Optional, List

class LLMClient:
    """
    Flexible interface for LLM calls (OpenAI, OpenAI-compatible, Gemini, Mock).
    Supports base_url for local or alternative providers (e.g., Ollama, Groq).
    """
    def __init__(
        self, 
        provider: Optional[str] = None, 
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        model: Optional[str] = None
    ):
        self.provider = provider or os.getenv("BRAINDUMP_LLM_PROVIDER", "mock")
        self.api_key = api_key or os.getenv("BRAINDUMP_API_KEY")
        self.base_url = base_url or os.getenv("BRAINDUMP_LLM_BASE_URL")
        self.model = model or os.getenv("BRAINDUMP_LLM_MODEL")

        # Set defaults if not provided
        if not self.model:
            if self.provider == "openai": self.model = "gpt-4o"
            elif self.provider == "gemini": self.model = "gemini-1.5-pro"
            else: self.model = "mock-model"

    def prompt(self, system: str, user: str, response_format: str = "text") -> Any:
        """Sends a prompt to the configured LLM provider."""
        if self.provider in ["openai", "openai-compatible"]:
            return self._openai_prompt(system, user, response_format)
        elif self.provider == "gemini":
            return self._gemini_prompt(system, user, response_format)
        else:
            return self._mock_response(system, user, response_format)

    def _openai_prompt(self, system: str, user: str, response_format: str) -> Any:
        try:
            from openai import OpenAI
            # Support for OpenAI-compatible APIs via base_url
            client = OpenAI(api_key=self.api_key, base_url=self.base_url)
            
            resp_type = {"type": "json_object"} if response_format == "json" else None
            
            response = client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system},
                    {"role": "user", "content": user}
                ],
                response_format=resp_type
            )
            content = response.choices[0].message.content
            return json.loads(content) if response_format == "json" else content
        except Exception as e:
            return {"error": str(e), "status": "fallback_to_mock"}

    def _gemini_prompt(self, system: str, user: str, response_format: str) -> Any:
        try:
            import google.generativeai as genai
            genai.configure(api_key=self.api_key)
            model = genai.GenerativeModel(self.model)
            
            full_prompt = f"SYSTEM: {system}\n\nUSER: {user}"
            response = model.generate_content(full_prompt)
            content = response.text
            
            if response_format == "json":
                # Robust JSON cleaning for Gemini
                clean_content = content.strip()
                if "```json" in clean_content:
                    clean_content = clean_content.split("```json")[1].split("```")[0].strip()
                elif "```" in clean_content:
                    clean_content = clean_content.split("```")[1].split("```")[0].strip()
                return json.loads(clean_content)
            return content
        except Exception as e:
            return {"error": str(e), "status": "fallback_to_mock"}

    def _mock_response(self, system: str, user: str, response_format: str) -> Any:
        """Mock fallback logic."""
        if "extract" in system.lower() or "analyze" in system.lower():
            return {
                "facts": [{"subject": "Task", "predicate": "executed", "object": "successfully"}],
                "entities": [{"name": "BrainDump", "type": "system"}],
                "relations": [{"source": "User", "target": "BrainDump", "type": "interacts_with"}]
            }
        if response_format == "json":
            return {"status": "success", "message": f"Mocked JSON response using {self.model}"}
        return f"BrainDump (Mock - {self.model}): Processed '{user[:30]}...'"

class FactExtractor:
    """Specialized service for extracting structured knowledge and graph nodes."""
    def __init__(self, llm_client: LLMClient):
        self.llm = llm_client

    def analyze_interaction(self, dump_content: Any) -> Dict[str, Any]:
        """Extracts facts, entities, and relations from a dump."""
        system_prompt = """
        You are a Knowledge Graph Engineer. Analyze the interaction and return a JSON object with:
        1. 'facts': List of key observations.
        2. 'entities': List of detected concepts, users, or projects (name, type).
        3. 'relations': List of semantic connections (source, target, type).
        """
        user_prompt = f"Dump Content: {json.dumps(dump_content)}"
        return self.llm.prompt(system_prompt, user_prompt, response_format="json")
