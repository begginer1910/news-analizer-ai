import logging 
import os
import sys

def setup_logging():
    env = os.getenv("APP_ENV", "development")
    if env == "development":
        level = logging.DEBUG
        handlers = [logging.StreamHandler(sys.stdout)]
    elif env == "testing":
        level = logging.WARNING
        handlers = [logging.FileHandler('test.log')]
    else:
        level = logging.INFO
        handlers = [logging.FileHandler('app.log'), logging.StreamHandler(sys.stdout)]
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=handlers,
        force=True
    )