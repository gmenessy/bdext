# 🧠 BrainDump (v3) - Demo Utilities
import os
import sqlite3
import shutil
from brain_vfs import BrainVFS
from retriever import BrainRetriever
from tool_router import ToolRouter
from agent_runtime import AgentRuntime
from dream_engine import DreamEngine
from decision_memory import DecisionMemory
from entity_resolver import EntityResolver
from policy_engine import PolicyEngine
from llm_client import LLMClient, FactExtractor
from conflict_resolver import ConflictResolver

def setup_demo_env(name: str):
    """
    Sets up a clean, sandboxed BrainDump environment for a specific demo.
    """
    root_dir = f"demo_data_{name}"
    if os.path.exists(root_dir):
        shutil.rmtree(root_dir)
    os.makedirs(root_dir, exist_ok=True)

    # 1. Initialize Components
    vfs = BrainVFS(root_dir=root_dir)
    db_path = vfs.metadata.db_path

    # Initialize DB Schema (Core)
    with open("schema.sql", "r") as f:
        schema = f.read()
    with sqlite3.connect(db_path) as conn:
        conn.executescript(schema)
        # 2. Schema-Extension for 'Living Case File'
        conn.executescript("""
            CREATE TABLE IF NOT EXISTS cases (
              case_id TEXT PRIMARY KEY,
              title TEXT,
              status TEXT,
              opened_at DATETIME,
              deadline DATETIME
            );
            CREATE TABLE IF NOT EXISTS case_links (
              case_id TEXT,
              entity_id TEXT,
              role TEXT
            );
        """)

    llm_client = LLMClient(provider="mock") # Use mock for demos

    fact_extractor = FactExtractor(llm_client)
    entity_resolver = EntityResolver(db_path)
    
    from vector_service import VectorService
    vector_service = VectorService(os.path.join(root_dir, "vector_index.json"))
    vfs.vector_service = vector_service
    
    retriever = BrainRetriever(vfs, db_path, entity_resolver=entity_resolver, vector_service=vector_service)
    conflict_resolver = ConflictResolver(vfs, retriever, llm_client)
    
    dream_engine = DreamEngine(
        vfs, retriever, 
        fact_extractor=fact_extractor, 
        entity_resolver=entity_resolver, 
        conflict_resolver=conflict_resolver
    )
    
    policy_engine = PolicyEngine(vfs, db_path=db_path)
    decision_memory = DecisionMemory(vfs, db_path=db_path)
    tool_router = ToolRouter()
    
    agent = AgentRuntime(
        retriever, vfs, tool_router, 
        policy_engine=policy_engine, 
        decision_memory=decision_memory,
        dream_engine=dream_engine
    )
    
    return {
        "agent": agent,
        "vfs": vfs,
        "retriever": retriever,
        "dream_engine": dream_engine,
        "policy_engine": policy_engine,
        "decision_memory": decision_memory,
        "entity_resolver": entity_resolver,
        "root_dir": root_dir,
        "db_path": db_path
    }
