from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional
import hashlib


@dataclass
class Article:
    title: str
    url: str
    source: str
    summary: Optional[str] = None
    content: Optional[str] = None
    published_at: Optional[datetime] = None
    category: str = "general"
    
    def __hash__(self) -> int:
        return int(hashlib.md5(self.url.encode()).hexdigest(), 16)
    
    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Article):
            return False
        return self.url == other.url


class BaseFetcher(ABC):
    @abstractmethod
    async def fetch(self, query: Optional[str] = None, category: str = "general") -> list[Article]:
        pass
    
    @property
    @abstractmethod
    def source_name(self) -> str:
        pass