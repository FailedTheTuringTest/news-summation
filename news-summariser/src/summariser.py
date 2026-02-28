import httpx
from typing import Optional
from .fetchers.base import Article
from .config import config


class Summariser:
    def __init__(
        self,
        api_key: Optional[str] = None,
        model: Optional[str] = None,
        api_url: Optional[str] = None,
    ):
        self._api_key = api_key or config.settings.ollama_cloud_key
        self._model = model or config.settings.ollama_model
        self._api_url = api_url or config.settings.ollama_cloud_url
    
    async def summarise_articles(self, articles: list[Article], scope: str) -> str:
        if not articles:
            return f"No articles found for {scope} news."
        
        articles_text = self._format_articles_for_summary(articles)
        
        prompt = f"""You are a news summariser. Create a concise, well-structured summary of the following {scope} news articles.

Focus on:
1. Key headlines and main stories
2. Important facts and developments
3. Notable trends or patterns

Present the summary in a clear, scannable format with bullet points for main stories.

Articles:
{articles_text}

Provide a summary in 3-5 bullet points, each 1-2 sentences. End with a brief "In brief" one-line takeaway."""

        summary = await self._call_ollama_cloud(prompt)
        if summary.startswith("API Error") or summary.startswith("HTTP Error") or summary.startswith("Error"):
            # Fallback if Ollama is unreachable
            return self._local_fallback_summary(articles, scope) + f"\n\n[Ollama Status: {summary}]"
        return summary
    
    def _format_articles_for_summary(self, articles: list[Article], max_articles: int = 15) -> str:
        formatted = []
        for i, article in enumerate(articles[:max_articles], 1):
            text = f"{i}. {article.title}"
            if article.summary:
                text += f"\n   {article.summary[:300]}..."
            formatted.append(text)
        return "\n\n".join(formatted)
    
    async def _call_ollama_cloud(self, prompt: str) -> str:
        headers = {"Content-Type": "application/json"}
        if self._api_key:
            headers["Authorization"] = f"Bearer {self._api_key}"

        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(
                    self._api_url,
                    headers=headers,
                    json={
                        "model": self._model,
                        "prompt": prompt,
                        "stream": False,
                    },
                    timeout=60.0,
                )
                if response.status_code != 200:
                    return f"API Error {response.status_code}: {response.text[:500]}"
                data = response.json()
                return data["response"]
            except httpx.HTTPStatusError as e:
                return f"HTTP Error: {e.response.status_code} - {e.response.text[:200]}"
            except httpx.HTTPError as e:
                return f"Error calling Ollama Cloud: {str(e)}"
            except (KeyError, IndexError) as e:
                return f"Error parsing response: {str(e)}"
    
    def _local_fallback_summary(self, articles: list[Article], scope: str) -> str:
        lines = [f"📰 {scope.upper()} NEWS HEADLINES\n"]
        
        seen_titles = set()
        for article in articles[:10]:
            title_lower = article.title.lower()
            if any(t in title_lower for t in seen_titles):
                continue
            seen_titles.add(title_lower[:50])
            
            bullet = f"• {article.title}"
            if article.source:
                bullet += f" ({article.source})"
            lines.append(bullet)
        
        lines.append(f"\nShowing {min(len(articles), 10)} of {len(articles)} articles.")
        lines.append("\n💡 Set NEWS_OLLAMA_CLOUD_KEY env var for AI-powered summaries.")
        
        return "\n".join(lines)
    
    async def summarise_by_topic(self, articles: list[Article], scope: str) -> dict[str, str]:
        if not articles:
            return {"general": f"No articles found for {scope} news."}
        
        categories: dict[str, list[Article]] = {}
        for article in articles:
            cat = article.category or "general"
            if cat not in categories:
                categories[cat] = []
            categories[cat].append(article)
        
        summaries = {}
        for category, cat_articles in categories.items():
            summaries[category] = await self.summarise_articles(cat_articles, f"{scope} {category}")
        
        return summaries