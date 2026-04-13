# 🧠 BrainDump (v3) - Project Context

## Project Overview
**BrainDump** is an Agentic Cognitive Memory System that transforms stateless LLM interactions into a learning cognitive system. It follows the core principle: **"Capture first, structure later."**

The system is currently **Pilot-Ready** and fully implemented as a modular Python-based memory operating system.

## Technical Architecture
### Core Modules
- **VFS Kernel (`brain_vfs.py`)**: Central abstraction for memory storage using the `vfs://` protocol.
- **fRAG Retriever (`retriever.py`)**: Hybrid retrieval combining SQL metadata, Knowledge Graph expansion, and Vector similarity.
- **Vector Service (`vector_service.py`)**: Deterministic trigram-based semantic search for zero-dependency local indexing.
- **Dream Engine (`dream_engine.py`)**: Automated consolidation (Daydream for fact extraction, Nightdream for redundancy merging).
- **Conflict Resolver (`conflict_resolver.py`)**: LLM-based logical consistency checking to prevent contradictory memories.
- **Entity Resolver (`entity_resolver.py`)**: Manages the canonical knowledge graph and semantic relations.
- **Policy Engine (`policy_engine.py`)**: Governance layer for runtime behavioral control and safety overrides.
- **LLM Client (`llm_client.py`)**: Flexible integration for OpenAI, OpenAI-compatible APIs (Ollama, Groq), and Google Gemini.

### Data Structure
- **Storage**: Markdown files (Human-readable truth) + SQLite (Metadata, Graph, Decisions).
- **Layers**: Core (DNA/Policies), Wiki (Skills/Concepts), Dumps (Episodic logs), Decisions (Outcome-based experience).

## Building and Running
### Installation
```bash
pip install -r requirements.txt
```

### Interactive CLI
The primary entry point for the pilot phase:
```bash
python3 main.py
```

### Configuration
Environment variables supported:
- `BRAINDUMP_LLM_PROVIDER`: `openai`, `gemini`, `openai-compatible`, or `mock`.
- `BRAINDUMP_API_KEY`: Your LLM API key.
- `BRAINDUMP_LLM_BASE_URL`: For OpenAI-compatible local providers (e.g., http://localhost:11434/v1).
- `BRAINDUMP_LLM_MODEL`: Specific model name (e.g., `gpt-4o`, `llama3`).

## Development Conventions
- **Memory Immutability**: Direct updates to DNA are restricted; evolution happens via the Dream Engine.
- **Deterministic Hashing**: All vectors use MD5-based trigram hashing to ensure index consistency across restarts.
- **Reasoning Traces**: Every agent action includes a transparency log explaining the retrieval and policy rationale.

## Current Status: Pilot-Ready ✅
All Sprints (1-5) are implemented and verified via integration tests. The system is capable of autonomous knowledge structuring, semantic search, and logical conflict resolution.
