from scheduler_config_service import SchedulerConfigService
from logging_config import setup_logging
setup_logging()
import asyncio
import logging
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from .jobs import run_news_job
from database import Database

logger = logging.getLogger(__name__)

async def start_scheduler(db:Database):
    scheduler = AsyncIOScheduler()
    cfg_service = SchedulerConfigService(db)
    async def job():
        cfg = await cfg_service.get()
        logger.info("Starting new job: %s/%s/%s (interval=%sh)",
                    cfg["category"], cfg["language"], cfg["country"], cfg["interval_h"])
        await run_news_job(**cfg)
    scheduler.add_job(
        job,
        trigger="interval",
        hours=24,
        id="news_job",
        replace_existing=True
    )
    scheduler.start()
    logger.info("Scheduler started")
    try:
        await asyncio.Future()
    except (KeyboardInterrupt, SystemExit):
        logger.info("Stopping scheduler")
        scheduler.shutdown()

if __name__ == "__main__":
    asyncio.run(start_scheduler())


