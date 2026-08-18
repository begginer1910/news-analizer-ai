import logging 
import os
import sys
from dotenv import load_dotenv
load_dotenv()
def setup_logging():
    env = os.getenv("APP_ENV", "production")
    if env == "development":
        level = logging.DEBUG
        handlers = [logging.StreamHandler(sys.stdout)]
    elif env == "testing":
        level = logging.WARNING
        handlers = [logging.FileHandler('test.log')]
    else:
        level = logging.INFO
        handlers = [logging.StreamHandler(sys.stdout)]
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=handlers,
        force=True
    )
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)
    logging.getLogger("groq").setLevel(logging.WARNING)