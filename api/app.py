from fastapi import FastAPI
from news_service import AnalizeNews
from auxiliary_functions import Auxiliary
from database import Database
from config import Config
from contextlib import asynccontextmanager
from .dependencies import init_deps
from .routes import router

def create_app(config=None):
    conf = config or Config()
    data = Database(conf.DB_PATH)
    service = AnalizeNews()
    helper = Auxiliary()
    init_deps(data, service, helper)

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        await data.initialize()
        yield
        await data.conn.close()
    app = FastAPI(lifespan=lifespan)
    app.include_router(router)
    return app