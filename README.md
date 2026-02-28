# News Summariser

AI-powered terminal app that summarises local, national, and global news using free AI models.

## Features

- **Multiple news sources**: RSS feeds + NewsAPI.org
- **AI summarisation**: Ollama Cloud (free tier) with Llama 3.2
- **Three scopes**: Local (Westmeath, Ireland), National (Ireland), Global
- **Beautiful output**: Rich terminal formatting with panels and progress indicators

## Installation

```bash
pip install -e .
```

## Configuration

Set environment variables for API keys:

```bash
export NEWS_NEWSAPI_KEY=your_newsapi_key        # Optional, adds more sources
export NEWS_OLLAMA_CLOUD_KEY=your_key_here       # AI summaries
```

Or create a config file at `~/.news-summariser/config.yaml`:

```yaml
local_location: "Westmeath, Ireland"
country_code: "ie"
newsapi_key: your_key_here
ollama_cloud_key: your_key_here
ollama_model: "llama3.2"

rss_feeds_local:
  - "https://www.westmeathindependent.ie/rss"

rss_feeds_national:
  - "https://www.rte.ie/news/rss"
  - "https://www.irishtimes.com/news/rss"

rss_feeds_global:
  - "https://feeds.bbci.co.uk/news/world/rss.xml"
```

## Usage

```bash
# Get local news (Westmeath, Ireland)
news local

# Get national news (Ireland)
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