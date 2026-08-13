import pytest
from app.config import Config, ALLOWED_INTERVALS_H

def test_allowed_intervals_h_constant():
    assert ALLOWED_INTERVALS_H == (12, 24)

def test_config_creates_succesfully(monkeypatch):
    monkeypatch.setenv("NEWS_API_KEY", "test_news")
    monkeypatch.setenv("GROQ_API_KEY", "test_groq")
    monkeypatch.setenv("TELEGRAM_API_KEY", "test_telegram")
    config = Config()
    assert config.NEWS_API_KEY == "test_news"
    assert config.GROQ_API_KEY == "test_groq"
    assert config.TELEGRAM_API_KEY == "test_telegram"
    assert config.DB_PATH == "news.db"

def test_db_path_custom_value(monkeypatch):
    monkeypatch.setenv("NEWS_API_KEY", "test_news")
    monkeypatch.setenv("GROQ_API_KEY", "test_groq")
    monkeypatch.setenv("TELEGRAM_API_KEY", "test_telegram")
    monkeypatch.setenv("DB_PATH", "custom.db")
    config = Config()
    assert config.DB_PATH == "custom.db"

def test_missing_news_api_key(monkeypatch):
    monkeypatch.delenv("NEWS_API_KEY", raising=False)
    monkeypatch.setenv("GROQ_API_KEY", "test_groq")
    monkeypatch.setenv("TELEGRAM_API_KEY", "test_telegram")
    with pytest.raises(ValueError) as exc_info:
        Config()
    assert str(exc_info.value) == "Missing API keys in .env file: NEWS_API_KEY"
        
def test_missing_groq_api_key(monkeypatch):
    monkeypatch.setenv("NEWS_API_KEY", "test_news")
    monkeypatch.delenv("GROQ_API_KEY", raising=False)
    monkeypatch.setenv("TELEGRAM_API_KEY", "test_telegram")
    with pytest.raises(ValueError) as exc_info:
        Config()
    assert str(exc_info.value) == "Missing API keys in .env file: GROQ_API_KEY"


def test_missing_telegram_api_key(monkeypatch):
    monkeypatch.setenv("NEWS_API_KEY", "test_news")
    monkeypatch.setenv("GROQ_API_KEY", "test_groq")
    monkeypatch.delenv("TELEGRAM_API_KEY", raising=False)
    with pytest.raises(ValueError) as exc_info:
        Config()
    assert str(exc_info.value) == "Missing API keys in .env file: TELEGRAM_API_KEY"

def test_multiple_missing_keys(monkeypatch):
    monkeypatch.delenv("NEWS_API_KEY", raising=False)
    monkeypatch.delenv("GROQ_API_KEY", raising=False)
    monkeypatch.delenv("TELEGRAM_API_KEY", raising=False)
    with pytest.raises(ValueError) as exc_info:
        Config()
    assert str(exc_info.value) == "Missing API keys in .env file: NEWS_API_KEY, GROQ_API_KEY, TELEGRAM_API_KEY"

