import pytest
from unittest.mock import MagicMock, AsyncMock, call
from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler
from telegram_bot import TelegramBot, CATEGORY, LANGUAGE, COUNTRY
from auxiliary_functions import Auxiliary

@pytest.mark.asyncio
async def test_start_handler():
    update = MagicMock(spec=Update)
    update.message.reply_text = AsyncMock()
    context = MagicMock()
    bot = TelegramBot("fake-token", MagicMock(), Auxiliary())
    result = await bot.start(update,context)
    update.message.reply_text.assert_awaited_once()
    assert result == CATEGORY

@pytest.mark.asyncio
@pytest.mark.parametrize("input_text,expected_state",[
    ("technology", LANGUAGE),
    ("invalid", CATEGORY),
])
async def test_category_handler(input_text,expected_state):
    update = MagicMock(spec=Update)
    update.message.text = input_text
    update.message.reply_text = AsyncMock()
    context = MagicMock()
    context.user_data = {}
    bot = TelegramBot("fake-token", MagicMock(), Auxiliary())
    result = await bot.category_handler(update,context)
    update.message.reply_text.assert_awaited_once()
    assert result == expected_state
    if expected_state == LANGUAGE:
        assert context.user_data["category"] == "technology"

@pytest.mark.asyncio
@pytest.mark.parametrize("input_text,expected_state",[
    ("english", COUNTRY),
    ("invalid", LANGUAGE),
])
async def test_language_handler(input_text,expected_state):
    update = MagicMock(spec=Update)
    update.message.text = input_text
    update.message.reply_text = AsyncMock()
    context = MagicMock()
    context.user_data = {}
    bot = TelegramBot("fake-token", MagicMock(), Auxiliary())
    result = await bot.language_handler(update,context)
    update.message.reply_text.assert_awaited_once()
    assert result == expected_state
    if expected_state == COUNTRY:
        assert context.user_data["language"] == "en"

@pytest.mark.asyncio
@pytest.mark.parametrize("input_text",[
    "invalid", "", "xyz"
])
async def test_country_handler_invalid(input_text):
    update = MagicMock(spec=Update)
    update.message.text = input_text
    update.message.reply_text = AsyncMock()
    context = MagicMock()
    context.user_data = {}
    bot = TelegramBot("fake-token", MagicMock(), Auxiliary())
    result = await bot.country_handler(update,context)
    update.message.reply_text.assert_called_once_with("Invalid country, please try again")
    assert result == COUNTRY

@pytest.mark.asyncio
async def test_country_handler_empty_result():
    analyze_mock = AsyncMock()
    analyze_mock.start.return_value = []
    update = MagicMock(spec=Update)
    update.message.text = "us"
    update.message.reply_text = AsyncMock()
    context = MagicMock()
    context.user_data = {"category": "technology","language": "en" }
    bot = TelegramBot("fake-token",analyze_mock, Auxiliary())
    result = await bot.country_handler(update,context)
    update.message.reply_text.assert_called_once_with("Article not found")
    assert result == ConversationHandler.END

@pytest.mark.asyncio
async def test_coutry_handler_result():
    analyze_mock = AsyncMock()
    analyze_mock.start.return_value = [
        {"title": "News", "summary": "sum", "sentiment": 1, "status": "saved"},
        {"title": "News2", "summary": "sum2", "sentiment": 0, "status": "saved"}
    ]
    update = MagicMock(spec=Update)
    update.message.text = "us"
    update.message.reply_text = AsyncMock()
    context = MagicMock()
    context.user_data = {"category": "technology","language": "en" }
    bot = TelegramBot("fake-token", analyze_mock, Auxiliary())
    result = await bot.country_handler(update,context)
    update.message.reply_text.assert_has_awaits([
        call("saved: News"),
        call("saved: News2"),
    ])
    assert result == ConversationHandler.END

@pytest.mark.asyncio
async def test_country_handler_error():
    analyze_mock = AsyncMock()
    analyze_mock.start.side_effect = Exception("API fail")
    update = MagicMock(spec=Update)
    update.message.text = "us"
    update.message.reply_text = AsyncMock()
    context = MagicMock()
    context.user_data = {"category": "technology", "language": "en"}
    bot = TelegramBot("fake-token", analyze_mock, Auxiliary())
    result = await bot.country_handler(update, context)
    update.message.reply_text.assert_awaited_once_with("Error: API fail")
    assert result == ConversationHandler.END