import logging
from news_service import AnalizeNews
from config import Config

logger = logging.getLogger(__name__)

async def run_news_job():
    config = Config()
    logger.info("Starting the news task: %s/%s/%s", config.JOB_CATEGORY, config.JOB_LANGUAGE, config.JOB_COUNTRY)
    analize = AnalizeNews()
    results = await analize.start(
        category=config.JOB_CATEGORY,
        language=config.JOB_LANGUAGE,
        country=config.JOB_COUNTRY
    )
    logger.info("Task finished = get %s articles", len(results))
    return results