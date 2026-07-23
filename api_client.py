import httpx
import logging
logger = logging.getLogger(__name__)
class NewsApiClient:
    def __init__(self, api_key:str):
        self.api_key = api_key
    async def get_news(self,selected_category,selected_language,selected_country):
        self.url = "https://newsapi.org/v2/top-headlines"
        params = {
            "apiKey" : self.api_key,
            "category" : selected_category,
            "language" : selected_language,
            "country" : selected_country,
            "pageSize" : 5
        }
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(self.url, params=params)
                response.raise_for_status()
                data = response.json()
                articles = data.get("articles")
                return articles if isinstance(articles, list) else []
        except Exception as e:
            logger.critical(f"Error with API : {e}")
            return []


