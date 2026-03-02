# News Summariser

AI-powered terminal app that summarises local, national, and global news using free AI models.

## Features

- **Multiple news sources**: RSS feeds + NewsAPI.org
- **AI summarisation**: Ollama Cloud (free tier) with Llama 3.2
- **Three scopes**: Local, National, Global
- **Beautiful output**: Rich terminal formatting with panels and progress indicators

## Installation

### Arch / CachyOS

Install dependencies via pacman:

```bash
sudo pacman -S python-httpx python-click python-rich python-feedparser python-pydantic python-pyyaml
```

If `python-pydantic-settings` is not available in the official repos, install from the AUR:

```bash
yay -S python-pydantic-settings
```

### Other distros

```bash
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
  "ollama_cloud_url": "https://ollama.com/api/generate",
  "ollama_model": "deepseek-v3.1:671b-cloud"
}
```

Environment variables also work as fallback:
- `NEWS_NEWSAPI_KEY`
- `NEWS_OLLAMA_CLOUD_KEY`

## Usage

```bash
# Get local news (as configured)
python3 -m src.main local

# Get national news (as configured)
python3 -m src.main national

# Get global news
python3 -m src.main global

# Get all summaries
python3 -m src.main all

# View configuration
python3 -m src.main config

# List news sources
python3 -m src.main sources

# JSON output
python3 -m src.main local --json
```

## Daily Autostart (KDE Plasma)

Set up the news summariser to open a terminal with your daily news on first login:

```bash
python3 -m src.main setup-autostart
```

This creates:
- `~/.news-summariser/daily_run.sh` — script that runs once per day
- `~/.config/autostart/news-summariser.desktop` — KDE autostart entry that launches Konsole

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
1. Visit https://ollama.com and sign in
2. Go to Settings → API Keys and generate a key
3. Set it in `regions.json` as `ollama_cloud_key` or via `NEWS_OLLAMA_CLOUD_KEY` env var
4. Free tier is available during cloud preview