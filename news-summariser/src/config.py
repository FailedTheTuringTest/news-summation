from pydantic import BaseModel
from pydantic_settings import BaseSettings, SettingsConfigDict
from pathlib import Path
from typing import Optional
import yaml


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="NEWS_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )
    
    newsapi_key: Optional[str] = None
    ollama_cloud_key: Optional[str] = None
    ollama_cloud_url: str = "http://localhost:11434/api/generate"
    ollama_model: str = "llama3.2"
    
    local_location: str = "Westmeath, Ireland"
    country_code: str = "ie"
    
    max_articles_per_source: int = 10
    
    rss_feeds_local: list[str] = [
        "https://www.westmeathindependent.ie/rss",
        "https://www.westmeathexaminer.ie/rss",
    ]
    
    rss_feeds_national: list[str] = [
        "https://www.rte.ie/news/rss",
        "https://www.irishtimes.com/news/rss",
        "https://www.independent.ie/news/rss",
    ]
    
    rss_feeds_global: list[str] = [
        "https://feeds.bbci.co.uk/news/world/rss.xml",
        "https://rss.nytimes.com/services/xml/rss/nyt/World.xml",
        "https://www.theguardian.com/world/rss",
    ]


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
            config_path = Path.home() / ".news-summariser" / "config.yaml"
            if config_path.exists():
                with open(config_path) as f:
                    config_data = yaml.safe_load(f) or {}
                self._settings = Settings(**config_data)
            else:
                self._settings = Settings()
        return self._settings
    
    def save_settings(self, settings: Settings) -> None:
        config_path = Path.home() / ".news-summariser" / "config.yaml"
        config_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(config_path, "w") as f:
            yaml.dump(settings.model_dump(exclude_none=False), f)
        
        self._settings = settings


config = Config()