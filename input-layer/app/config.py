from pydantic import BaseSettings

class Settings(BaseSettings):
    API_KEY: str = "change-me"
    REDIS_URL: str = "redis://localhost:6379/0"
    KAFKA_BOOTSTRAP: str = "localhost:9092"
    PUBLISHER: str = "redis"  # or "kafka"
    DEFAULT_USER_AGENT: str = "MyInputLayerBot/1.0 (+https://example.com/bot)"
    RSS_SOURCES: list = [
        "https://vnexpress.net/rss/tin-moi-nhat.rss",
        "https://cafebiz.vn/rss.rss",
        # add more
    ]

    class Config:
        env_file = ".env"

settings = Settings()
