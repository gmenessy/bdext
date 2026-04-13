# 🧠 BrainDump (v3) - Final Pilot Verification
import os
import sqlite3
import shutil
import time
from brain_vfs import BrainVFS, VFSNode
from retriever import BrainRetriever
from tool_router import ToolRouter
from agent_runtime import AgentRuntime
from decision_memory import DecisionMemory
from entity_resolver import EntityResolver
from policy_engine import PolicyEngine, PolicyRule
from llm_client import LLMClient, FactExtractor
from dream_engine import DreamEngine
from vector_service import VectorService

def test_full_pilot_lifecycle():
    print("🚀 Starting Final Pilot Verification...")
    
    # 1. Setup Environment
    root_dir = "test_pilot_final"
    if os.path.exists(root_dir):
        shutil.rmtree(root_dir)
    os.makedirs(root_dir)
    
    db_path = os.path.join(root_dir, "metadata.db")
    vector_path = os.path.join(root_dir, "vector_index.json")
    
    vector_service = VectorService(vector_path)
    vfs = BrainVFS(root_dir, vector_service=vector_service)
    resolver = EntityResolver(db_path=db_path)
    retriever = BrainRetriever(vfs, db_path=db_path, entity_resolver=resolver, vector_service=vector_service)
    tool_router = ToolRouter()
    decision_memory = DecisionMemory(vfs, db_path=db_path)
    policy_engine = PolicyEngine(vfs, db_path=db_path)
    llm_client = LLMClient(provider="mock")
    fact_extractor = FactExtractor(llm_client)
    dream_engine = DreamEngine(vfs, retriever, fact_extractor=fact_extractor)
    
    agent = AgentRuntime(
        retriever, vfs, tool_router, 
        policy_engine=policy_engine, 
        decision_memory=decision_memory,
        dream_engine=dream_engine
    )

    # 2. Test Policy Enforcement (Governance)
    print(" - Testing Policy Engine...")
    policy = PolicyRule(id="p1", condition="danger", action="echo Blocked by Policy", priority=1.0)
    policy_engine.register_policy(policy)
    res = agent.run_task("danger zone")
    assert "Blocked by Policy" in res["output"]
    print("   ✅ Policy enforced.")

    # 3. Test Knowledge Graph (Entities & Relations)
    print(" - Testing Knowledge Graph...")
    e1 = resolver.resolve_entity("ProjectX", "project")
    e2 = resolver.resolve_entity("Python", "language")
    resolver.create_relation(e1, e2, "uses")
    
    ctx = retriever.retrieve("Tell me about ProjectX")
    evidence_ids = [e["id"] for e in ctx.evidence]
    assert e2 in evidence_ids
    print("   ✅ Graph expansion working.")

    # 4. Test Semantic Search (Vector-Lite)
    print(" - Testing Semantic Search...")
    vfs.write(VFSNode("vfs://wiki/test", "wiki", "The quick brown fox jumps over the lazy dog."))
    # Search for something with character/word overlap
    ctx = retriever.retrieve("quick fox")
    semantic_matches = [e["id"] for e in ctx.evidence if e["relation"] == "semantic_similarity"]
    assert "vfs://wiki/test" in semantic_matches
    print("   ✅ Semantic search working.")

    # 5. Test Memory Consolidation (Dreaming)
    print(" - Testing Dream Engine...")
    # Add a fresh dump to ensure daydream has something to process
    vfs.write(VFSNode("vfs://dumps/sessions/test/new_dump", "dumps", "Fresh interaction content.", metadata={"summary": "New task"}))
    dream_res = dream_engine.run_daydream()
    assert len(dream_res["promoted"]) > 0
    
    # Verify redundancy merge (Nightdream)
    vfs.write(VFSNode("vfs://wiki/dup1", "wiki", "Redundant Content", metadata={"summary": "Duplicate"}))
    vfs.write(VFSNode("vfs://wiki/dup2", "wiki", "Redundant Content", metadata={"summary": "Duplicate"}))
    night_res = dream_engine.run_nightdream()
    assert night_res["merged"] >= 1
    print("   ✅ Dream consolidation working.")

    # 6. Test Memory Scoring (Decay & Usage)
    print(" - Testing Memory Scoring...")
    path = "vfs://wiki/popular"
    vfs.write(VFSNode(path, "wiki", "High usage content", metadata={"summary": "Popular"}))
    
    # Read multiple times to increase usage_count
    for _ in range(3):
        vfs.read(path)
        
    with sqlite3.connect(db_path) as conn:
        conn.row_factory = sqlite3.Row
        row = conn.execute("SELECT usage_count, calc_score FROM (SELECT *, (exp(-0.1 * (julianday('now') - julianday(last_used))) * (1 + log(usage_count + 1)) * confidence) as calc_score FROM memory_entries WHERE id = ?)", (path,)).fetchone()
        assert row["usage_count"] >= 3
        assert row["calc_score"] > 1.0 # Should be boosted by log(usage)
    print("   ✅ Memory scoring & usage tracking working.")

    print("\n🎉 ALL PILOT FEATURES VERIFIED! BrainDump (v3) is ready for deployment. ✅")

if __name__ == "__main__":
    try:
        test_full_pilot_lifecycle()
    except Exception as e:
        print(f"❌ Verification failed: {e}")
        import traceback
        traceback.print_exc()
