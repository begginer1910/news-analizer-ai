from database import Database
from config import ALLOWED_INTERVALS_H

class SchedulerConfigService:
    def __init__(self, db: Database):
        self.db = db

    async def get(self):
        row = await self.db._fetch_scheduler_config_row()
        if not row:
            raise RuntimeError("Missing config scheduler")
        return {
            "category": row[0],
            "language": row[1],
            "country": row[2],
            "interval_h": row[3],
        }

    async def update(self, *, category: str, language: str, country: str, interval_h: int):
        if interval_h not in ALLOWED_INTERVALS_H:
            raise ValueError(f"interval_h must be one of {ALLOWED_INTERVALS_H}")
        await self.db._update_scheduler_config_row(category, language, country, interval_h)
        return await self.get()
