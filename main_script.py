from database import Data_base
from api_client import NewsApiClient
from ai_service import Groq_ai
from auxiliary_functions import auxiliary
class main:
    def __init__(self):
        self.news_client = NewsApiClient()
        self.helper = auxiliary()
        self.AI = Groq_ai()
        self.data = Data_base()
    def start(self):
        selected_category = self.helper.text("Please select a category")
        selected_language = self.helper.u_language()
        selected_country = self.helper.text("Please select a country (for example: en, us):")
        articles = self.news_client.get_news(selected_category,selected_language,selected_country)
        if not articles:
            print("Articles not found")
            return
        for art in articles:
            print(f"\nAnalyzing: {art.get('title')}")
        ai_results = self.AI.summarize(
            art.get('title'),
            art.get('description'),
            selected_language,
        )
        data = {
            "title": art.get('title'),
            "url": art.get('url'),
            "category": selected_category,
            "language": selected_language,
            "country": selected_country,
            "summary": ai_results.get('summary'),
            "sentiment": ai_results.get('sentiment'),
            "publishedAt": art.get('publishedAt')
        }
        self.data.add_article(data)
if __name__ == "__main__":
    app = main()
    app.start()
