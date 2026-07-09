from fastapi import FastAPI
from news_service import AnalizeNews
from auxiliary_functions import Auxiliary
from schemas import FetchRequest, ArticleResponse, FetchResult
from database import Database
from config import Config
from contextlib import asynccontextmanager
import csv
from io import StringIO
from fastapi.responses import StreamingResponse

@asynccontextmanager
async def lifespan(app: FastAPI):
    await data.initialize()
    yield
    await data.conn.close()

conf = Config()
app = FastAPI(lifespan=lifespan)
helper = Auxiliary()
data = Database(conf.DB_PATH)
service = AnalizeNews(database=data)


@app.get("/api/categories", response_model=list[str])
async def get_categories():
    return helper.validcategories

@app.get("/api/languages", response_model=dict[str, str])
async def get_languages():
    return helper.avaible_languages

@app.get("/api/countries", response_model=dict[str,str])
async def get_countries():
    return helper.countries

@app.get("/api/articles", response_model=list[ArticleResponse])
async def get_article():
    return await data.get_articles()

@app.post("/api/news/fetch", response_model=list[FetchResult])
async def post_news(request: FetchRequest):
    return await service.start(request.category, request.language, request.country) 

@app.get("/api/export/csv")
async def export_csv(category: str | None= None, limit: int = 20):
    articles = await data.get_articles(category=category, limit=limit)
    output = StringIO()
    writer = csv.writer(output)
    writer.writerow(["id", "title", "url", "category", "language", "country", "summary", "sentiment", "publishedAt"])
    for a in articles:
        writer.writerow([a["id"], a["title"], a["url"], a["category"], a["language"], a["country"], a["summary"], a["sentiment"], a["publishedAt"]])
    output.seek(0)
    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=articles.csv"}
    )