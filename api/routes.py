from fastapi import APIRouter, Depends
from .schemas import FetchRequest, FetchResult, ArticleResponse
from .dependencies import get_db, get_service, get_helper
from database import Database
from news_service import AnalizeNews
from auxiliary_functions import Auxiliary

router = APIRouter()

@router.get("/api/categories", response_model=list[str])
async def get_categories(helper:Auxiliary = Depends(get_helper)):
    return helper.validcategories

@router.get("/api/languages", response_model=dict[str,str])
async def get_languages(helper:Auxiliary = Depends(get_helper)):
    return helper.avaible_languages

@router.get("/api/countries", response_model=dict[str,str])
async def get_countries(helper:Auxiliary = Depends(get_helper)):
    return helper.countries

@router.get("/api/articles", response_model=list[ArticleResponse])
async def get_articles(database:Database = Depends(get_db)):
    return await database.get_articles()

@router.post("/api/news/fetch", response_model=list[FetchResult])
async def post_news(request:FetchRequest, service:AnalizeNews = Depends(get_service)):
    return await service.start(request.category, request.language, request.country)

@router.get("/api/export/csv")
async def export_csv(category:str | None = None, limit: int = 20, database:Database = Depends(get_db),):
    from io import StringIO
    import csv
    from fastapi.responses import StreamingResponse
    articles = await database.get_articles(category=category, limit=limit)
    output = StringIO()
    writer = csv.writer(output)
    writer.writerow(["id", "title", "url", "category", "language", "country", "summary", "sentiment", "publishedAt"])
    for a in articles:
        writer.writerow([a["id"], a["title"], a["url"], a["category"], a["language"], a["country"], a["summary"], a["sentiment"], a["publishedAt"]])
    output.seek(0)
    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=articles.csv"},
    )