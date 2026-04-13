# 🧠 BrainDump (v3) - Agent Runtime & Orchestrator Implementation
from datetime import datetime
import uuid
from typing import Dict, Any, Optional

class AgentRuntime:
    def __init__(
        self,
        retriever,
        vfs,
        tool_router,
        policy_engine=None,
        decision_memory=None,
        dream_engine=None,
    ):
        self.retriever = retriever
        self.vfs = vfs
        self.tool_router = tool_router
        self.policy_engine = policy_engine
        self.decision_memory = decision_memory
        self.dream_engine = dream_engine

    def run_task(self, task_input: str, decision_info: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Orchestrate the interaction loop:
        1. Retrieval (fRAG)
        2. Policy Injection (Governance)
        3. Reasoning (Thinking)
        4. Tool Execution
        5. Logging & Dreaming
        """
        # 1. Retrieval (fRAG)
        context = self.retriever.retrieve(task_input)

        # 2. Policy Injection
        policy_context = {"query": task_input, "context": context}
        policy_hint = self.policy_engine.apply(policy_context) if self.policy_engine else {}

        # 3. Reasoning Trace (Transparency)
        # In a full system, this would be an LLM-call explaining the chosen path
        reasoning_trace = f"Analyzing task. Relevant contexts: {len(context.wiki)} wiki entries, {len(context.evidence)} evidence fragments. "
        if policy_hint:
            reasoning_trace += f"Applying policy {policy_hint.get('rule_id')}. "

        # 4. Execution Plan
        execution_query = policy_hint.get("policy_override", task_input) if policy_hint else task_input

        # 5. Execution
        result = self.tool_router.execute({"query": execution_query})
        result["reasoning"] = reasoning_trace

        # 6. Dump Log
        self._write_dump(task_input, result)

        # 7. Record Decision
        if decision_info and self.decision_memory:
            from decision_memory import DecisionRecord
            record = DecisionRecord(
                id=uuid.uuid4().hex[:8],
                task_id=uuid.uuid4().hex[:8],
                decision=decision_info.get("decision", ""),
                reasoning_summary=decision_info.get("reasoning", ""),
                chosen_action=decision_info.get("action", ""),
                outcome_score=decision_info.get("reward", 0.0)
            )
            self.decision_memory.record(record)
            
        # 8. Trigger Daydream (Consolidation)
        if hasattr(self, "dream_engine") and self.dream_engine:
            self.dream_engine.run_daydream()
        
        return result

    def _write_dump(self, task_input: str, result: Dict[str, Any]):
        """Write interaction to the Dump layer."""
        from brain_vfs import VFSNode
        
        session_id = datetime.now().strftime("%Y-%m-%d")
        timestamp = datetime.now().isoformat()
        dump_node = VFSNode(
            path=f"vfs://dumps/sessions/{session_id}/task_{uuid.uuid4().hex[:8]}",
            layer="dumps",
            content={
                "task": task_input,
                "result": result,
                "timestamp": timestamp
            },
            metadata={"summary": f"Task: {task_input[:50]}..."}
        )
        self.vfs.write(dump_node)
