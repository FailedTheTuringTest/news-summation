# news-summation

AI-powered terminal app that summarises local, national, and global news using cloud LLMs.

## Features

- **Multiple news sources**: RSS feeds + NewsAPI.org
- **AI summarisation**: Ollama Cloud with DeepSeek V3.1 (671B) by default
- **Three scopes**: Local, National, Global
- **Beautiful output**: Rich terminal formatting with panels and progress indicators
- **Fallback mode**: Shows formatted headlines when no API key is configured
- **Daily autostart**: Optional KDE Plasma autostart on first login of the day

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

This also installs a `news` CLI entry point you can run from anywhere.

## Configuration

All settings are configured in `regions.json`. The app looks for it in the following locations (in order):

1. `./regions.json` (project root)
2. `~/.news-summariser/regions.json`

```json
{
  "local_location": "Your City, Your Country",
  "country_code": "us",
  "max_articles_per_source": 10,
  "rss_feeds_local": ["https://example.com/local/rss"],
  "rss_feeds_national": ["https://example.com/national/rss"],
  "rss_feeds_global": ["https://feeds.bbci.co.uk/news/world/rss.xml"],
  "newsapi_key": null,
  "ollama_cloud_key": null,
  "ollama_cloud_url": "https://ollama.com/api/generate",
  "ollama_model": "deepseek-v3.1:671b-cloud"
}
```

Environment variables (prefixed with `NEWS_`) also work as fallback via pydantic-settings:

- `NEWS_NEWSAPI_KEY`
- `NEWS_OLLAMA_CLOUD_KEY`
- `NEWS_OLLAMA_CLOUD_URL`
- `NEWS_OLLAMA_MODEL`

You can also place a `.env` file in the project root.

## Usage

```bash
# Get local news
python3 -m src.main local

# Get national news
python3 -m src.main national

# Get global news
python3 -m src.main global

# Get all summaries (local + national + global)
python3 -m src.main all

# View current configuration
python3 -m src.main config-cmd

# List configured news sources
python3 -m src.main sources

# JSON output (works with any scope command)
python3 -m src.main local --json
```

If installed with `pip install -e .`, use `news` instead of `python3 -m src.main`:

```bash
news all
news local --json
```

## Daily Autostart (KDE Plasma)

Set up the news summariser to open a Konsole window with your daily news on first login:

```bash
python3 -m src.main setup-autostart
```

This creates:

- `~/.news-summariser/daily_run.sh` — script that runs once per day (skips if already run today)
- `~/.config/autostart/news-summariser.desktop` — KDE autostart entry that launches Konsole

> **Note:** The project directory must remain at its current location for the autostart script to work.

## Without API Keys

The app works without any API keys:

- RSS feeds are always fetched directly (no key required)
- Without an Ollama Cloud key, the app shows formatted headlines instead of AI summaries
- Without a NewsAPI key, only RSS feeds are used as sources

## Getting API Keys

### NewsAPI.org (Optional)

1. Visit https://newsapi.org/register
2. Free tier: 100 requests/day
3. Add to `regions.json` as `newsapi_key` or set `NEWS_NEWSAPI_KEY`

### Ollama Cloud (For AI summaries)

1. Visit https://ollama.com and sign in
2. Go to Settings → API Keys and generate a key
3. Add to `regions.json` as `ollama_cloud_key` or set `NEWS_OLLAMA_CLOUD_KEY`

## Project Structure

```
news-summation/
├── pyproject.toml          # Project metadata & dependencies
├── regions.json            # User configuration
└── src/
    ├── main.py             # CLI entry point (Click commands)
    ├── config.py            # Settings via pydantic-settings
    ├── summariser.py        # Ollama Cloud API integration
    └── fetchers/
        ├── base.py          # Article model & base fetcher
        ├── rss.py           # RSS feed fetcher (feedparser)
        └── newsapi.py       # NewsAPI.org fetcher
```

## Requirements

- Python ≥ 3.10
- httpx, click, rich, feedparser, pydantic, pydantic-settings, pyyaml
