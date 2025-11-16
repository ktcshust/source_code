# config loader
from pydantic import BaseSettings

class Settings(BaseSettings):
    REDIS_URL: str = "redis://localhost:6379/0"
    INPUT_STREAM: str = "processing:ingested"
    MONGO_URI: str = "mongodb://localhost:27017"
    MONGO_DB: str = "news_ai"
    OPENAI_API_KEY: str | None = None
    OPENAI_MODEL: str = "gpt-4o-mini"   # default model (override as needed)
    LLM_LOCAL_MODEL_PATH: str | None = None  # path to .gguf/.bin if using llama-cpp
    SUMMARY_MIN_TOKENS: int = 50
    SUMMARY_MAX_TOKENS: int = 400
    SMTP_HOST: str = "smtp.example.com"
    SMTP_PORT: int = 587
    SMTP_USER: str | None = None
    SMTP_PASSWORD: str | None = None
    REPORT_OUTPUT_DIR: str = "/tmp/reports"
    PUBLISH_SUMMARY_STREAM: str = "ai:summaries"  # optional redis stream for downstream consumers
    class Config:
        env_file = ".env"

settings = Settings()
