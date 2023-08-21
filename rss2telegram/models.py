from datetime import datetime
from typing import Optional

from pydantic import BaseModel
from pydantic_settings import BaseSettings, SettingsConfigDict


class Post(BaseModel):
    title: str
    image: Optional[str]
    content: str
    date: datetime


class Settings(BaseSettings):
    TELEGRAM_TOKEN: str
    CHANNEL_ID: str
    FEED: str
    POSTS_FILE: str = "posts.json"
    VERBOSE: bool = False

    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8"
    )


settings = Settings()
