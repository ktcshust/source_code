# asyncpg / psycopg client
# postgres_client.py
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from .db_config import settings

engine = create_engine(settings.postgres_url, echo=False)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

