import asyncio
import pytest
from unittest.mock import AsyncMock, MagicMock
import app.scheduler.scheduler as sched

@pytest.mark.asyncio
async def test_create_scheduler_uses_interval_from_config():
    cfg_service = MagicMock()
    cfg_service.get = AsyncMock(return_value={"category": "general", "language": "en", "country": "us", "interval_h": 12})
    scheduler = await sched.create_scheduler(cfg_service, service=MagicMock())
    job = scheduler.get_job("news_job")
    assert job is not None
    assert job.trigger.interval.seconds == 12 * 3600

@pytest.mark.asyncio
async def test_job_uses_fresh_config_and_calls_run_news_job(monkeypatch):
    cfg_service = MagicMock()
    cfg_service.get = AsyncMock(return_value={"category": "technology", "language": "pl", "country": "pl", "interval_h": 12})
    fake_service = MagicMock()
    scheduler = await sched.create_scheduler(cfg_service, service=fake_service)
    mock_run = AsyncMock(return_value=[{"status": "saved"}])
    monkeypatch.setattr(sched, "run_news_job", mock_run)
    job = scheduler.get_job("news_job")
    await job.func()
    mock_run.assert_awaited_once_with("technology", "pl", "pl", service=fake_service)

@pytest.mark.asyncio
async def test_job_reschedules_when_interval_changes(monkeypatch):
    cfg_service = MagicMock()
    cfg_service.get = AsyncMock(side_effect=[
        {"category": "general", "language": "en", "country": "us", "interval_h": 12},
        {"category": "general", "language": "en", "country": "us", "interval_h": 24},
    ])
    mock_run = AsyncMock(return_value=[])
    monkeypatch.setattr(sched, "run_news_job", mock_run)
    scheduler = await sched.create_scheduler(cfg_service, service=MagicMock())
    job = scheduler.get_job("news_job")
    await job.func()
    assert scheduler.get_job("news_job").trigger.interval.total_seconds() == 24 * 3600

@pytest.mark.asyncio
async def test_job_reschedules_only_once_for_same_new_interval(monkeypatch):
    def make_config(interval):
        return {"category": "general", "language": "en", "country": "us", "interval_h": interval}

    cfg_service = MagicMock()
    cfg_service.get = AsyncMock(side_effect=[
        make_config(12),
        make_config(24),
        make_config(24),
    ])
    mock_run = AsyncMock(return_value=[])
    monkeypatch.setattr(sched, "run_news_job", mock_run)
    scheduler = await sched.create_scheduler(cfg_service, service=MagicMock())
    real_reschedule = scheduler.reschedule_job
    scheduler.reschedule_job = MagicMock(side_effect=real_reschedule)
    job = scheduler.get_job("news_job")
    await job.func()
    await job.func()
    assert scheduler.reschedule_job.call_count == 1
    assert scheduler.get_job("news_job").trigger.interval.total_seconds() == 24 * 3600

class FakeScheduler:
    def __init__(self):
        self.started = False
        self.shutdown_called = False
        self.shutdown_wait = None

    def start(self):
        self.started = True

    def shutdown(self, wait=True):
        self.shutdown_called = True
        self.shutdown_wait = wait

@pytest.mark.asyncio
async def test_start_scheduler_starts_and_shuts_down(monkeypatch):
    fake = FakeScheduler()

    async def fake_create(cfg_service, service):
        return fake

    monkeypatch.setattr(sched, "create_scheduler", fake_create)

    task = asyncio.create_task(sched.start_scheduler(MagicMock(), service=MagicMock()))
    for _ in range(100):
        if fake.started:
            break
        await asyncio.sleep(0)
    assert fake.started is True

    task.cancel()
    with pytest.raises(asyncio.CancelledError):
        await task

    assert fake.shutdown_called is True
    assert fake.shutdown_wait is False


