# pydantic models
from pydantic import BaseModel
from typing import Any, Optional

class ArticleDiscovered(BaseModel):
    id: str
    title: Optional[str]
    link: str
    published: Optional[str]
    fetched_at: Optional[str]
    source: Optional[str]
    raw: Optional[dict] = None  # full original payload

class ProcessingJob(BaseModel):
    article: ArticleDiscovered
    received_at: str
    attempt: int = 0
