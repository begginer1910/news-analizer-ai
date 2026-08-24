import asyncio
import logging
from app.logging_config import setup_logging
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from .jobs import run_news_job
from .scheduler_config_service import SchedulerConfigService
from app.database import Database
from app.services.news_service import AnalizeNews

setup_logging()

logger = logging.getLogger(__name__)

async def create_scheduler(cfg_service: SchedulerConfigService, service:AnalizeNews) -> AsyncIOScheduler:
    initial_config = await cfg_service.get()
    scheduled_interval = initial_config["interval_h"]
    scheduler = AsyncIOScheduler()

    async def job():
        nonlocal scheduled_interval
        current = await cfg_service.get()
        if scheduled_interval != current["interval_h"]:
            scheduler.reschedule_job("news_job", trigger="interval", hours=current["interval_h"])
            scheduled_interval = current["interval_h"]
        logger.info("Starting new job: %s/%s/%s (interval=%sh)",
                    current["category"], current["language"], current["country"], current["interval_h"])
        await run_news_job(current["category"], current["language"], current["country"], service=service)

    scheduler.add_job(
        job,
        trigger="interval",
        hours=initial_config["interval_h"],
        id="news_job",
        replace_existing=True,
    )
    return scheduler

async def start_scheduler(db: Database, service:AnalizeNews):
    scheduler = await create_scheduler(SchedulerConfigService(db), service)
    scheduler.start()
    logger.info("Scheduler started")
    try:
        await asyncio.Future()
    except asyncio.CancelledError:
        logger.info("Stopping scheduler")
        scheduler.shutdown(wait=False)
        raise 
