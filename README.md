# News Summariser

AI-powered terminal app that summarises local, national, and global news using free AI models.

## Features

- **Multiple news sources**: RSS feeds + NewsAPI.org
- **AI summarisation**: Ollama Cloud (free tier) with Llama 3.2
- **Three scopes**: Local, National, Global
- **Beautiful output**: Rich terminal formatting with panels and progress indicators

## Installation

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .
```

## Configuration

All settings are configured in `regions.json`. Create it in the project root or at `~/.news-summariser/regions.json`:

```json
{
  "local_location": "Your City, Your Country",
  "country_code": "us",
  "max_articles_per_source": 10,
  "rss_feeds_local": ["https://example.com/local/rss"],
  "rss_feeds_national": ["https://example.com/national/rss"],
  "rss_feeds_global": ["https://feeds.bbci.co.uk/news/world/rss.xml"],
  "newsapi_key": "your_key_here",
  "ollama_cloud_key": "your_key_here",
  "ollama_cloud_url": "http://localhost:11434/api/generate",
  "ollama_model": "llama3.2"
}
```

Environment variables also work as fallback:
- `NEWS_NEWSAPI_KEY`
- `NEWS_OLLAMA_CLOUD_KEY`

## Usage

```bash
# Get local news (as configured)
news local

# Get national news (as configured)
news national

# Get global news
news global

# Get all summaries
news all

# View configuration
news config

# List news sources
news sources

# JSON output
news local --json
```

## Without API Keys

The app works without any API keys:
- RSS feeds are fetched directly (no key required)
- Without Ollama key, shows formatted headlines instead of AI summaries

## Getting API Keys

### NewsAPI.org (Optional)
1. Visit https://newsapi.org/register
2. Free tier: 100 requests/day
3. Paste key in config

### Ollama Cloud (For AI summaries)
1. Visit https://ollama.ai
2. Get your API key
3. Free tier available for hosted models