import asyncio
from auxiliary_functions import Auxiliary
from news_service import AnalizeNews

class Main:
    def __init__(self):
        self.helper = Auxiliary()
        self.analize = AnalizeNews()
    async def valid_data(self):
        while True:
            category = await asyncio.to_thread(self.helper.text, "Enter a category")
            category = self.helper.validate_category(category)
            if category:break
            print("Invalid category")
        while True:
            language = await asyncio.to_thread(self.helper.text,"Enter a language")
            language = self.helper.validate_language(language)
            if language:break
            print("Invalid language")
        while True:
            country = await asyncio.to_thread(self.helper.text,"Enter a country")
            country = self.helper.validate_country(country)
            if country:break
            print("Invalid country")
        return category, language, country
    async def summation(self):
        category, language, country = await self.valid_data()
        results = await self.analize.start(category, language, country)
        if not results:
            print("Article not found")
        for r in results:
            print(f"{r['status']}: {r['title']}")


if __name__ == "__main__":
    try:
        asyncio.run(Main().summation())
    except ValueError as e:
        print(f"Error: {e}")
        exit(1)