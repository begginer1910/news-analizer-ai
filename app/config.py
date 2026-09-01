import os

ALLOWED_INTERVALS_H = (12, 24)

class Config:
    NEWS_API_KEY:str
    GROQ_API_KEY:str
    def __init__(self, require_telegram: bool = True):
        self.NEWS_API_KEY = os.getenv("NEWS_API_KEY")
        self.GROQ_API_KEY = os.getenv("GROQ_API_KEY")
        self.DB_PATH = os.getenv("DB_PATH", "news.db")
        self.TELEGRAM_API_KEY = os.getenv("TELEGRAM_API_KEY")
        self.API_HOST = os.getenv("API_HOST", "0.0.0.0")
        self.API_PORT = int(os.getenv("API_PORT", "8000"))
        self._validate(require_telegram)
    def _validate(self, require_telegram: bool):
        missing = []
        if not self.NEWS_API_KEY:
            missing.append('NEWS_API_KEY')
        if not self.GROQ_API_KEY:
            missing.append('GROQ_API_KEY')
        if require_telegram and not self.TELEGRAM_API_KEY:
            missing.append('TELEGRAM_API_KEY')
        if missing:
            raise ValueError(
                f'Missing API keys in .env file: {", ".join(missing)}'
            )