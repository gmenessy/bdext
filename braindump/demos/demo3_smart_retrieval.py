# 🧠 Demo 3: Smart Retrieval - "Memory-Augmented Researcher"
import sys
import os
import sqlite3
from demo_utils import setup_demo_env
from brain_vfs import VFSNode

def run_demo():
    print("🧠 BrainDump Demo 3: Smart Retrieval")
    print("-----------------------------------")
    env = setup_demo_env("smart_retrieval")
    agent = env["agent"]
    vfs = env["vfs"]
    entity_resolver = env["entity_resolver"]
    retriever = env["retriever"]
    
    # Step 1: Seeding initial Knowledge Layer (Wiki)
    print("\n[Step 1] Seeding initial Wiki and Graph...")
    
    # Wiki: Project Artemis
    vfs.write(VFSNode(
        path="vfs://wiki/projects/artemis",
        layer="wiki",
        content={"summary": "Project Artemis focuses on decentralized identity solutions.", "tech": "W3C DID, Verifiable Credentials"},
        metadata={"summary": "Project Artemis Definition"}
    ))
    
    # Wiki: Sarah (The expert)
    vfs.write(VFSNode(
        path="vfs://wiki/users/sarah",
        layer="wiki",
        content={"name": "Sarah", "role": "Senior Architect", "expertise": ["RAG", "Identity"]},
        metadata={"summary": "User: Sarah Expert Profile"}
    ))

    # Graph Relation: Sarah -> Project Artemis
    sarah_id = entity_resolver.resolve_entity("Sarah", "user")
    artemis_id = entity_resolver.resolve_entity("Artemis", "project")
    entity_resolver.create_relation(sarah_id, artemis_id, "leads")
    print(" ✅ Wiki Seeded & Graph Relations established: 'Sarah leads Project Artemis'")

    # Step 2: Querying the agent
    print("\n[Step 2] Querying the researcher...")
    query = "Who is the lead for Project Artemis and what is their expertise?"
    print(f" 👤 Query: '{query}'")
    
    # We'll look at the retrieval context directly to see fRAG in action
    context = retriever.retrieve(query)
    
    print("\n📊 fRAG Retrieval Insights:")
    print(f"  - Wiki entries found: {len(context.wiki)}")
    print(f"  - Knowledge Fragments (Evidence): {len(context.evidence)}")
    for e in context.evidence:
        print(f"    * Found: {e['id']} (Relation: {e['relation']})")

    # Step 3: Result
    result = agent.run_task(query)
    print(f"\n🤖 Agent Response: {result['output']}")
    print(f"🔧 Reasoning Trace: {result.get('reasoning', 'None')}")

    print("\n✨ Demo 3 Complete: BrainDump retrieved relevant info across Wiki and Graph.")

if __name__ == "__main__":
    run_demo()
