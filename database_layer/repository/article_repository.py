# ArticleRepository
# article_repository.py
from ..mongo_client import articles_collection
from ..models.article_record import ArticleRecord

class ArticleRepository:

    @staticmethod
    def save(article: ArticleRecord):
        articles_collection.update_one(
            {"id": article.id},
            {"$set": article.model_dump()},
            upsert=True
        )

    @staticmethod
    def exists(article_id: str) -> bool:
        return articles_collection.find_one({"id": article_id}) is not None

    @staticmethod
    def get(article_id: str):
        return articles_collection.find_one({"id": article_id})

