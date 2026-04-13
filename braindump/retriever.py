# 🧠 BrainDump (v3) - Retriever (fRAG) Implementation
import sqlite3
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional

@dataclass
class RetrievalContext:
    dna: List[Dict[str, Any]] = field(default_factory=list)
    wiki: List[Dict[str, Any]] = field(default_factory=list)
    decisions: List[Dict[str, Any]] = field(default_factory=list)
    policies: List[Dict[str, Any]] = field(default_factory=list)
    active_tasks: List[Dict[str, Any]] = field(default_factory=list)
    evidence: List[Dict[str, Any]] = field(default_factory=list)

class BrainRetriever:
    def __init__(self, vfs, db_path: str = "metadata.db", entity_resolver=None, vector_service=None):
        self.vfs = vfs
        self.db_path = db_path
        self.entity_resolver = entity_resolver
        self.vector_service = vector_service

    def _query_metadata(self, layer: str, limit: int = 5) -> List[Dict[str, Any]]:
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            # Scoring Formula:
            # recency = exp(-0.1 * days_since_last_used)
            # score = recency * (1 + log(usage_count)) * confidence
            cursor = conn.execute("""
                SELECT *, 
                (
                    exp(-0.1 * (julianday('now') - julianday(last_used))) * 
                    (1 + log(usage_count + 1)) * 
                    confidence
                ) as calc_score
                FROM memory_entries 
                WHERE layer = ? 
                ORDER BY calc_score DESC LIMIT ?
            """, (layer, limit))
            return [dict(row) for row in cursor.fetchall()]

    def retrieve(self, query: str) -> RetrievalContext:
        """
        fRAG = fragment-aware Retrieval over VFS + Graph + Decisions + Policies + Vector.
        Resolves content for all evidence paths.
        """
        # 1. Semantic Vector Search
        semantic_results = []
        if self.vector_service:
            semantic_results = self.vector_service.search(query, limit=5)

        # 2. Entity Resolution
        entities_found = []
        if self.entity_resolver:
            for word in query.split():
                if len(word) > 4: 
                    ent_id = self.entity_resolver.resolve_entity(word.strip("?!.,"))
                    entities_found.append(ent_id)

        context = RetrievalContext()
        
        # 3. Retrieve Fragments from layers
        context.dna = self._query_metadata("core", limit=3)
        context.wiki = self._query_metadata("wiki", limit=5)
        context.decisions = self._query_metadata("decisions", limit=3)
        context.policies = self._query_metadata("core", limit=2)
        
        # 4. Resolve Evidence Content (Graph + Vector)
        raw_evidence_paths = []
        
        # From Graph
        if self.entity_resolver:
            for ent_id in entities_found:
                neighbors = self.entity_resolver.get_related_entities(ent_id)
                for n in neighbors:
                    path = n["target_id"] if "target_id" in n else n["source_id"]
                    raw_evidence_paths.append((path, n["relation_type"], n["weight"]))
        
        # From Vector
        for path, score in semantic_results:
            if score > 0.3:
                raw_evidence_paths.append((path, "semantic_similarity", score))

        # Deduplicate and Resolve Content
        seen_paths = set()
        for path, rel, weight in raw_evidence_paths:
            if path not in seen_paths:
                node = self.vfs.read(path)
                if node:
                    context.evidence.append({
                        "id": path,
                        "content": node.content,
                        "relation": rel,
                        "weight": weight
                    })
                seen_paths.add(path)
        
        return context

    def get_working_memory_payload(self, context: RetrievalContext) -> Dict[str, Any]:
        """Assemble a context for the LLM."""
        return {
            "working_memory": {
                "dna": context.dna,
                "policies": context.policies,
                "wiki": context.wiki,
                "decisions": context.decisions,
                "evidence": context.evidence
            }
        }
