from exceptions import NewsAPIError
import httpx
import logging
logger = logging.getLogger(__name__)
import asyncio
import random
from auxiliary_functions import Auxiliary
class NewsApiClient:
    def __init__(self, api_key:str):
        self.api_key = api_key
        self.helper = Auxiliary()
        self.max_retries = 3
        self.base_delay = 1.0
        self.max_delay = 10.0
    async def _execute_with_retry(self, coro_func):
          for attempt in range(self.max_retries+1):
                try:
                      return await coro_func()
                except Exception as exc:
                      if isinstance(exc, NewsAPIError):
                           raise
                      if not self.helper.is_retryable(exc):
                        raise NewsAPIError(str(exc)) from exc
                      logger.warning(f"Attempt: {attempt + 1}/{self.max_retries + 1}, failed:{exc}")
                      if attempt == self.max_retries:
                          logger.error("All retry attempts exhausted")
                          raise NewsAPIError(str(exc)) from exc
                      delay = min(self.base_delay * (2 ** attempt) + random.uniform(0,1), self.max_delay)
                      await asyncio.sleep(delay)   
    async def get_news(self,selected_category,selected_language,selected_country):
        self.url = "https://newsapi.org/v2/top-headlines"
        params = {
            "apiKey" : self.api_key,
            "category" : selected_category,
            "language" : selected_language,
            "country" : selected_country,
            "pageSize" : 5
        }
        async def _fetch():
            async with httpx.AsyncClient() as client:
                response = await client.get(self.url, params=params)
                response.raise_for_status()
                data = response.json()
                articles = data.get("articles")
                if not isinstance(articles, list):
                    raise NewsAPIError("Invalid response structure from NewsAPI")
                return articles
        return await self._execute_with_retry(_fetch)
            