from config import Config
from auxiliary_functions import Auxiliary
from news_service import AnalizeNews
from telegram_bot import TelegramBot

class MainBot:
    def __init__(self):
        self.conf = Config()
        self.helper = Auxiliary()
        self.analize = AnalizeNews()
        self.telegram_bot = TelegramBot(self.conf.TELEGRAM_API_KEY,self.analize,self.helper )
    def run_bot(self):
        try:
            self.telegram_bot.run()
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    try:
        MainBot().run_bot()
    except ValueError as e:
        print(f"Error: {e}")
        exit(1)