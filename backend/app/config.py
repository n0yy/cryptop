from pydantic_settings import BaseSettings
from typing import List
from functools import lru_cache


class Settings(BaseSettings):
    DATABASE_URL: str
    REDIS_URL: str
    CELERY_BROKER_URL: str
    CELERY_RESULT_BACKEND: str
    
    OPENAI_API_KEY: str
    ANTHROPIC_API_KEY: str = ""
    
    COINGECKO_API_KEY: str = ""
    COINMARKETCAP_API_KEY: str = ""
    ETHERSCAN_API_KEY: str = ""
    TWITTER_BEARER_TOKEN: str = ""
    REDDIT_CLIENT_ID: str = ""
    REDDIT_CLIENT_SECRET: str = ""
    
    TWILIO_ACCOUNT_SID: str = ""
    TWILIO_AUTH_TOKEN: str = ""
    TWILIO_PHONE_NUMBER: str = ""
    
    SMTP_HOST: str = "smtp.gmail.com"
    SMTP_PORT: int = 587
    SMTP_USER: str = ""
    SMTP_PASSWORD: str = ""
    
    DISCORD_WEBHOOK_URL: str = ""
    
    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    ENVIRONMENT: str = "development"
    LOG_LEVEL: str = "INFO"
    CORS_ORIGINS: str = "http://localhost:3000,http://localhost:8000"
    
    WEBSOCKET_MAX_CONNECTIONS: int = 10000
    WEBSOCKET_PING_INTERVAL: int = 30
    WEBSOCKET_PING_TIMEOUT: int = 10
    
    CACHE_TTL: int = 300
    RATE_LIMIT_PER_MINUTE: int = 60
    
    REPORT_STORAGE_PATH: str = "/tmp/reports"
    CHART_STORAGE_PATH: str = "/tmp/charts"
    
    class Config:
        env_file = ".env"
        case_sensitive = True
    
    @property
    def cors_origins_list(self) -> List[str]:
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",")]


@lru_cache()
def get_settings() -> Settings:
    return Settings()

CELERY_BROKER_URL: str = Field(default="redis://localhost:6379/0")
CELERY_RESULT_BACKEND: str = Field(default="redis://localhost:6379/0")


