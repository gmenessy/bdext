# 🧠 BrainDump (v3) - Entity Resolver Implementation
import sqlite3
import json
import uuid
from typing import List, Dict, Any, Optional

class EntityResolver:
    """
    Manages the canonical representation of entities and their relations.
    Prevents concept duplication and enables graph-based navigation.
    """
    def __init__(self, db_path: str = "metadata.db"):
        self.db_path = db_path

    def resolve_entity(self, name: str, entity_type: str = "concept") -> str:
        """
        Resolves a name to an entity_id. 
        Creates a new entity if no match (canonical or alias) is found.
        """
        name_lower = name.lower()
        
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            # 1. Check canonical name or aliases (JSON search)
            cursor = conn.execute(
                "SELECT entity_id FROM entities WHERE LOWER(canonical_name) = ? OR aliases LIKE ?",
                (name_lower, f'%"{name}"%')
            )
            row = cursor.fetchone()
            
            if row:
                return row["entity_id"]
            
            # 2. Create new entity if not found
            entity_id = f"ent_{uuid.uuid4().hex[:8]}"
            conn.execute(
                "INSERT INTO entities (entity_id, type, canonical_name, aliases) VALUES (?, ?, ?, ?)",
                (entity_id, entity_type, name, json.dumps([name]))
            )
            return entity_id

    def link_memory_to_entity(self, memory_id: str, entity_id: str):
        """Links a specific memory fragment (VFS node) to a canonical entity."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                "UPDATE memory_entries SET entity_id = ? WHERE id = ?",
                (entity_id, memory_id)
            )

    def create_relation(self, source_id: str, target_id: str, rel_type: str, weight: float = 1.0):
        """Creates a semantic edge in the memory graph."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                "INSERT OR REPLACE INTO relations (source_id, target_id, relation_type, weight) VALUES (?, ?, ?, ?)",
                (source_id, target_id, rel_type, weight)
            )

    def get_related_entities(self, entity_id: str) -> List[Dict[str, Any]]:
        """Finds neighbors in the graph."""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute("""
                SELECT target_id, relation_type, weight 
                FROM relations WHERE source_id = ?
                UNION
                SELECT source_id, relation_type, weight 
                FROM relations WHERE target_id = ?
            """, (entity_id, entity_id))
            return [dict(row) for row in cursor.fetchall()]
