# 🧠 BrainDump (v3) - Sprint 3 Integration Test
import os
import sqlite3
from brain_vfs import BrainVFS
from retriever import BrainRetriever
from tool_router import ToolRouter
from agent_runtime import AgentRuntime
from policy_engine import PolicyEngine, PolicyRule

def test_governance_loop_integration():
    """
    Test the governance loop: 
    Policy Register -> Task Evaluation -> Action Override.
    """
    # 1. Setup Kernel
    root_dir = "test_data_s3"
    os.makedirs(root_dir, exist_ok=True)
    vfs = BrainVFS(root_dir)
    db_path = os.path.join(root_dir, "metadata.db")
    
    # 2. Setup Components
    retriever = BrainRetriever(vfs, db_path=db_path)
    tool_router = ToolRouter()
    policy_engine = PolicyEngine(vfs, db_path=db_path)
    agent = AgentRuntime(retriever, vfs, tool_router, policy_engine=policy_engine)
    
    # 3. Register a "Safety" Policy
    # Condition: "rm -rf"
    # Action: "echo Safe: Blocking delete command."
    policy = PolicyRule(
        id="safety_block_delete",
        condition="rm -rf",
        action="echo Safe: Blocking delete command.",
        priority=1.0,
        source="system"
    )
    policy_engine.register_policy(policy)
    
    # 4. Run Dangerous Task
    dangerous_input = "rm -rf /"
    result = agent.run_task(dangerous_input)
    
    # 5. Assertions
    # The result should come from the echo tool (the policy override), not the real (mocked) router.
    assert result["status"] == "success"
    assert "Safe: Blocking delete command." in result["output"]
    assert result["tool"] == "echo"
    
    print("Sprint 3 Integration Test: PASSED ✅")

if __name__ == "__main__":
    try:
        test_governance_loop_integration()
    finally:
        # Cleanup
        # shutil.rmtree("test_data_s3")
        pass
