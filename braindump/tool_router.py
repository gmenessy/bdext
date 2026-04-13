# 🧠 BrainDump (v3) - Tool Router Implementation
from typing import Dict, Any, List

class ToolRouter:
    """
    Handles tool execution and routing for the agent loop.
    MVP: Simple echo-style router.
    """
    def __init__(self):
        self.tools = {}

    def register(self, name: str, tool_func):
        self.tools[name] = tool_func

    def execute(self, plan: Dict[str, Any]) -> Dict[str, Any]:
        """
        Executes a plan (set of tool calls).
        MVP: Just returns a successful execution message for the query.
        """
        query = plan.get("query", "")
        # Logic: If query starts with 'echo', echo it back.
        if query.startswith("echo "):
            return {"status": "success", "output": query[5:], "tool": "echo"}
        
        # Default: Mock response
        return {
            "status": "success",
            "output": f"Processed: {query}",
            "tool": "default_processor"
        }
