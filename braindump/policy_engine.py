# 🧠 BrainDump (v3) - Policy Engine Implementation
import sqlite3
import json
from dataclasses import dataclass
from typing import Dict, Any, List, Optional

@dataclass
class PolicyRule:
    id: str
    condition: str
    action: str
    priority: float = 0.5
    confidence: float = 0.8
    source: str = "system"

class PolicyEngine:
    """
    Adaptive Governance layer for agent control.
    """
    def __init__(self, vfs, db_path: str = "metadata.db"):
        self.vfs = vfs
        self.db_path = db_path

    def register_policy(self, rule: PolicyRule):
        """Registers a new policy rule."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT OR REPLACE INTO policies (id, condition, action, priority, confidence, source)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (rule.id, rule.condition, rule.action, rule.priority, rule.confidence, rule.source))

    def evaluate(self, task_context: Dict[str, Any]) -> List[PolicyRule]:
        """
        Matches applicable policies for a given context.
        MVP: Simple keyword match in conditions.
        """
        task_query = task_context.get("query", "").lower()
        applicable_rules = []
        
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute("SELECT * FROM policies ORDER BY priority DESC")
            rules = cursor.fetchall()
            
            for r in rules:
                condition = r["condition"].lower()
                if condition in task_query:
                    applicable_rules.append(PolicyRule(
                        id=r["id"],
                        condition=r["condition"],
                        action=r["action"],
                        priority=r["priority"],
                        confidence=r["confidence"],
                        source=r["source"]
                    ))
        
        return applicable_rules

    def apply(self, task_context: Dict[str, Any]) -> Dict[str, Any]:
        """Composes an execution plan or modifies the context based on policies."""
        rules = self.evaluate(task_context)
        # MVP: Return the first matching action as an override or hint
        if rules:
            return {"policy_override": rules[0].action, "rule_id": rules[0].id}
        return {}
