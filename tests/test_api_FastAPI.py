import pytest
import httpx
from app.api.app import create_app
from app.api.dependencies import get_db, get_helper, get_service
from unittest.mock import AsyncMock, MagicMock
from app.auxiliary_functions import Auxiliary
from app.exceptions import NewsAPIError

mock_config = MagicMock()
mock_config.DB_PATH = ":memory:"
mock_database = MagicMock()
mock_database.get_articles = AsyncMock(return_value=[])
mock_database._fetch_scheduler_config_row = AsyncMock(return_value=("general", "en", "us", 24))
mock_database._update_scheduler_config_row = AsyncMock()
mock_service = MagicMock()
mock_service.start = AsyncMock(return_value=[])

@pytest.fixture
async def client():
    app = create_app(config=mock_config)
    app.dependency_overrides[get_helper] = lambda: Auxiliary()
    app.dependency_overrides[get_db] = lambda : mock_database
    app.dependency_overrides[get_service] = lambda: mock_service
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as c:
        yield c

async def test_get_api_categories(client):
    response =  await client.get("/api/categories")
    assert response.status_code == 200
    assert response.json() == Auxiliary().validcategories

async def test_get_api_languages(client):
    response = await client.get("/api/languages")
    assert response.status_code == 200
    assert response.json() == Auxiliary().avaible_languages

async def test_get_api_countries(client):
    response = await client.get("/api/countries")
    assert response.status_code == 200
    assert response.json() == Auxiliary().countries

async def test_get_api_articles(client):
    response = await client.get("/api/articles")
    assert response.status_code == 200
    assert response.json() == []

async def test_post_api_news_fetch(client):
    response = await client.post("/api/news/fetch", json={
        "category": "general",
        "language": "en",
        "country": "us"
    })
    assert response.status_code == 200
    assert response.json() == []
    mock_service.start.assert_awaited_once_with("general", "en", "us")

async def test_post_api_news_fetch_returns_502_when_newsapi_fails(client):
    original_start = mock_service.start
    mock_service.start = AsyncMock(side_effect=NewsAPIError("NewsAPI request failed: HTTPStatusError"))
    try:
        response = await client.post("/api/news/fetch", json={
            "category": "general",
            "language": "en",
            "country": "us"
        })
        assert response.status_code == 502
        assert response.json() == {"detail": "Upstream news service unavailable, try again later."}
        mock_service.start.assert_awaited_once_with("general", "en", "us")
    finally:
        mock_service.start = original_start

async def test_get_api_export(client):
    mock_database.get_articles = AsyncMock(return_value=[{
        "id": 1,
        "title": "Test Article",
        "url": "https://test.com",
        "category": "general",
        "language": "en",
        "country": "us",
        "summary": "Test summary",
        "sentiment": 1,
        "publishedAt": "2024-01-01T00:00:00Z",
    }])
    response = await client.get("/api/export/csv")
    assert response.status_code == 200
    assert "text/csv" in response.headers["content-type"]
    assert response.headers["content-disposition"] == "attachment; filename=articles.csv"
    expected = (
        "id,title,url,category,language,country,summary,sentiment,publishedAt\r\n"
        "1,Test Article,https://test.com,general,en,us,Test summary,1,2024-01-01T00:00:00Z\r\n"
    )
    assert response.text == expected
    mock_database.get_articles.assert_awaited_once_with(category=None, limit=20)

async def test_export_csv_with_category(client):
    mock_database.get_articles = AsyncMock(return_value=[{
        "id": 1,
        "title": "Tech News",
        "url": "https://test.com",
        "category": "technology",
        "language": "en",
        "country": "us",
        "summary": "Summary",
        "sentiment": 1,
        "publishedAt": "2024-01-01T00:00:00Z",
    }])
    response = await client.get("/api/export/csv?category=technology&limit=5")

    assert response.status_code == 200
    mock_database.get_articles.assert_awaited_once_with(category="technology", limit=5)

async def test_get_api_scheduler_config(client):
    response = await client.get("/api/scheduler/config")
    assert response.status_code == 200
    assert response.json() == {
        "category": "general",
        "language": "en",
        "country": "us",
        "interval_h": 24,
    }

async def test_put_api_scheduler_config(client):
    mock_database._update_scheduler_config_row = AsyncMock()
    mock_database._fetch_scheduler_config_row = AsyncMock(return_value=("technology", "pl", "pl", 12))
    response = await client.put("/api/scheduler/config", json={
        "category": "technology",
        "language": "pl",
        "country": "pl",
        "interval_h": 12,
    })
    assert response.status_code == 200
    assert response.json() == {
        "category": "technology",
        "language": "pl",
        "country": "pl",
        "interval_h": 12,
    }
    mock_database._update_scheduler_config_row.assert_awaited_once_with("technology", "pl", "pl", 12)

async def test_put_api_scheduler_config_interval_not_allowed(client):
    mock_database._update_scheduler_config_row = AsyncMock()
    response = await client.put("/api/scheduler/config", json={
        "category": "general",
        "language": "en",
        "country": "us",
        "interval_h": 8,
    })
    assert response.status_code == 422
    mock_database._update_scheduler_config_row.assert_not_awaited()

async def test_put_api_scheduler_config_missing_field(client):
    response = await client.put("/api/scheduler/config", json={
        "category": "general",
        "language": "en",
        "country": "us",
    })
    assert response.status_code == 422
