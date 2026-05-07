from datetime import datetime

import requests
import os
from dotenv import load_dotenv
class NewsApiClient:
    def __init__(self):
        load_dotenv()
        self.api_key = os.getenv("NEWS_API_KEY")
        self.url = "https://newsapi.org/v2/top-headlines"
    def get_news(self,selected_category,selected_language,selected_country):
        params = {
            "apiKey" : self.api_key,
            "category" : selected_category,
            "language" : selected_language,
            "country" : selected_country,
            "pageSize" : 5
        }
        try:
            response = requests.get(self.url, params=params)
            response.raise_for_status()
            return response.json().get('articles', [])
        except Exception as e:
            print(f"Error with API : {e}")
            return []


