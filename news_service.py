from database import Database
from api_client import NewsApiClient
from ai_service import Groq_ai
from config import Config

class AnalizeNews:
    def __init__(self):
        conf = Config()
        self.news_client = NewsApiClient(conf.NEWS_API_KEY)
        self.ai = Groq_ai(conf.GROQ_API_KEY)
        self.data = Database(conf.DB_PATH)

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
        except Exception as e:
            return {
                "title": article.get('title', 'unknown'),
                "status": "error",
                "error": str(e),
            }
