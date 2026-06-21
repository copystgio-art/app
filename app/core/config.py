from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    anthropic_api_key: str = Field(..., env="ANTHROPIC_API_KEY")
    redis_url: str = Field("redis://localhost:6379/0", env="REDIS_URL")

    fb_email: str = Field("", env="FB_EMAIL")
    fb_password: str = Field("", env="FB_PASSWORD")
    fb_session_path: str = Field("./fb_session.json", env="FB_SESSION_PATH")

    default_search_country: str = Field("IT", env="DEFAULT_SEARCH_COUNTRY")
    default_ad_type: str = Field("ALL", env="DEFAULT_AD_TYPE")
    max_ads_per_search: int = Field(50, env="MAX_ADS_PER_SEARCH")

    database_url: str = Field("sqlite+aiosqlite:///./fb_automation.db", env="DATABASE_URL")

    class Config:
        env_file = ".env"
        extra = "ignore"


settings = Settings()
