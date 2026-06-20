from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ConversationHandler
from news_service import AnalizeNews
from auxiliary_functions import Auxiliary
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
    def run(self):
        self.app.run_polling()
    async def cancel(self,update: Update, context):
        await update.message.reply_text("canceled")
        return ConversationHandler.END
    async def start(self, update: Update, context):
        await update.message.reply_text(
            "Hello! Please enter a news category:\n"
            f"{','.join(self.helper.validcategories)}"
        )
        return CATEGORY

    async def category_handler(self,update:Update, context):
        text = update.message.text.lower().strip()
        valid = self.helper.validate_category(text)
        if not valid:
            await update.message.reply_text("Invalid category, please try again")
            return CATEGORY
        context.user_data["category"] = valid
        await update.message.reply_text(
            "Please enter your language:\n" + ",".join(self.helper.avaible_languages.keys())
        )
        return LANGUAGE
    async def language_handler(self, update: Update, context):
        text = update.message.text.lower().strip()
        valid = self.helper.validate_language(text)
        if not valid:
            await update.message.reply_text("Invalid language, please try again")
            return LANGUAGE
        context.user_data["language"] = valid
        await update.message.reply_text(
            "Please enter your country:\n" +",".join(self.helper.countries.keys())
        )
        return COUNTRY
    async def country_handler(self, update: Update, context):
        text = update.message.text.lower().strip()
        valid = self.helper.validate_country(text)
        if not valid:
            await update.message.reply_text("Invalid country, please try again")
            return COUNTRY
        context.user_data["country"] = valid
        category = context.user_data["category"]
        language = context.user_data["language"]
        country = valid
        try:
            results = await self.analyze.start(category, language, country)
            if not results:
                await update.message.reply_text("Article not found")
            else:
                for r in results:
                    await update.message.reply_text(f"{r['status']}: {r['title']}")
        except Exception as e:
            await update.message.reply_text(f"Error: {e}")
        return ConversationHandler.END



