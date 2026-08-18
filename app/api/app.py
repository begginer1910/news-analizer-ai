import uvicorn
from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from app.services.news_service import AnalizeNews
from app.auxiliary_functions import Auxiliary
from app.database import Database
from app.config import Config
from contextlib import asynccontextmanager
from .dependencies import init_deps
from .routes import router
import asyncio
from app.scheduler.scheduler import start_scheduler
import os

def create_app(config=None):
    conf = config or Config(require_telegram=False)
    data = Database(conf.DB_PATH)
    service = AnalizeNews(config=conf)
    helper = Auxiliary()
    init_deps(data, service, helper)

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        await data.initialize()
        task = asyncio.create_task(start_scheduler(data, service))
        yield
        task.cancel()
        try:
            await task
        except asyncio.CancelledError:
            pass
        await data.conn.close()
        data.conn = None
    app = FastAPI(lifespan=lifespan)
    app.include_router(router)

    static_dir = os.path.join(os.path.dirname(__file__), "static", "frontend")
    app.mount("/frontend", StaticFiles(directory=static_dir, html=True), name="frontend")

    @app.get("/")
    async def root():
        return RedirectResponse(url="/frontend/index.html")

    return app
if __name__ == "__main__":
    reload = os.getenv("APP_ENV", "production") == "development"
    uvicorn.run("app.api.app:create_app", factory=True, reload=reload)