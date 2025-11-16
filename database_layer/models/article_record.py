# ArticleRecord model
# article_record.py
from pydantic import BaseModel
from typing import Optional, List

class ArticleRecord(BaseModel):
    id: str
    url: str
    title: str
    content: str
    published_at: Optional[str]
    tags: List[str] = []

