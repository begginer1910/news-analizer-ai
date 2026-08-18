import pytest
from unittest.mock import AsyncMock, MagicMock
import app.scheduler.jobs as jobs

@pytest.mark.asyncio
async def test_run_news_job_calls_start_and_returns_results(monkeypatch):
    fake_analyze = MagicMock()
    fake_analyze.start = AsyncMock(return_value=[{"status": "saved"}])
    monkeypatch.setattr(jobs, "AnalizeNews", lambda: fake_analyze)
    result = await jobs.run_news_job("business", "pl", "pl", service=fake_analyze)
    fake_analyze.start.assert_awaited_once_with(category="business", language="pl", country="pl")
    assert result == [{"status": "saved"}]

@pytest.mark.asyncio
async def test_run_news_job_returns_empty_when_no_articles(monkeypatch):
    fake_analyze = MagicMock()
    fake_analyze.start = AsyncMock(return_value=[])
    monkeypatch.setattr(jobs, "AnalizeNews", lambda: fake_analyze)
    result = await jobs.run_news_job("general", "en", "us", service=fake_analyze)
    assert result == []
