from app.logging_config import setup_logging
setup_logging()
from app.config import Config
from app.auxiliary_functions import Auxiliary
from app.services.news_service import AnalizeNews
from app.bots.telegram_bot import TelegramBot
import asyncio
import logging
logger = logging.getLogger(__name__)

class MainBot:
    def __init__(self):
        self.conf = Config()
        self.helper = Auxiliary()
        self.analize = AnalizeNews()
        self.telegram_bot = TelegramBot(self.conf.TELEGRAM_API_KEY,self.analize,self.helper )
    
    async def run_bot(self):
        try:
            await self.telegram_bot.run()   
        except KeyboardInterrupt:
            pass
        finally:
            await self.telegram_bot.stop()
def main():
    try:
        asyncio.run(MainBot().run_bot())
    except ValueError as e:
        logging.error(f"Error: {e}")
        exit(1)
if __name__ == "__main__":
    main()