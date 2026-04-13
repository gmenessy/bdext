# 🧠 Demo 1: BrainDump QuickCapture - "Capture first, structure later"
import sys
import os
from demo_utils import setup_demo_env

def run_demo():
    print("🧠 BrainDump Demo 1: QuickCapture")
    print("---------------------------------")
    env = setup_demo_env("quickcapture")
    agent = env["agent"]
    dream_engine = env["dream_engine"]
    
    # Step 1: Simulating a busy user dumping ideas
    thoughts = [
        "We should start using Python 3.12 for all new microservices.",
        "Met with Sarah. She suggests focusing on the RAG retriever first.",
        "Idea: Deterministic hashing for vector indexing could save memory."
    ]
    
    print("\n[Step 1] Capturing messy thoughts...")
    for thought in thoughts:
        print(f" 📥 Capturing: '{thought}'")
        agent.run_task(thought)
        
    # Step 2: Show that they are in the 'dumps' layer
    import sqlite3
    with sqlite3.connect(env["db_path"]) as conn:
        cursor = conn.execute("SELECT id, summary FROM memory_entries WHERE layer = 'dumps'")
        dumps = cursor.fetchall()
        print(f"\n📊 Dumps layer contains {len(dumps)} active entries.")
        for d in dumps:
            print(f"  - [{d[0]}] {d[1]}")

    # Step 3: Trigger Daydream (Consolidation)
    print("\n[Step 2] Triggering 'Daydream' (Autonomous Consolidation)...")
    result = dream_engine.run_daydream()
    print(f" ✅ Promoted {len(result['promoted'])} entries to the Wiki layer.")
    
    # Step 4: Show the Wiki layer
    with sqlite3.connect(env["db_path"]) as conn:
        cursor = conn.execute("SELECT id, summary FROM memory_entries WHERE layer = 'wiki'")
        wiki = cursor.fetchall()
        print(f"\n📚 Wiki layer now contains {len(wiki)} structured entries:")
        for w in wiki:
            print(f"  - [{w[0]}] {w[1]}")

    print("\n✨ Demo 1 Complete: BrainDump took raw thoughts and structured them autonomously.")

if __name__ == "__main__":
    run_demo()
