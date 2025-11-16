# motor client
# mongo_client.py
from pymongo import MongoClient
from .db_config import settings

mongo_client = MongoClient(settings.mongo_url)
mongo_db = mongo_client["ai_news"]

articles_collection = mongo_db["articles"]
summaries_collection = mongo_db["summaries"]

