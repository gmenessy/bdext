# 🧠 BrainDump (v3) - Decision Memory Implementation
import sqlite3
import json
from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, Any, List, Optional

@dataclass
class DecisionRecord:
    id: str
    task_id: str
    decision: str
    reasoning_summary: str
    chosen_action: str
    outcome_score: float = 0.0
    created_at: datetime = field(default_factory=datetime.utcnow)

class DecisionMemory:
    """
    Experience-driven outcome based memory.
    """
    def __init__(self, vfs, db_path: str = "metadata.db"):
        self.vfs = vfs
        self.db_path = db_path

    def record(self, record: DecisionRecord):
        """Records a strategic decision to storage and index."""
        from brain_vfs import VFSNode
        
        # 1. Write to VFS
        vfs_path = f"vfs://decisions/{record.id}"
        node = VFSNode(
            path=vfs_path,
            layer="decisions",
            content={
                "task_id": record.task_id,
                "decision": record.decision,
                "reasoning": record.reasoning_summary,
                "chosen_action": record.chosen_action,
                "outcome_score": record.outcome_score,
                "timestamp": record.created_at.isoformat()
            },
            metadata={"summary": f"Decision: {record.decision[:50]}..."}
        )
        self.vfs.write(node)
        
        # 2. Index in Decisions table for fast query
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT OR REPLACE INTO decisions (id, task_id, decision, reasoning_summary, chosen_action, outcome_score, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (record.id, record.task_id, record.decision, record.reasoning_summary, record.chosen_action, record.outcome_score, record.created_at.isoformat()))

    def update_outcome(self, decision_id: str, reward: float):
        """Updates the outcome score of a decision."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("UPDATE decisions SET outcome_score = ? WHERE id = ?", (reward, decision_id))
            
            # Also update VFS node
            vfs_path = f"vfs://decisions/{decision_id}"
            node = self.vfs.read(vfs_path)
            if node:
                node.content["outcome_score"] = reward
                self.vfs.write(node)
