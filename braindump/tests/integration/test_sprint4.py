# 🧠 BrainDump (v3) - Sprint 4 Integration Test (Graph-Aware Dreaming)
import os
import sqlite3
import shutil
from brain_vfs import BrainVFS, VFSNode
from retriever import BrainRetriever
from tool_router import ToolRouter
from agent_runtime import AgentRuntime
from entity_resolver import EntityResolver
from llm_client import LLMClient, FactExtractor
from dream_engine import DreamEngine

def test_graph_aware_dreaming():
    print("🚀 Starting Sprint 4 Integration Test...")
    
    # 1. Setup
    root_dir = "test_sprint4"
    if os.path.exists(root_dir):
        shutil.rmtree(root_dir)
    os.makedirs(root_dir)
    db_path = os.path.join(root_dir, "metadata.db")
    
    vfs = BrainVFS(root_dir)
    resolver = EntityResolver(db_path=db_path)
    retriever = BrainRetriever(vfs, db_path=db_path, entity_resolver=resolver)
    llm_client = LLMClient(provider="mock")
    fact_extractor = FactExtractor(llm_client)
    dream_engine = DreamEngine(vfs, retriever, fact_extractor=fact_extractor, entity_resolver=resolver)
    
    agent = AgentRuntime(retriever, vfs, ToolRouter(), dream_engine=dream_engine)

    # 2. Simulate Interaction (Writes Dump + Triggers Daydream automatically)
    # The mock analyzer will return entities like "BrainDump" and relations like "User -> interacts_with -> BrainDump"
    agent.run_task("Hello BrainDump, let's test Sprint 4.")
    
    # 3. Assertions
    # Check if "BrainDump" entity exists in the graph
    with sqlite3.connect(db_path) as conn:
        cursor = conn.execute("SELECT canonical_name FROM entities WHERE canonical_name = 'BrainDump'")
        row = cursor.fetchone()
        assert row is not None
        assert row[0] == "BrainDump"
        
        # Check if relations exist (The mock returns User -> interacts_with -> BrainDump)
        cursor = conn.execute("SELECT count(*) FROM relations")
        count = cursor.fetchone()[0]
        assert count > 0
    
    print("Sprint 4 Integration Test: PASSED ✅")

if __name__ == "__main__":
    try:
        test_graph_aware_dreaming()
    finally:
        # shutil.rmtree("test_sprint4")
        pass
