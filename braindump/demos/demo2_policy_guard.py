# 🧠 Demo 2: The Policy Guard - "Governance and Safety"
import sys
import os
from demo_utils import setup_demo_env
from policy_engine import PolicyRule

def run_demo():
    print("🧠 BrainDump Demo 2: The Policy Guard")
    print("------------------------------------")
    env = setup_demo_env("policy_guard")
    policy_engine = env["policy_engine"]
    agent = env["agent"]
    
    # Step 1: Register a "DNA" Policy
    print("\n[Step 1] Registering a strict Governance Policy (DNA)...")
    forbidden_tech_policy = PolicyRule(
        id="policy_tech_guard_v1",
        condition="oracle", # MVP matches keywords in query
        action="BLOCKED: Policy 'No Proprietary DBs' restricts usage of Oracle. Suggest PostgreSQL instead.",
        priority=0.9,
        source="dna"
    )
    policy_engine.register_policy(forbidden_tech_policy)
    print(" ✅ Registered: 'No Proprietary DBs' (Condition: 'oracle')")

    # Step 2: Try a safe task
    print("\n[Step 2] Executing a safe task...")
    task_1 = "Research how to optimize PostgreSQL queries."
    print(f" 👤 Task: '{task_1}'")
    result_1 = agent.run_task(task_1)
    print(f" 🤖 Agent Response: {result_1['output']}")
    print(f" 🔧 Reasoning Trace: {result_1.get('reasoning', 'None')}")

    # Step 3: Try a forbidden task
    print("\n[Step 3] Executing a forbidden task...")
    task_2 = "Should we migrate our core database to Oracle?"
    print(f" 👤 Task: '{task_2}'")
    result_2 = agent.run_task(task_2)
    print(f" 🤖 Agent Response: {result_2['output']}")
    print(f" ⚠️  Reasoning Trace: {result_2.get('reasoning', 'None')}")

    print("\n✨ Demo 2 Complete: The Policy Engine successfully intervened to enforce safety.")

if __name__ == "__main__":
    run_demo()
