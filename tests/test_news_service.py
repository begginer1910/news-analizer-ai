import pytest
from unittest.mock import AsyncMock
from app.services.news_service import AnalizeNews
from app.exceptions import AIServiceError


def create_service(monkeypatch):
    monkeypatch.setenv("NEWS_API_KEY", "test_news")
    monkeypatch.setenv("GROQ_API_KEY", "test_groq")
    monkeypatch.setenv("TELEGRAM_API_KEY", "test_telegram")
    return AnalizeNews()


@pytest.mark.asyncio
async def test_start_no_articles(monkeypatch):
    service = create_service(monkeypatch)
    service.data.initialize = AsyncMock()
    service.news_client.get_news = AsyncMock(return_value=[])

    results = await service.start("general", "en", "us")

    assert results == []
    service.data.initialize.assert_awaited_once()
    service.news_client.get_news.assert_awaited_once_with("general", "en", "us")


@pytest.mark.asyncio
async def test_start_one_article_saved(monkeypatch):
    service = create_service(monkeypatch)
    service.data.initialize = AsyncMock()
    service.news_client.get_news = AsyncMock(return_value=[{
        "title": "Test Title",
        "description": "Test Description",
        "url": "https://test.com",
        "publishedAt": "2024-01-01T00:00:00Z",
    }])
    service.ai.summarize = AsyncMock(return_value={
        "summary": "Test summary",
        "sentiment": 1,
    })
    service.data.add_article = AsyncMock(return_value="saved")

    results = await service.start("business", "pl", "pl")

    assert len(results) == 1
    assert results[0]["title"] == "Test Title"
    assert results[0]["summary"] == "Test summary"
    assert results[0]["sentiment"] == 1
    assert results[0]["status"] == "saved"


@pytest.mark.asyncio
async def test_start_one_article_duplicated(monkeypatch):
    service = create_service(monkeypatch)
    service.data.initialize = AsyncMock()
    service.news_client.get_news = AsyncMock(return_value=[{
        "title": "Test",
        "description": "Desc",
        "url": "https://test.com",
        "publishedAt": "2024-01-01",
    }])
    service.ai.summarize = AsyncMock(return_value={
        "summary": "Summary",
        "sentiment": 0,
    })
    service.data.add_article = AsyncMock(return_value="duplicated")

    results = await service.start("general", "en", "us")

    assert results[0]["status"] == "duplicated"


@pytest.mark.asyncio
async def test_start_multiple_articles(monkeypatch):
    service = create_service(monkeypatch)
    service.data.initialize = AsyncMock()
    service.news_client.get_news = AsyncMock(return_value=[
        {"title": "A", "description": "Desc A", "url": "https://a.com", "publishedAt": "2024-01-01"},
        {"title": "B", "description": "Desc B", "url": "https://b.com", "publishedAt": "2024-01-02"},
    ])
    service.ai.summarize = AsyncMock(return_value={"summary": "S", "sentiment": 1})
    service.data.add_article = AsyncMock(return_value="saved")

    results = await service.start("general", "en", "us")

    assert len(results) == 2
    assert results[0]["title"] == "A"
    assert results[1]["title"] == "B"


@pytest.mark.asyncio
async def test_proces_article_ai_error(monkeypatch):
    service = create_service(monkeypatch)
    service.ai.summarize = AsyncMock(side_effect=AIServiceError("AI failed"))
    service.data.add_article = AsyncMock()

    article = {
        "title": "Test",
        "description": "Desc",
        "url": "https://test.com",
        "publishedAt": "2024-01-01",
    }
    result = await service.proces_article(article, "general", "en", "us")

    assert result["title"] == "Test"
    assert result["status"] == "error"
    assert result["error"] == "The message could not be processed. Please try again later."
    service.data.add_article.assert_not_awaited()


@pytest.mark.asyncio
async def test_proces_article_passes_correct_data_to_database(monkeypatch):
    service = create_service(monkeypatch)
    service.ai.summarize = AsyncMock(return_value={"summary": "Sum", "sentiment": 1})
    service.data.add_article = AsyncMock(return_value="saved")

    article = {
        "title": "Title",
        "description": "Desc",
        "url": "https://url.com",
        "publishedAt": "2024-01-01",
    }
    await service.proces_article(article, "tech", "en", "us")

    service.data.add_article.assert_awaited_once_with({
        "title": "Title",
        "url": "https://url.com",
        "category": "tech",
        "language": "en",
        "country": "us",
        "summary": "Sum",
        "sentiment": 1,
        "publishedAt": "2024-01-01",
    })