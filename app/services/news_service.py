from app.database import Database
from .news_api_client import NewsApiClient
from .ai_service import Groq_ai
from app.config import Config
from app.exceptions import NewsAPIError, AIServiceError
import logging
logger = logging.getLogger(__name__)

class AnalizeNews:
    def __init__(self, database: Database | None = None, config:Config | None = None):
        conf = config or Config()
        self.news_client = NewsApiClient(conf.NEWS_API_KEY)
        self.ai = Groq_ai(conf.GROQ_API_KEY)
        self.data = database or Database(conf.DB_PATH)

    async def start(self, category, language, country):
        await self.data.initialize()
        articles = await self.news_client.get_news(category, language, country)
        if not articles:
            return []
        results = []
        for art in articles:
            result = await self.proces_article(art, category, language, country)
            results.append(result)
        return results

    async def proces_article(self, article, category, language, country):
        try:
            ai_result = await self.ai.summarize(
                article.get('title'),
                article.get('description'),
                article.get('content'),
                language,
            )
            data = {
                "title": article.get('title'),
                "url": article.get('url'),
                "category": category,
                "language": language,
                "country": country,
                "summary": ai_result.get('summary'),
                "sentiment": ai_result.get('sentiment'),
                "publishedAt": article.get('publishedAt'),
            }
            status = await self.data.add_article(data)
            return {
                "title": data['title'],
                "summary": data['summary'],
                "sentiment": data['sentiment'],
                "status": status,
            }
        except NewsAPIError as e:
            logger.warning("NewsAPI error processed: %s", type(e).__name__)
            return {"title": article.get('title', 'unknown'),
                    "status": "error",
                    "error": "Failed to retrieve messages from the source. Please try again later."                   
                    }
        except AIServiceError as e:
            logger.warning("AI service error processsed: %s", type(e).__name__)
            return {
                "title": article.get('title', 'unknown'),
                "status": "error",
                "error":"The message could not be processed. Please try again later."
            }
        except Exception as e:
            logger.error("Unexpected error processing article: %s", type(e).__name__, exc_info=True)
            return {
                "title": article.get('title', 'unknown'),
                "status": "error",
                "error": "An unexpected error occurred. Please contact the administrator.",
            }
