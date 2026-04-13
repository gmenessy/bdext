# 🧠 BrainDump (v3) - Sprint 2 Integration Test
import os
import sqlite3
from brain_vfs import BrainVFS, VFSNode
from retriever import BrainRetriever
from tool_router import ToolRouter
from agent_runtime import AgentRuntime
from decision_memory import DecisionMemory
from dream_engine import DreamEngine

def test_learning_loop_integration():
    """
    Test the learning loop: 
    Decision Record -> Task -> Daydream Promotion.
    """
    # 1. Setup Kernel
    root_dir = "test_data_s2"
    os.makedirs(root_dir, exist_ok=True)
    vfs = BrainVFS(root_dir)
    db_path = os.path.join(root_dir, "metadata.db")
    
    # 2. Setup Components
    retriever = BrainRetriever(vfs, db_path=db_path)
    tool_router = ToolRouter()
    decision_memory = DecisionMemory(vfs, db_path=db_path)
    dream_engine = DreamEngine(vfs, retriever)
    agent = AgentRuntime(retriever, vfs, tool_router, decision_memory=decision_memory, dream_engine=dream_engine)
    
    # 3. Run Task with Decision
    decision_info = {
        "decision": "Use echo tool for hello world",
        "reasoning": "Fastest and safest for basic output.",
        "action": "execute_echo",
        "reward": 0.9
    }
    task_input = "echo Sprint 2"
    agent.run_task(task_input, decision_info=decision_info)
    
    # 4. Verify Decision Record
    with sqlite3.connect(db_path) as conn:
        cursor = conn.execute("SELECT outcome_score FROM decisions LIMIT 1")
        score = cursor.fetchone()[0]
        assert score == 0.9
        
        # Verify Daydream promoted the dump to wiki
        cursor = conn.execute("SELECT count(*) FROM memory_entries WHERE layer = 'wiki' AND id LIKE 'vfs://wiki/concepts/%'")
        count = cursor.fetchone()[0]
        assert count > 0
        
        # Verify Dump state is 'processed'
        cursor = conn.execute("SELECT state FROM memory_entries WHERE layer = 'dumps' LIMIT 1")
        state = cursor.fetchone()[0]
        assert state == 'processed'
    
    print("Sprint 2 Integration Test: PASSED ✅")

if __name__ == "__main__":
    try:
        test_learning_loop_integration()
    finally:
        # Cleanup
        # shutil.rmtree("test_data_s2")
        pass
