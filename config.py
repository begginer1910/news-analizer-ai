from dotenv import load_dotenv
import os
load_dotenv()

class Config:
    NEWS_API_KEY:str
    GROQ_API_KEY:str
    def __init__(self):
        self.NEWS_API_KEY = os.getenv("NEWS_API_KEY")
        self.GROQ_API_KEY = os.getenv("GROQ_API_KEY")
        self.DB_PATH = os.getenv("DB_PATH", "news.db")
        self.TELEGRAM_API_KEY = os.getenv("TELEGRAM_API_KEY")
        self.API_HOST = os.getenv("API_HOST", "0.0.0.0")
        self.API_PORT = int(os.getenv("API_PORT", "8000"))
        self.JOB_CATEGORY = os.getenv("JOB_CATEGORY", "general")
        self.JOB_LANGUAGE = os.getenv("JOB_LANGUAGE", "en")
        self.JOB_COUNTRY = os.getenv("JOB_COUNTRY", "us")
        self.JOB_INTERVAL_H = int(os.getenv("JOB_INTERVAL_H", "24"))
        self._validate()
    def _validate(self):
        missing = []
        if not self.NEWS_API_KEY:
            missing.append('NEWS_API_KEY')
        if not self.GROQ_API_KEY:
            missing.append('GROQ_API_KEY')
        if not self.TELEGRAM_API_KEY:
            missing.append('TELEGRAM_API_KEY')
        if missing:
            raise ValueError(
                f'Missing API keys in .env file: {", ".join(missing)}'
            )