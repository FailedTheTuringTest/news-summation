import asyncio
import click
from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown
from rich.progress import Progress, SpinnerColumn, TextColumn
from typing import Optional

from .fetchers import Article, NewsAPIFetcher, RSSFetcher
from .summariser import Summariser
from .config import config


console = Console()


def deduplicate_articles(articles: list[Article]) -> list[Article]:
    seen = set()
    unique = []
    for article in articles:
        key = (article.title.lower()[:50], article.source)
        if key not in seen:
            seen.add(key)
            unique.append(article)
    return unique


async def fetch_local_news() -> list[Article]:
    settings = config.settings
    articles = []
    
    rss_fetcher = RSSFetcher(settings.rss_feeds_local, "Local RSS")
    articles.extend(await rss_fetcher.fetch(query=settings.local_location.split(",")[0]))
    
    if settings.newsapi_key:
        newsapi = NewsAPIFetcher()
        local_query = settings.local_location
        articles.extend(await newsapi.fetch(query=local_query))
    
    return deduplicate_articles(articles)[:settings.max_articles_per_source]


async def fetch_national_news() -> list[Article]:
    settings = config.settings
    articles = []
    
    rss_fetcher = RSSFetcher(settings.rss_feeds_national, "National RSS")
    articles.extend(await rss_fetcher.fetch())
    
    if settings.newsapi_key:
        newsapi = NewsAPIFetcher()
        articles.extend(await newsapi.fetch(country=settings.country_code))
    
    return deduplicate_articles(articles)[:settings.max_articles_per_source]


async def fetch_global_news() -> list[Article]:
    settings = config.settings
    articles = []
    
    rss_fetcher = RSSFetcher(settings.rss_feeds_global, "Global RSS")
    articles.extend(await rss_fetcher.fetch())
    
    if settings.newsapi_key:
        newsapi = NewsAPIFetcher()
        articles.extend(await newsapi.fetch(category="world"))
    
    return deduplicate_articles(articles)[:settings.max_articles_per_source]


@click.group()
@click.version_option(version="0.1.0", prog_name="news-summariser")
def cli():
    """AI-powered news summariser for local, national, and global news."""
    pass


@cli.command()
@click.option("--json", "output_json", is_flag=True, help="Output as JSON")
def local(output_json: bool):
    """Get local news summary for your configured location."""
    asyncio.run(_fetch_and_summarise("local", fetch_local_news, output_json))


@cli.command()
@click.option("--json", "output_json", is_flag=True, help="Output as JSON")
def national(output_json: bool):
    """Get national news summary for your configured country."""
    asyncio.run(_fetch_and_summarise("national", fetch_national_news, output_json))


@cli.command()
@click.option("--json", "output_json", is_flag=True, help="Output as JSON")
def global_(output_json: bool):
    """Get global news summary."""
    asyncio.run(_fetch_and_summarise("global", fetch_global_news, output_json))


@cli.command()
@click.option("--json", "output_json", is_flag=True, help="Output as JSON")
def all_(output_json: bool):
    """Get all news summaries (local, national, global)."""
    asyncio.run(_fetch_all_summaries(output_json))


async def _fetch_and_summarise(
    scope: str, 
    fetch_func, 
    output_json: bool
):
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        task = progress.add_task(f"Fetching {scope} news...", total=None)
        articles = await fetch_func()
        progress.update(task, description=f"Generating {scope} summary...")
        
        summariser = Summariser()
        summary = await summariser.summarise_articles(articles, scope)
    
    if output_json:
        import json
        data = {
            "scope": scope,
            "article_count": len(articles),
            "articles": [
                {"title": a.title, "url": a.url, "source": a.source}
                for a in articles[:10]
            ],
            "summary": summary,
        }
        console.print(json.dumps(data, indent=2))
    else:
        title = f"📰 {scope.upper()} NEWS"
        if scope == "local":
            title += f" - {config.settings.local_location}"
        elif scope == "national":
            title += f" - {config.settings.country_code.upper()}"
        
        console.print(Panel(Markdown(summary), title=title, border_style="blue"))


async def _fetch_all_summaries(output_json: bool):
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        task = progress.add_task("Fetching all news...", total=None)
        
        local_articles, national_articles, global_articles = await asyncio.gather(
            fetch_local_news(),
            fetch_national_news(),
            fetch_global_news(),
        )
        
        progress.update(task, description="Generating summaries...")
        
        summariser = Summariser()
        summaries = await asyncio.gather(
            summariser.summarise_articles(local_articles, "local"),
            summariser.summarise_articles(national_articles, "national"),
            summariser.summarise_articles(global_articles, "global"),
        )
    
    if output_json:
        import json
        data = {
            "local": {"articles": len(local_articles), "summary": summaries[0]},
            "national": {"articles": len(national_articles), "summary": summaries[1]},
            "global": {"articles": len(global_articles), "summary": summaries[2]},
        }
        console.print(json.dumps(data, indent=2))
    else:
        for scope, articles, summary in [
            ("local", local_articles, summaries[0]),
            ("national", national_articles, summaries[1]),
            ("global", global_articles, summaries[2]),
        ]:
            title = f"📰 {scope.upper()} NEWS"
            if scope == "local":
                title += f" - {config.settings.local_location}"
            elif scope == "national":
                title += f" - {config.settings.country_code.upper()}"
            
            console.print(Panel(Markdown(summary), title=title, border_style="blue"))
            console.print()


@cli.command()
def config_cmd():
    """Show current configuration."""
    settings = config.settings
    console.print(Panel(
        f"[bold]Configuration[/bold]\n\n"
        f"Local Location: {settings.local_location}\n"
        f"Country Code: {settings.country_code}\n"
        f"Ollama Model: {settings.ollama_model}\n"
        f"NewsAPI Key: {'✓ Set' if settings.newsapi_key else '✗ Not set'}\n"
        f"Ollama Cloud Key: {'✓ Set' if settings.ollama_cloud_key else '✗ Not set'}\n\n"
        f"[dim]Set environment variables:[/dim]\n"
        f"  NEWS_NEWSAPI_KEY=<key>\n"
        f"  NEWS_OLLAMA_CLOUD_KEY=<key>",
        title="⚙️  Settings",
        border_style="yellow",
    ))


@cli.command()
def sources():
    """List configured news sources."""
    settings = config.settings
    
    console.print("\n[bold]📰 Local Sources[/bold]")
    for feed in settings.rss_feeds_local:
        console.print(f"  • {feed}")
    
    console.print("\n[bold]📰 National Sources[/bold]")
    for feed in settings.rss_feeds_national:
        console.print(f"  • {feed}")
    
    console.print("\n[bold]📰 Global Sources[/bold]")
    for feed in settings.rss_feeds_global:
        console.print(f"  • {feed}")
    
    console.print("\n[bold]🔑 API Sources[/bold]")
    console.print(f"  • NewsAPI: {'Configured' if settings.newsapi_key else 'Not configured'}")


if __name__ == "__main__":
    cli()