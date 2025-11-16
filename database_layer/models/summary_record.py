# SummaryRecord model
# summary_record.py
from pydantic import BaseModel
from typing import Optional

class SummaryRecord(BaseModel):
    id: str
    article_id: str
    summary_text: str
    summary_vector: Optional[list] = None  # for pgvector

