import json
from pydantic import BaseModel
from pydantic_settings import BaseSettings, SettingsConfigDict
from pathlib import Path
from typing import Optional
import yaml


DEFAULT_RSS_LOCAL = [
    "https://www.westmeathindependent.ie/rss",
    "https://www.westmeathexaminer.ie/rss",
]

DEFAULT_RSS_NATIONAL = [
    "https://www.rte.ie/news/rss",
    "https://www.irishtimes.com/news/rss",
    "https://www.independent.ie/news/rss",
]

DEFAULT_RSS_GLOBAL = [
    "https://feeds.bbci.co.uk/news/world/rss.xml",
    "https://rss.nytimes.com/services/xml/rss/nyt/World.xml",
    "https://www.theguardian.com/world/rss",
]


def load_json_config() -> dict:
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
    ollama_cloud_url: str = "http://localhost:11434/api/generate"
    ollama_model: str = "llama3.2"
    
    local_location: str = "Westmeath, Ireland"
    country_code: str = "ie"
    
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
            config_data: dict = {}
            
            yaml_path = Path.home() / ".news-summariser" / "config.yaml"
            if yaml_path.exists():
                with open(yaml_path) as f:
                    yaml_config = yaml.safe_load(f) or {}
                config_data.update(yaml_config)
            
            json_config = load_json_config()
            config_data.update(json_config)
            
            self._settings = Settings(**config_data)
        return self._settings
    
    def reload(self) -> None:
        self._settings = None
    
    def save_settings(self, settings: Settings) -> None:
        config_path = Path.home() / ".news-summariser" / "config.yaml"
        config_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(config_path, "w") as f:
            yaml.dump(settings.model_dump(exclude_none=False), f)
        
        self._settings = settings


config = Config()