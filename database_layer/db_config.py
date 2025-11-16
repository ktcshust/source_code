# database config loader
# db_config.py
from pydantic import BaseModel
import os

class DatabaseSettings(BaseModel):
    postgres_url: str = os.getenv("POSTGRES_URL", "postgresql+psycopg://user:password@localhost:5432/ai_news")
    mongo_url: str = os.getenv("MONGO_URL", "mongodb://localhost:27017")
    redis_url: str = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    s3_endpoint: str = os.getenv("S3_ENDPOINT", "http://localhost:9000")
    s3_access_key: str = os.getenv("S3_ACCESS_KEY", "minioadmin")
    s3_secret_key: str = os.getenv("S3_SECRET_KEY", "minioadmin")
    s3_bucket: str = os.getenv("S3_BUCKET", "news-reports")


settings = DatabaseSettings()

