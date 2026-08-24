from pydantic import BaseModel
from typing import Literal

class FetchRequest(BaseModel):
    category: str
    language: str
    country: str
    
class ArticleResponse(BaseModel):
    id: int
    title: str
    url: str
    category: str
    language: str
    country: str
    summary: str
    sentiment: int | None
    publishedAt: str

class FetchResult(BaseModel):
    title: str
    summary: str
    sentiment: int
    status: str

class SchedulerConfigIn(BaseModel):
    category:str
    language:str
    country:str
    interval_h:Literal[12, 24]

class SchedulerConfigOut(SchedulerConfigIn):
    pass