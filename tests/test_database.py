import pytest
from app.database import Database

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

@pytest.mark.asyncio
async def test_initialize_creates_scheduler_config_table(db):
    cursor = await db.conn.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='scheduler_config'")
    row = await cursor.fetchone()
    assert row is not None

@pytest.mark.asyncio
async def test_initialize_creates_default_config(db):
    row = await db._fetch_scheduler_config_row()
    assert tuple(row) == ("general", "en", "us", 24)

@pytest.mark.asyncio
async def test_update_scheduler_config_row(db):
    await db._update_scheduler_config_row("technology", "pl", "pl", 12)
    row = await db._fetch_scheduler_config_row()
    assert tuple(row) == ("technology", "pl", "pl", 12)

@pytest.mark.asyncio
async def test_initialize_reconnects_after_close():
    database = Database(":memory:")
    await database.initialize()
    await database.conn.close()
    await database.initialize()
    result = await database.add_article({
        "title":"Reconnect Test",
        "url":"https://test.com",
        "category":"tech",
        "language":"en",
        "country":"us",
        "summary":"Test",
        "sentiment":1,
        "publishedAt":"2024-01-01T00:00:00Z",
    })
    assert result == "saved"
    await database.conn.close()

@pytest.mark.asyncio
async def test_initialize_skips_when_alive():
    database = Database(":memory:")
    await database.initialize()
    original_conn = database.conn
    await database.initialize()
    assert database.conn is original_conn
    await database.conn.close()