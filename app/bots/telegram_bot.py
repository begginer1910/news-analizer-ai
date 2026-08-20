from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ConversationHandler
from app.services.news_service import AnalizeNews
from app.auxiliary_functions import Auxiliary
import logging
logger = logging.getLogger(__name__)
CATEGORY, LANGUAGE, COUNTRY = range(3)

class TelegramBot:
    def __init__(self, token:str, analyze:AnalizeNews, helper: Auxiliary):
        self.analyze = analyze
        self.helper = helper
        self.app = Application.builder().token(token).build()
        self._register_handlers()
    def _register_handlers(self):
        conv_handler = ConversationHandler(
            entry_points = [CommandHandler("start", self.start)],
            states = {
                CATEGORY: [MessageHandler(filters.TEXT & ~filters.COMMAND, self.category_handler)],
                LANGUAGE: [MessageHandler(filters.TEXT & ~filters.COMMAND, self.language_handler)],
                COUNTRY: [MessageHandler(filters.TEXT & ~filters.COMMAND, self.country_handler)],
            },
            fallbacks = [CommandHandler("cancel", self.cancel)]
        )
        self.app.add_handler(conv_handler)
    async def run(self):
        logger.info("Starting Telegram bot polling")
        await self.app.initialize()
        await self.app.start()
        await self.app.updater.start_polling()
    async def stop(self):
        await self.app.updater.stop()
        await self.app.stop()
        await self.app.shutdown()
    async def cancel(self, update: Update, context):
        await update.message.reply_text("canceled")
        logger.info("User cancelled the conversation")
        return ConversationHandler.END
    async def start(self, update: Update, context):
        await update.message.reply_text(
            "Hello! Please enter a news category:\n"
            f"{','.join(self.helper.validcategories)}"
        )
        logger.info("User started conversation, asking for category")
        return CATEGORY

    async def category_handler(self,update:Update, context):
        text = update.message.text.lower().strip()
        valid = self.helper.validate_category(text)
        if not valid:
            await update.message.reply_text("Invalid category, please try again")
            logger.warning("User entered invalid category: %s", text)
            return CATEGORY
        context.user_data["category"] = valid
        logger.debug("User selected category: %s", valid)
        await update.message.reply_text(
            "Please enter your language:\n" + ",".join(self.helper.avaible_languages.keys())
        )
        return LANGUAGE
    async def language_handler(self, update: Update, context):
        text = update.message.text.lower().strip()
        valid = self.helper.validate_language(text)
        if not valid:
            await update.message.reply_text("Invalid language, please try again")
            logger.warning("User entered invalid language: %s", text)
            return LANGUAGE
        context.user_data["language"] = valid
        logger.debug("User selected language: %s", valid)
        await update.message.reply_text(
            "Please enter your country:\n" +",".join(self.helper.countries.keys())
        )
        return COUNTRY
    async def country_handler(self, update: Update, context):
        text = update.message.text.lower().strip()
        valid = self.helper.validate_country(text)
        if not valid:
            await update.message.reply_text("Invalid country, please try again")
            logger.warning("User entered invalid country: %s", text)
            return COUNTRY
        context.user_data["country"] = valid
        category = context.user_data["category"]
        language = context.user_data["language"]
        country = valid
        try:
            results = await self.analyze.start(category, language, country)
            if not results:
                await update.message.reply_text("No articles were found matching the specified criteria.")
                logger.info("No articles found for category=%s, language=%s, country=%s", 
                           category, language, country)
            else:
                for r in results:
                    if r["status"] == "error":
                        error_msg = r.get("error", "An unexpected error occurred.")    
                        await update.message.reply_text(f"Error: {error_msg}")
                        logger.warning("Article result: %s - %s", r['status'], r['title'])
                    else:
                        await update.message.reply_text(f"{r['status']}: {r['title']}")
                        logger.info("Result: %s – %s", r['status'], r['title'])
        except Exception as e:
            await update.message.reply_text(f"We apologize, an internal error occurred. Please try again later.")
            logger.error("Error processing news request: %s", e, exc_info=True)
        return ConversationHandler.END



