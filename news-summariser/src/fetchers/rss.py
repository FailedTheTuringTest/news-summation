import httpx
import feedparser
from datetime import datetime
from typing import Optional
from .base import Article, BaseFetcher


class RSSFetcher(BaseFetcher):
    def __init__(self, feeds: list[str], source_label: str = "RSS"):
        self._feeds = feeds
        self._source_label = source_label
    
    @property
    def source_name(self) -> str:
        return self._source_label
    
    async def fetch(
        self, 
        query: Optional[str] = None,
        category: str = "general"
    ) -> list[Article]:
        articles: list[Article] = []
        
        for feed_url in self._feeds:
            try:
                async with httpx.AsyncClient() as client:
                    response = await client.get(feed_url, timeout=10.0, follow_redirects=True)
                    response.raise_for_status()
                
                feed = feedparser.parse(response.content)
                
                for entry in feed.entries[:15]:
                    if not entry.get("title") or not entry.get("link"):
                        continue
                    
                    if query and query.lower() not in entry.get("title", "").lower():
                        continue
                    
                    published_at = None
                    if entry.get("published_parsed"):
                        try:
                            published_at = datetime(*entry.published_parsed[:6])
                        except (ValueError, TypeError):
                            pass
                    
                    source_name = entry.get("source", {}).get("title", self._source_label)
                    if hasattr(feed, "feed") and feed.feed.get("title"):
                        source_name = feed.feed.title
                    
                    articles.append(Article(
                        title=entry.title,
                        url=entry.link,
                        source=source_name,
                        summary=entry.get("summary"),
                        content=entry.get("content", [{}])[0].get("value") if entry.get("content") else None,
                        published_at=published_at,
                        category=category,
                    ))
            except Exception:
                continue
        
        return articles