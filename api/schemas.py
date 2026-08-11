from pydantic import BaseModel, Field

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
    sentiment: int
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
    interval_h:int = Field(...,gt=0)

class SchedulerConfigOut(SchedulerConfigIn):
    pass