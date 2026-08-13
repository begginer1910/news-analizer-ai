from app.logging_config import setup_logging
setup_logging()
import asyncio
from app.auxiliary_functions import Auxiliary
from app.services.news_service import AnalizeNews
import logging
logger = logging.getLogger(__name__)

class Main:
    def __init__(self):
        self.helper = Auxiliary()
        self.analize = AnalizeNews()
    async def valid_data(self):
        while True:
            category = await asyncio.to_thread(self.helper.text, "Enter a category")
            category = self.helper.validate_category(category)
            if category:break
            print(f"Invalid category, available:{self.helper.validcategories} ")
            logger.debug(f"User enter invalid category:{category}, should give: {self.helper.validcategories}")
        while True:
            language = await asyncio.to_thread(self.helper.text,"Enter a language")
            language = self.helper.validate_language(language)
            if language:break
            print(f"Invalid language, available: {self.helper.avaible_languages} ")
            logger.debug(f"User enter invalid language: {language}, should give:{self.helper.avaible_languages}")
        while True:
            country = await asyncio.to_thread(self.helper.text,"Enter a country")
            country = self.helper.validate_country(country)
            if country:break
            print("Invalid country, enter full name of country for example: Poland , France")
            logger.debug("User enter invalid country")
        return category, language, country
    async def summation(self):
        category, language, country = await self.valid_data()
        results = await self.analize.start(category, language, country)
        if not results:
            print("Article not found")
            logger.info("No articles found for the specified criteria.")
        else:
            for r in results:
                if r["status"] == "error":
                    print(f"Error: {r.get('error', 'unknown eror')}")
                    logger.warning(f"Article processing error: {r.get('error')}")
                else:
                    print(f"{r['status']}: {r['title']}")
                    logger.info(f"Result: {r['status']} - {r['title']}")

def main():
    try:
        asyncio.run(Main().summation())
    except ValueError as e:
        logging.error(f"Error: {e}")
        exit(1)
if __name__ == "__main__":
    main()