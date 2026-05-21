import aiosqlite
import os
import json
import logging
from prompt_optimizer.models import PromptCandidate

class WikiDatabase:
    def __init__(self, db_path: str):
        self.db_path = db_path
        self.logger = logging.getLogger(__name__)

    async def init_db(self):
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("""
                CREATE TABLE IF NOT EXISTS wiki_insights (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    run_name TEXT,
                    phase TEXT,
                    model_name TEXT,
                    prompt_text TEXT,
                    rationale TEXT,
                    delta REAL,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)
            await db.commit()

    async def store_insight(self, run_name: str, candidate: PromptCandidate, delta: float, target_model: str):
        try:
            async with aiosqlite.connect(self.db_path) as db:
                await db.execute("""
                    INSERT INTO wiki_insights (run_name, phase, model_name, prompt_text, rationale, delta)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (run_name, candidate.phase.value, target_model, candidate.prompt_text, candidate.rationale, delta))
                await db.commit()
        except Exception as e:
            self.logger.error(f"Fehler beim Speichern in Wiki DB: {e}")

    async def get_top_insights(self, target_model: str, limit: int = 3) -> str:
        try:
            async with aiosqlite.connect(self.db_path) as db:
                db.row_factory = aiosqlite.Row
                async with db.execute("""
                    SELECT phase, rationale, delta
                    FROM wiki_insights
                    WHERE model_name = ?
                    ORDER BY delta DESC
                    LIMIT ?
                """, (target_model, limit)) as cursor:
                    rows = await cursor.fetchall()

            if not rows:
                return "Bisher keine historischen Erkenntnisse (WIKI leer)."

            insights = ["Historische WIKI-Erkenntnisse (Was hat zuvor gut funktioniert):"]
            for row in rows:
                insights.append(f"- Phase: {row['phase']}, Delta: +{row['delta']:.2f}, Begründung: {row['rationale']}")

            return "\n".join(insights)
        except Exception as e:
            self.logger.error(f"Fehler beim Lesen aus Wiki DB: {e}")
            return ""
