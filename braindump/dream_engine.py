# 🧠 BrainDump (v3) - Dream Engine Implementation
from typing import List, Dict, Any, Optional
from brain_vfs import VFSNode
import uuid

class DreamEngine:
    """
    The consolidation and learning core of BrainDump.
    """
    def __init__(self, vfs, retriever, fact_extractor=None, entity_resolver=None, conflict_resolver=None):
        self.vfs = vfs
        self.retriever = retriever
        self.fact_extractor = fact_extractor
        self.entity_resolver = entity_resolver
        self.conflict_resolver = conflict_resolver

    def run_daydream(self) -> Dict[str, Any]:
        """
        Micro Consolidation:
        1. Scan Dumps for new interactions.
        2. LLM Analysis: Extract Facts, Entities, Relations.
        3. Register Entities & Graph relations.
        4. Promote to Wiki.
        """
        import sqlite3
        promoted_paths = []
        with sqlite3.connect(self.vfs.metadata.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute("SELECT * FROM memory_entries WHERE layer = 'dumps' AND state = 'active'")
            dumps = cursor.fetchall()
            
            for dump in dumps:
                dump_path = dump["id"]
                node = self.vfs.read(dump_path)
                
                # 1. LLM Analysis (Deep Insight)
                analysis = {}
                if self.fact_extractor and node:
                    analysis = self.fact_extractor.analyze_interaction(node.content)
                
                # 2. Graph Update: Register Entities & Relations
                if self.entity_resolver and analysis:
                    # Register Entities
                    ent_map = {}
                    for ent in analysis.get("entities", []):
                        eid = self.entity_resolver.resolve_entity(ent["name"], ent.get("type", "concept"))
                        ent_map[ent["name"]] = eid
                    
                    # Register Relations
                    for rel in analysis.get("relations", []):
                        src_id = ent_map.get(rel["source"]) or self.entity_resolver.resolve_entity(rel["source"])
                        tgt_id = ent_map.get(rel["target"]) or self.entity_resolver.resolve_entity(rel["target"])
                        self.entity_resolver.create_relation(src_id, tgt_id, rel["type"])

                # 3. Promote to Wiki
                target_path = f"vfs://wiki/concepts/learned_{uuid.uuid4().hex[:8]}"
                new_node = VFSNode(
                    path=target_path,
                    layer="wiki",
                    content={"analysis": analysis, "original": node.content if node else None},
                    metadata={"summary": dump["summary"], "source": dump_path}
                )
                self.vfs.write(new_node)
                
                # 4. Conflict Check: Automated logical consistency
                if self.conflict_resolver:
                    conflicts = self.conflict_resolver.check_for_conflicts(target_path)
                    for c in conflicts:
                        self.conflict_resolver.resolve_automatically(c)
                
                # 5. Cooling
                conn.execute("UPDATE memory_entries SET state = 'processed' WHERE id = ?", (dump_path,))
                promoted_paths.append(target_path)
        
        return {
            "status": "success",
            "promoted": promoted_paths,
            "mode": "daydream"
        }

    def run_nightdream(self) -> Dict[str, Any]:
        """
        Deep Consolidation:
        1. Identify redundant Wiki entries (Mocked by title similarity).
        2. Merge content and update metadata.
        3. Archive old entries.
        """
        import sqlite3
        merged_count = 0
        
        with sqlite3.connect(self.vfs.metadata.db_path) as conn:
            conn.row_factory = sqlite3.Row
            # 1. Group Wiki entries by summary (Simplification for MVP)
            cursor = conn.execute("""
                SELECT summary, count(*) as cnt, GROUP_CONCAT(id) as ids 
                FROM memory_entries 
                WHERE layer = 'wiki' 
                GROUP BY summary 
                HAVING cnt > 1
            """)
            redundant_groups = cursor.fetchall()
            
            for group in redundant_groups:
                ids = group["ids"].split(",")
                canonical_id = ids[0]
                duplicates = ids[1:]
                
                # 2. Merge logic (MVP: Just log and mark duplicates for archival)
                for dup_id in duplicates:
                    conn.execute("UPDATE memory_entries SET state = 'archived' WHERE id = ?", (dup_id,))
                    merged_count += 1
                    
        return {
            "status": "success",
            "merged": merged_count,
            "mode": "nightdream"
        }
