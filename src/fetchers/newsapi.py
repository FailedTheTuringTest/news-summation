import httpx
from datetime import datetime
from typing import Optional
from .base import Article, BaseFetcher
from ..config import config


class NewsAPIFetcher(BaseFetcher):
    def __init__(self, api_key: Optional[str] = None):
        self._api_key = api_key or config.settings.newsapi_key
        self._base_url = "https://newsapi.org/v2"
    
    @property
    def source_name(self) -> str:
        return "NewsAPI"
    
    async def fetch(
        self, 
        query: Optional[str] = None, 
        category: str = "general",
        country: Optional[str] = None,
        page_size: int = 10
    ) -> list[Article]:
        if not self._api_key:
            return []
        
        articles: list[Article] = []
        
        async with httpx.AsyncClient() as client:
            if query:
                url = f"{self._base_url}/everything"
                params = {
                    "q": query,
                    "pageSize": page_size,
                    "sortBy": "publishedAt",
                    "apiKey": self._api_key,
                }
            else:
                url = f"{self._base_url}/top-headlines"
                params = {
                    "category": category,
                    "pageSize": page_size,
                    "apiKey": self._api_key,
                }
                if country:
                    params["country"] = country
            
            try:
                response = await client.get(url, params=params, timeout=10.0)
                response.raise_for_status()
                data = response.json()
                
                for item in data.get("articles", []):
                    if not item.get("title") or not item.get("url"):
                        continue
                    
                    published_at = None
                    if item.get("publishedAt"):
                        try:
                            published_at = datetime.fromisoformat(
                                item["publishedAt"].replace("Z", "+00:00")
                            )
                        except (ValueError, TypeError):
                            pass
                    
                    articles.append(Article(
                        title=item["title"],
                        url=item["url"],
                        source=item.get("source", {}).get("name", "Unknown"),
                        summary=item.get("description"),
                        content=item.get("content"),
                        published_at=published_at,
                        category=category,
                    ))
            except httpx.HTTPError:
                pass
        
        return articles