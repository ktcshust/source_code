# SummaryRepository
# summary_repository.py
from ..mongo_client import summaries_collection
from ..models.summary_record import SummaryRecord

class SummaryRepository:

    @staticmethod
    def save(summary: SummaryRecord):
        summaries_collection.update_one(
            {"id": summary.id},
            {"$set": summary.model_dump()},
            upsert=True
        )

    @staticmethod
    def get_by_article(article_id: str):
        return summaries_collection.find_one({"article_id": article_id})

