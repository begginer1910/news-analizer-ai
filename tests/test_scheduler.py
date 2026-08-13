import pytest
from unittest.mock import AsyncMock, MagicMock
import app.scheduler.scheduler as sched

@pytest.mark.asyncio
async def test_create_scheduler_uses_interval_from_config():
    cfg_service = MagicMock()
    cfg_service.get = AsyncMock(return_value={"category": "general", "language": "en", "country": "us", "interval_h": 12})
    scheduler = await sched.create_scheduler(cfg_service)
    job = scheduler.get_job("news_job")
    assert job is not None
    assert job.trigger.interval.seconds == 12 * 3600

@pytest.mark.asyncio
async def test_job_uses_fresh_config_and_calls_run_news_job(monkeypatch):
    cfg_service = MagicMock()
    cfg_service.get = AsyncMock(return_value={"category": "technology", "language": "pl", "country": "pl", "interval_h": 12})
    scheduler = await sched.create_scheduler(cfg_service)
    mock_run = AsyncMock(return_value=[{"status": "saved"}])
    monkeypatch.setattr(sched, "run_news_job", mock_run)
    job = scheduler.get_job("news_job")
    await job.func()
    mock_run.assert_awaited_once_with("technology", "pl", "pl")

class FakeScheduler:
    def __init__(self):
        self.started = False
        self.shutdown_called = False

    def start(self):
        self.started = True

    def shutdown(self):
        self.shutdown_called = True

@pytest.mark.asyncio
async def test_start_scheduler_starts_and_shuts_down(monkeypatch):
    fake = FakeScheduler()

    async def fake_create(cfg_service):
        return fake

    monkeypatch.setattr(sched, "create_scheduler", fake_create)

    async def _raise_keyboard_interrupt():
        raise KeyboardInterrupt

    monkeypatch.setattr(sched.asyncio, "Future", _raise_keyboard_interrupt)
    await sched.start_scheduler(MagicMock())
    assert fake.started is True
    assert fake.shutdown_called is True
