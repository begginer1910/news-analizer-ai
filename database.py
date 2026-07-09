import aiosqlite

class Database:
    def __init__(self, db_path:str):
        self.db_path = db_path
        self.conn = None
    async def initialize(self):
        if self.conn is not None:
            return
        self.conn = await aiosqlite.connect(self.db_path)
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
        print("Table created")

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

