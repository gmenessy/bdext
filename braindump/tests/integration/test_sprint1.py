# 🧠 BrainDump (v3) - Sprint 1 Integration Test
import os
import sqlite3
from brain_vfs import BrainVFS, VFSNode
from retriever import BrainRetriever
from tool_router import ToolRouter
from agent_runtime import AgentRuntime

def test_agent_loop_integration():
    """
    Test the basic Agent Loop: 
    Retrieval -> Execution -> Dump Log.
    """
    # 1. Setup Kernel
    root_dir = "test_data"
    os.makedirs(root_dir, exist_ok=True)
    vfs = BrainVFS(root_dir)
    
    # 2. Setup Components
    retriever = BrainRetriever(vfs, db_path=os.path.join(root_dir, "metadata.db"))
    tool_router = ToolRouter()
    agent = AgentRuntime(retriever, vfs, tool_router)
    
    # 3. Add initial memory (Wiki)
    wiki_node = VFSNode(
        path="vfs://wiki/projects/test_project",
        layer="wiki",
        content="Test Project Definition",
        metadata={"summary": "A test project for Sprint 1 validation."}
    )
    vfs.write(wiki_node)
    
    # 4. Run Task
    task_input = "echo Hello BrainDump!"
    result = agent.run_task(task_input)
    
    # 5. Assertions
    assert result["status"] == "success"
    assert result["output"] == "Hello BrainDump!"
    assert result["tool"] == "echo"
    
    # 6. Verify Dump was written
    with sqlite3.connect(os.path.join(root_dir, "metadata.db")) as conn:
        cursor = conn.execute("SELECT count(*) FROM memory_entries WHERE layer = 'dumps'")
        count = cursor.fetchone()[0]
        assert count > 0
    
    print("Sprint 1 Integration Test: PASSED ✅")

if __name__ == "__main__":
    try:
        test_agent_loop_integration()
    finally:
        # Cleanup
        # shutil.rmtree("test_data")
        pass
