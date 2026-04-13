# 🧠 BrainDump (v3) - Conflict Resolution Engine
import sqlite3
import json
from typing import List, Dict, Any, Tuple, Optional

class ConflictResolver:
    """
    Detects and manages contradictions in the Knowledge Layer.
    """
    def __init__(self, vfs, retriever, llm_client):
        self.vfs = vfs
        self.retriever = retriever
        self.llm = llm_client

    def check_for_conflicts(self, new_node_path: str) -> List[Dict[str, Any]]:
        """
        Scans existing wiki entries for potential contradictions with a new node.
        """
        new_node = self.vfs.read(new_node_path)
        if not new_node:
            return []

        # 1. Retrieve semantically similar existing entries
        # We use a lower threshold to find anything remotely related
        context = self.retriever.retrieve(str(new_node.content))
        potential_matches = context.wiki + [e for e in context.evidence if "wiki" in e.get("id", "")]
        
        conflicts = []
        for match in potential_matches:
            match_id = match.get("id") or match.get("path")
            if match_id == new_node_path:
                continue
                
            match_node = self.vfs.read(match_id)
            if not match_node:
                continue

            # 2. LLM Validation: Ask if they contradict
            is_conflict = self._validate_conflict_with_llm(new_node.content, match_node.content)
            
            if is_conflict:
                conflicts.append({
                    "original_id": match_id,
                    "new_id": new_node_path,
                    "reason": "Semantic contradiction detected by LLM."
                })
        
        return conflicts

    def _validate_conflict_with_llm(self, content_a: Any, content_b: Any) -> bool:
        """Uses LLM to detect if two pieces of information are logically contradictory."""
        system_prompt = "You are a Logic Validator. Compare two pieces of information and determine if they are logically contradictory. Return JSON: {'is_contradictory': true/false, 'explanation': '...'}"
        user_prompt = f"Info A: {json.dumps(content_a)}\n\nInfo B: {json.dumps(content_b)}"
        
        result = self.llm.prompt(system_prompt, user_prompt, response_format="json")
        return result.get("is_contradictory", False) if isinstance(result, dict) else False

    def resolve_automatically(self, conflict: Dict[str, Any]):
        """
        Resolves a conflict based on recency/confidence.
        MVP: Mark the older one as 'superseded'.
        """
        with sqlite3.connect(self.vfs.metadata.db_path) as conn:
            # Mark the older entry as superseded
            conn.execute("UPDATE memory_entries SET state = 'superseded' WHERE id = ?", (conflict["original_id"],))
            print(f"⚠️ Conflict Resolved: {conflict['original_id']} superseded by {conflict['new_id']}")
