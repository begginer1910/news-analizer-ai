import pytest
from database import Database

@pytest.fixture
async def db():
    database = Database(":memory:")
    await database.initialize()
    yield database
    await database.conn.close()

SAMPLE_DATA = {
    "title": "Test Title",
    "url": "https://test.com",
    "category": "tech",
    "language": "en",
    "country": "us",
    "summary": "Test summary",
    "sentiment": 1,
    "publishedAt": "2024-01-01T00:00:00Z",
}

async def assert_row_matches(row, data):
    assert row[1] == data["title"]
    assert row[2] == data["url"]
    assert row[3] == data["category"]
    assert row[4] == data["language"]
    assert row[5] == data["country"]
    assert row[6] == data["summary"]
    assert row[7] == data["sentiment"]
    assert row[8] == data["publishedAt"]

@pytest.mark.asyncio
async def test_initialize_creates_table(db):
    cursor = await db.conn.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='table_news'")
    row = await cursor.fetchone()
    assert row is not None

@pytest.mark.asyncio
async def test_add_article_saved(db):
    result = await db.add_article(SAMPLE_DATA)
    assert result == "saved"
    cursor = await db.conn.execute("SELECT * FROM table_news")
    await assert_row_matches(await cursor.fetchone(),SAMPLE_DATA)

@pytest.mark.asyncio
async def test_add_article_duplicated(db):
    await db.add_article(SAMPLE_DATA)
    result = await db.add_article(SAMPLE_DATA)
    assert result == "duplicated"


