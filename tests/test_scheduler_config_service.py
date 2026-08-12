import pytest
from unittest.mock import AsyncMock, MagicMock
from Scheduler.scheduler_config_service import SchedulerConfigService

@pytest.mark.asyncio
async def test_get_returns_mapped_dict():
    db = MagicMock()
    db._fetch_scheduler_config_row = AsyncMock(return_value=("general", "en", "us", 24))
    svc = SchedulerConfigService(db)
    result = await svc.get()
    assert result == {"category": "general", "language": "en", "country": "us", "interval_h": 24}

@pytest.mark.asyncio
async def test_get_raises_when_no_row():
    db = MagicMock()
    db._fetch_scheduler_config_row = AsyncMock(return_value=None)
    svc = SchedulerConfigService(db)
    with pytest.raises(RuntimeError):
        await svc.get()

@pytest.mark.asyncio
async def test_update_calls_db_and_returns_new_config():
    db = MagicMock()
    db._fetch_scheduler_config_row = AsyncMock(return_value=("technology", "pl", "pl", 12))
    db._update_scheduler_config_row = AsyncMock()
    svc = SchedulerConfigService(db)
    result = await svc.update(category="technology", language="pl", country="pl", interval_h=12)
    db._update_scheduler_config_row.assert_awaited_once_with("technology", "pl", "pl", 12)
    assert result == {"category": "technology", "language": "pl", "country": "pl", "interval_h": 12}

@pytest.mark.asyncio
async def test_update_rejects_disallowed_interval():
    db = MagicMock()
    db._update_scheduler_config_row = AsyncMock()
    svc = SchedulerConfigService(db)
    with pytest.raises(ValueError):
        await svc.update(category="general", language="en", country="us", interval_h=8)
    db._update_scheduler_config_row.assert_not_awaited()
