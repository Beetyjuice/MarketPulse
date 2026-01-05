# 🇲🇦 Morocco Stock Market Scraper

A comprehensive Python toolkit for scraping and monitoring the Casablanca Stock Exchange (Bourse de Casablanca) and Moroccan financial news.

## Features

### Stock Data Scraping
- **Multi-source aggregation**: Scrapes from BMCE Capital Bourse, BPNet (Banque Populaire), CDG Capital, and Casablanca Bourse
- **Real-time quotes**: Current prices, variations, volumes, order books
- **Market indices**: MASI, MADEX, and other indices
- **Historical data**: Track stock performance over time

### News Monitoring
- **18+ news sources**: Financial portals, official agencies, general media
- **RSS feed aggregation**: Automatic parsing of RSS feeds
- **Web scraping**: Direct scraping for sources without RSS
- **Relevance scoring**: AI-powered keyword matching and scoring
- **Real-time alerts**: Watchdog for high-relevance news

### Data Storage
- **SQLite database**: Persistent storage for all scraped data
- **Export capabilities**: JSON, CSV exports
- **Historical tracking**: Keep track of market history

## Installation

```bash
# Clone or copy the project
cd morocco_market_scraper

# Install dependencies
pip install -r requirements.txt

# For JavaScript-rendered pages (optional)
pip install selenium webdriver-manager
```

## Quick Start

### Command Line Interface

```bash
# Run a single scrape of stocks and news
python main.py scrape

# Scrape only stocks
python main.py scrape --stocks --export

# Scrape only news
python main.py scrape --news

# Start continuous monitoring
python main.py monitor --stock-interval 300 --news-interval 900

# Get market summary
python main.py summary

# Get market summary as JSON
python main.py summary --json

# Get specific stock information
python main.py stock ATW

# List all available tickers
python main.py list

# Export all data
python main.py export --output-dir data/exports
```

### Python API

```python
from morocco_market_scraper.main import MarketMonitor
from morocco_market_scraper.scrapers.stock_scraper import MarketDataAggregator
from morocco_market_scraper.news.news_scraper import NewsAggregator

# Initialize the market monitor
monitor = MarketMonitor()

# Scrape current stock data
stocks_result = monitor.scrape_stocks()
print(f"Scraped {stocks_result['stocks_count']} stocks")

# Scrape news
news_result = monitor.scrape_news(min_relevance=30)
print(f"Found {news_result['articles_new']} new articles")

# Get market summary
summary = monitor.get_market_summary()
print(summary['top_gainers'])

# Get specific stock info
atw_info = monitor.get_stock_info('ATW')
print(atw_info['current'])
```

### News Monitoring with Alerts

```python
from morocco_market_scraper.news.news_scraper import NewsWatchdog

def my_alert_handler(article):
    print(f"NEW ALERT: {article.title}")
    print(f"Relevance: {article.relevance_score}")
    print(f"Keywords: {article.matched_keywords}")
    # Send email, Slack notification, etc.

# Create watchdog
watchdog = NewsWatchdog()
watchdog.add_callback(my_alert_handler)

# Start monitoring (blocks until stopped)
watchdog.run(interval_seconds=900, min_relevance=50)
```

## Data Sources

### Stock Market Data
| Source | URL | Features |
|--------|-----|----------|
| BMCE Capital Bourse | bmcecapitalbourse.com | Full quotes, order book, history |
| BPNet (Banque Populaire) | bpnet.gbp.ma | All stocks, variations, yearly ranges |
| CDG Capital Bourse | cdgcapitalbourse.ma | Cotations, detailed data |
| Casablanca Bourse | casablanca-bourse.com | Official data (requires JS) |

### News Sources
| Category | Sources |
|----------|---------|
| **Official/Regulatory** | AMMC, Bank Al-Maghrib, Casablanca Bourse |
| **Financial News** | LesEco, Médias24, La Vie Éco, L'Économiste, Finances News |
| **Market News** | Le Boursier, Challenge.ma |
| **General/Business** | Le360, Hespress, MAP, TelQuel |
| **Economic Data** | HCP, Ministry of Finance |

## Project Structure

```
morocco_market_scraper/
├── main.py                 # Main orchestrator & CLI
├── requirements.txt        # Python dependencies
├── config/
│   └── settings.py         # Configuration, sources, tickers
├── scrapers/
│   └── stock_scraper.py    # Stock data scrapers
├── news/
│   └── news_scraper.py     # News scrapers & RSS aggregator
├── utils/
│   ├── helpers.py          # Utility functions
│   └── database.py         # SQLite database operations
└── data/
    ├── morocco_market.db   # SQLite database
    ├── market_data.json    # Latest stock data export
    ├── news_data.json      # Latest news export
    └── exports/            # CSV and bulk exports
```

## Stock Tickers

The system includes 70+ Moroccan stocks across all sectors:

- **Banking**: ATW (Attijariwafa), BCP, BOA, CIH, CDM, BMCI, CFG
- **Insurance**: WAA (Wafa Assurance), ADI, SAH
- **Telecom**: IAM (Maroc Telecom)
- **Real Estate**: ADH (Addoha), RDS, ALM, AKT, ARD
- **Mining**: MNG (Managem), SMI, CMT
- **Industry**: LHM (LafargeHolcim), CMA, SID
- **Energy**: TQM (Taqa), GAZ, TOT
- **Retail**: LBV (Label'Vie), ATH (Auto Hall)
- **Technology**: HPS, DWY, M2M, SMO

Run `python main.py list` for the complete list.

## Keyword Filtering

News articles are scored based on relevance using these keyword categories:

- **Market terms**: bourse, cotation, action, volume, indice...
- **Company names**: attijariwafa, maroc telecom, cosumar...
- **Sectors**: banque, assurance, immobilier, telecom...
- **Events**: dividende, résultats, fusion, acquisition...
- **Economic indicators**: PIB, inflation, taux directeur...

## Database Schema

The SQLite database includes these tables:

- `stocks`: Current and historical stock quotes
- `stock_history`: Daily OHLCV data
- `indices`: Market index values
- `news`: Scraped news articles with metadata
- `alerts`: Price alerts configuration
- `scrape_logs`: Scraping operation logs

## Configuration

Edit `config/settings.py` to:

- Add or remove data sources
- Modify scraping intervals
- Update keyword lists
- Configure rate limiting
- Add new stock tickers

## Error Handling

The scrapers include:

- Automatic retry with exponential backoff
- Rate limiting to avoid bans
- Graceful handling of network errors
- Duplicate detection for news articles
- Data validation for stock quotes

## Contributing

Contributions are welcome! Areas for improvement:

- Add more data sources
- Implement Selenium for JS-rendered sites
- Add technical analysis indicators
- Create visualization dashboard
- Implement notification systems (email, Telegram, etc.)

## Disclaimer

This tool is for educational and research purposes. Ensure compliance with the terms of service of each data source. Market data should not be used as the sole basis for investment decisions.

## License

MIT License - Free to use, modify, and distribute.
