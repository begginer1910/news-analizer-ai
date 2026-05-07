import sqlite3
class Data_base:
    def __init__(self):
        self.conn = sqlite3.connect("news.db")
        self.c = self.conn.cursor()
        self.c.execute("""
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
        self.conn.commit()
    def add_article(self, data):
        new = ("INSERT INTO table_news (title, url, category, language, country, summary, sentiment, publishedAt)"
               " VALUES (?,?,?,?,?,?,?,?)")
        try:
            self.c.execute(new, (
                data['title'], data['url'], data['category'],
                data['language'],data["country"], data['summary'], data['sentiment'],
                data['publishedAt']
            ))
            self.conn.commit()
            print(f"Saved: {data['title'][:30]}...")

        except sqlite3.IntegrityError:
            print("The article already exists in the database.")
