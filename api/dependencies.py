from database import Database
from news_service import AnalizeNews
from auxiliary_functions import Auxiliary

_database: Database | None = None
_service: AnalizeNews | None = None
_helper: Auxiliary | None = None

def init_deps(database: Database, service: AnalizeNews, helper:Auxiliary):
    global _database, _service, _helper
    _database = database
    _service = service
    _helper = helper

def get_db():
    return _database

def get_service():
    return _service

def get_helper():
    return _helper