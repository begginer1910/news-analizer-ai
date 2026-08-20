import aiosqlite
import logging 
logger = logging.getLogger(__name__)

class Database:
    def __init__(self, db_path:str):
        self.db_path = db_path
        self.conn = None
    async def _create_scheduler_config_table(self):
        await self.conn.execute("""
            CREATE TABLE IF NOT EXISTS scheduler_config (
                id INTEGER PRIMARY KEY CHECK (id =1),
                category TEXT NOT NULL,
                language TEXT NOT NULL,
                country TEXT NOT NULL,
                interval_h INTEGER NOT NULL
                )
            """)
        await self.conn.commit()
    async def _fetch_scheduler_config_row(self):
        cursor = await self.conn.execute(
            "SELECT category, language, country, interval_h FROM scheduler_config WHERE id = 1"
        )
        return await cursor.fetchone()

    async def _update_scheduler_config_row(
        self,
        category: str,
        language: str,
        country: str,
        interval_h: int,
    ):
       await self.conn.execute(
            """
            UPDATE scheduler_config
            SET category = ?, language = ?, country = ?, interval_h = ?
            WHERE id = 1
            """,
            (category, language, country, interval_h),
        )
       await self.conn.commit()
    async def initialize(self):
        if self.conn is not None:
            try:
                await self.conn.execute("SELECT 1")
                return
            except Exception:
                self.conn = None
        self.conn = await aiosqlite.connect(self.db_path)
        await self.conn.execute("PRAGMA journal_mode=WAL")
        self.conn.row_factory = aiosqlite.Row
        await self._create_scheduler_config_table()
        await self.conn.execute("""
            INSERT OR IGNORE INTO scheduler_config (id, category, language, country, interval_h)
            VALUES (1, 'general', 'en', 'us', 24)
        """)
        await self.conn.commit()
        await self.conn.execute("""
                    CREATE TABLE IF NOT EXISTS table_news (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        title TEXT UNIQUE,
                        url TEXT NOT NULL,
                        category TEXT NOT NULL,
                        language TEXT NOT NULL,
                        country TEXT NOT NULL,
                        summary TEXT NOT NULL,
                        sentiment INTEGER,
                        publishedAt TEXT NOT NULL
                    ) 
                """)
        await self.conn.commit()
        logger.info("Tables created")

    async def add_article(self, data):
        new = ("INSERT INTO table_news (title, url, category, language, country, summary, sentiment, publishedAt)"
               " VALUES (?,?,?,?,?,?,?,?)")
        try:
            await self.conn.execute(new, (
                data['title'], data['url'], data['category'],
                data['language'],data["country"], data['summary'], data['sentiment'],
                data['publishedAt']
            ))
            await self.conn.commit()
            return "saved"

        except aiosqlite.IntegrityError:
            return "duplicated"
    
    async def get_articles(self, category=None, limit=20):
        if category:
            cursor = await self.conn.execute(
                "SELECT * FROM table_news WHERE category = ? ORDER BY id DESC LIMIT ?",
                (category, limit)
            )
        else:
            cursor = await self.conn.execute(
                "SELECT * FROM table_news ORDER BY id DESC LIMIT ?",
                (limit,)
            )
        rows = await cursor.fetchall()
        return [dict(row) for row in rows]