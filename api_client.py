from exceptions import NewsAPIError
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
        except httpx.HTTPStatusError as exc:
                logger.error(f"NewsAPI HTTP error {exc.response.status_code}: {exc.response.text}")
                raise NewsAPIError(f"NewsAPI error {exc.response.status_code}") from exc
        except httpx.RequestError as exc:
                logger.error(f"NewsAPI request failed: {exc}")
                raise NewsAPIError(f"Network error: {str(exc)}") from exc
        except ValueError as exc:
                logger.error(f"Invalid JSON from NewsAPI: {exc}")
                raise NewsAPIError("Invalid response format from NewsAPI") from exc
        articles = data.get("articles")
        if not isinstance(articles,list):
              logger.error("expected 'articles' list in NewsAPI reponse")
              raise NewsAPIError("Invalid response structure from NewsAPI")
        return articles

