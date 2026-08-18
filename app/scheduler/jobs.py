import logging
from app.services.news_service import AnalizeNews

logger = logging.getLogger(__name__)

async def run_news_job(category, language, country, service:AnalizeNews):
    logger.info("Starting the news task: %s/%s/%s", category, language, country)
    results = await service.start(
        category=category,
        language=language,
        country=country,
    )
    logger.info("Task finished = got %s articles", len(results))
    return results
