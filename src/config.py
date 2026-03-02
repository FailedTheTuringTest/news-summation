import json
from pydantic_settings import BaseSettings, SettingsConfigDict
from pathlib import Path
from typing import Optional


DEFAULT_RSS_LOCAL = [
    "https://example.com/local/rss",
]

DEFAULT_RSS_NATIONAL = [
    "https://example.com/national/rss",
]

DEFAULT_RSS_GLOBAL = [
    "https://feeds.bbci.co.uk/news/world/rss.xml",
]


def load_config() -> dict:
    paths = [
        Path.cwd() / "regions.json",
        Path.home() / ".news-summariser" / "regions.json",
    ]
    for path in paths:
        if path.exists():
            with open(path) as f:
                return json.load(f)
    return {}


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="NEWS_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )
    
    newsapi_key: Optional[str] = None
    ollama_cloud_key: Optional[str] = None
    ollama_cloud_url: str = "https://ollama.com/api/generate"
    ollama_model: str = "deepseek-v3.1:671b-cloud"
    
    local_location: str = "Your City, Your Country"
    country_code: str = "us"
    
    max_articles_per_source: int = 10
    
    rss_feeds_local: list[str] = DEFAULT_RSS_LOCAL
    rss_feeds_national: list[str] = DEFAULT_RSS_NATIONAL
    rss_feeds_global: list[str] = DEFAULT_RSS_GLOBAL


class Config:
    _instance: Optional["Config"] = None
    _settings: Optional[Settings] = None
    
    def __new__(cls) -> "Config":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    @property
    def settings(self) -> Settings:
        if self._settings is None:
            config_data = load_config()
            self._settings = Settings(**config_data)
        return self._settings
    
    def reload(self) -> None:
        self._settings = None


config = Config()