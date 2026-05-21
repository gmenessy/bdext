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
                    is_anti_pattern BOOLEAN,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)
            await db.commit()

    async def store_insight(self, run_name: str, candidate: PromptCandidate, delta: float, target_model: str, is_anti_pattern: bool = False):
        try:
            async with aiosqlite.connect(self.db_path) as db:
                await db.execute("""
                    INSERT INTO wiki_insights (run_name, phase, model_name, prompt_text, rationale, delta, is_anti_pattern)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (run_name, candidate.phase.value, target_model, candidate.prompt_text, candidate.rationale, delta, is_anti_pattern))
                await db.commit()
        except Exception as e:
            self.logger.error(f"Fehler beim Speichern in Wiki DB: {e}")

    async def get_top_insights(self, target_model: str, pos_limit: int = 3, neg_limit: int = 2) -> str:
        try:
            async with aiosqlite.connect(self.db_path) as db:
                db.row_factory = aiosqlite.Row

                # Fetch positive insights
                async with db.execute("""
                    SELECT phase, rationale, delta
                    FROM wiki_insights
                    WHERE model_name = ? AND is_anti_pattern = FALSE
                    ORDER BY delta DESC
                    LIMIT ?
                """, (target_model, pos_limit)) as cursor:
                    pos_rows = await cursor.fetchall()

                # Fetch negative insights (anti-patterns)
                async with db.execute("""
                    SELECT phase, rationale, delta
                    FROM wiki_insights
                    WHERE model_name = ? AND is_anti_pattern = TRUE
                    ORDER BY delta ASC
                    LIMIT ?
                """, (target_model, neg_limit)) as cursor:
                    neg_rows = await cursor.fetchall()

            if not pos_rows and not neg_rows:
                return "Bisher keine historischen Erkenntnisse (WIKI leer)."

            insights = []
            if pos_rows:
                insights.append("Historische WIKI-Erkenntnisse (Was hat zuvor GUT funktioniert):")
                for row in pos_rows:
                    insights.append(f"- Phase: {row['phase']}, Delta: +{row['delta']:.2f}, Erfolgsgrund: {row['rationale']}")

            if neg_rows:
                insights.append("\nHistorische ANTI-PATTERNS (Was in Sackgassen führte - bitte VERMEIDEN):")
                for row in neg_rows:
                    insights.append(f"- Phase: {row['phase']}, Delta: {row['delta']:.2f}, Fehlergrund: {row['rationale']}")

            return "\n".join(insights)
        except Exception as e:
            self.logger.error(f"Fehler beim Lesen aus Wiki DB: {e}")
            return ""
