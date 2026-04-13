# 🧠 BrainDump Demo Applications

This directory contains 3 demo applications that showcase the core capabilities of the **BrainDump (v3)** Cognitive Memory System.

All demos use the **Mock LLM Provider**, meaning they do not require an API key to run. They will simulate LLM reasoning and fact extraction.

---

## 1. Demo: QuickCapture - "Capture first, structure later"
**Focus:** Episodic Memory Capture & Autonomous Consolidation.
Demonstrates how BrainDump takes raw, messy user thoughts and promotes them to the structured Wiki layer using the `DreamEngine`.

**Run:**
```bash
python3 demos/demo1_quickcapture.py
```

---

## 2. Demo: The Policy Guard - "Governance and Safety"
**Focus:** Policy-Driven Agent Control.
Demonstrates the `PolicyEngine` enforcing "DNA" rules on agent behavior, blocking forbidden technical choices or unsafe actions.

**Run:**
```bash
python3 demos/demo2_policy_guard.py
```

---

## 3. Demo: Smart Retrieval - "Memory-Augmented Researcher"
**Focus:** fRAG (fragment-aware Retrieval-Augmented Generation) & Knowledge Graph.
Demonstrates how the `BrainRetriever` uses semantic vector search and Knowledge Graph relations to pull relevant information from multiple layers.

**Run:**
```bash
python3 demos/demo3_smart_retrieval.py
```

---

## 4. Demo: Intelligente Akte - "Living Case File"
**Focus:** Bayesian Beliefs, Decision Reasoning, and Temporal Intelligence.
Simulates a 30-day building permit process (Stadt Freiburg) with contradictory structural reports. Demonstrates conflict detection, decision recording with reasoning, and proximity-based prioritization.

**Run:**
```bash
python3 demos/demo4_living_case_file.py
```

---

## Technical Details
- Each demo creates a sandboxed directory (e.g., `demo_data_quickcapture/`) to store its VFS and SQLite metadata.
- Demos use the `demo_utils.py` helper to ensure a clean, consistent setup.
