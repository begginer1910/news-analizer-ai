import uvicorn
from fastapi import FastAPI
from app.services.news_service import AnalizeNews
from app.auxiliary_functions import Auxiliary
from app.database import Database
from app.config import Config
from contextlib import asynccontextmanager
from .dependencies import init_deps
from .routes import router
import asyncio
from app.scheduler.scheduler import start_scheduler

def create_app(config=None):
    conf = config or Config()
    data = Database(conf.DB_PATH)
    service = AnalizeNews()
    helper = Auxiliary()
    init_deps(data, service, helper)

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        await data.initialize()
        asyncio.create_task(start_scheduler(data))
        yield
        await data.conn.close()
    app = FastAPI(lifespan=lifespan)
    app.include_router(router)
    return app
if __name__ == "__main__":
    uvicorn.run("app.api.app:create_app", factory=True, reload=True)