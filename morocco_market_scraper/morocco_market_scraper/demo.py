#!/usr/bin/env python3
"""
Example script demonstrating Morocco Market Scraper functionality
"""

import sys
from pathlib import Path

# Add parent to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from datetime import datetime
import json


def demo_stock_scraping():
    """Demonstrate stock data scraping"""
    print("\n" + "=" * 60)
    print("📈 STOCK DATA SCRAPING DEMO")
    print("=" * 60)
    
    from scrapers.stock_scraper import MarketDataAggregator, BPNetScraper, BMCECapitalScraper
    
    # Test BPNet scraper (most reliable)
    print("\n🏦 Testing BPNet Scraper...")
    bpnet = BPNetScraper()
    stocks = bpnet.get_all_stocks()
    
    print(f"✅ Found {len(stocks)} stocks from BPNet")
    print("\nTop 10 stocks by variation:")
    print("-" * 50)
    
    sorted_stocks = sorted(
        [s for s in stocks if s.variation_pct is not None],
        key=lambda x: x.variation_pct or 0,
        reverse=True
    )
    
    for stock in sorted_stocks[:10]:
        sign = "+" if (stock.variation_pct or 0) >= 0 else ""
        print(f"  {stock.ticker:6} {stock.name:30} {stock.price:>10.2f} MAD  {sign}{stock.variation_pct:>6.2f}%")
    
    # Test aggregator
    print("\n🔄 Testing Market Data Aggregator...")
    aggregator = MarketDataAggregator()
    merged = aggregator.get_merged_stocks()
    
    print(f"✅ Merged {len(merged)} unique stocks from all sources")
    
    # Export sample
    aggregator.export_to_json("data/sample_market_data.json")
    print("✅ Exported to data/sample_market_data.json")
    
    return stocks


def demo_news_scraping():
    """Demonstrate news scraping"""
    print("\n" + "=" * 60)
    print("📰 NEWS SCRAPING DEMO")
    print("=" * 60)
    
    from news.news_scraper import NewsAggregator, RSSNewsScraper
    
    # Test RSS scraping for a source with RSS
    print("\n📡 Testing RSS Feed Scraping...")
    rss_sources = ["leseco", "medias24", "lavieeco", "challenge"]
    
    aggregator = NewsAggregator()
    
    for source in rss_sources[:2]:  # Test first 2
        try:
            articles = aggregator.scrape_source(source, max_articles=5)
            print(f"  {source}: {len(articles)} articles")
        except Exception as e:
            print(f"  {source}: Error - {e}")
    
    # Scrape all with relevance filtering
    print("\n🔍 Scraping all sources with relevance filtering...")
    all_articles = aggregator.scrape_all(max_per_source=5, min_relevance=0)
    
    print(f"✅ Total articles: {len(all_articles)}")
    
    # Show top relevant articles
    print("\n📊 Top 5 Most Relevant Articles:")
    print("-" * 60)
    
    for i, article in enumerate(aggregator.get_top_stories(5), 1):
        print(f"\n{i}. [{article.relevance_score:.0f}] {article.title[:70]}...")
        print(f"   Source: {article.source}")
        print(f"   Keywords: {', '.join(article.matched_keywords[:5])}")
        if article.published_date:
            print(f"   Date: {article.published_date.strftime('%Y-%m-%d %H:%M')}")
    
    # Summary report
    print("\n📈 Summary Report:")
    print("-" * 40)
    report = aggregator.get_summary_report()
    print(f"  Total articles: {report['total_articles']}")
    print(f"  Average relevance: {report['avg_relevance']:.1f}")
    print(f"  High relevance (>50): {report['high_relevance_count']}")
    print(f"  Top keywords: {[k[0] for k in report['top_keywords'][:5]]}")
    
    # Export
    aggregator.export_to_json("data/sample_news_data.json")
    print("\n✅ Exported to data/sample_news_data.json")
    
    return all_articles


def demo_database():
    """Demonstrate database operations"""
    print("\n" + "=" * 60)
    print("💾 DATABASE OPERATIONS DEMO")
    print("=" * 60)
    
    from utils.database import MarketDatabase
    
    db = MarketDatabase("data/demo_market.db")
    print("✅ Database initialized")
    
    # Insert sample stock
    sample_stock = {
        "ticker": "ATW",
        "name": "Attijariwafa Bank",
        "price": 744.90,
        "variation_pct": 2.03,
        "volume": 15000,
        "high": 745.50,
        "low": 730.00,
        "source": "demo"
    }
    
    db.insert_stock(sample_stock)
    print(f"✅ Inserted sample stock: {sample_stock['ticker']}")
    
    # Insert sample news
    sample_news = {
        "hash_id": f"demo_{datetime.now().timestamp()}",
        "title": "Attijariwafa Bank annonce des résultats records",
        "url": "https://example.com/news/atw-results",
        "source": "Demo News",
        "relevance_score": 85.0,
        "matched_keywords": ["attijariwafa", "banque", "résultats"],
        "summary": "La banque leader affiche une croissance significative..."
    }
    
    db.insert_news(sample_news)
    print(f"✅ Inserted sample news article")
    
    # Query data
    stocks = db.get_latest_stocks()
    print(f"✅ Retrieved {len(stocks)} stocks from database")
    
    news = db.get_news(limit=10, min_relevance=0)
    print(f"✅ Retrieved {len(news)} news articles from database")
    
    return db


def demo_market_monitor():
    """Demonstrate the full market monitor"""
    print("\n" + "=" * 60)
    print("🖥️ MARKET MONITOR DEMO")
    print("=" * 60)
    
    from main import MarketMonitor
    
    monitor = MarketMonitor("data/demo_market.db")
    print("✅ Market Monitor initialized")
    
    # Run single scrape
    print("\n🔄 Running single scrape cycle...")
    result = monitor.run_once()
    
    print(f"\nStock scrape: {result['stocks']['status']}")
    print(f"  - Stocks: {result['stocks'].get('stocks_count', 0)}")
    print(f"  - Duration: {result['stocks'].get('duration_seconds', 0)}s")
    
    print(f"\nNews scrape: {result['news']['status']}")
    print(f"  - New articles: {result['news'].get('articles_new', 0)}")
    print(f"  - Duration: {result['news'].get('duration_seconds', 0)}s")
    
    # Get summary
    print("\n📊 Market Summary:")
    print("-" * 40)
    summary = monitor.get_market_summary()
    
    print(f"Total stocks tracked: {summary['market']['total_stocks']}")
    
    if summary['top_gainers']:
        print("\nTop Gainers:")
        for g in summary['top_gainers'][:3]:
            print(f"  {g['ticker']}: {g['price']} MAD (+{g['variation_pct']}%)")
    
    if summary['top_losers']:
        print("\nTop Losers:")
        for l in summary['top_losers'][:3]:
            print(f"  {l['ticker']}: {l['price']} MAD ({l['variation_pct']}%)")
    
    return monitor


def main():
    """Run all demos"""
    print("\n" + "=" * 70)
    print("🇲🇦 MOROCCO STOCK MARKET SCRAPER - DEMO")
    print("=" * 70)
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Create data directory
    Path("data").mkdir(exist_ok=True)
    
    try:
        # Run demos
        stocks = demo_stock_scraping()
        articles = demo_news_scraping()
        db = demo_database()
        monitor = demo_market_monitor()
        
        print("\n" + "=" * 70)
        print("✅ ALL DEMOS COMPLETED SUCCESSFULLY")
        print("=" * 70)
        
        print("\nGenerated files:")
        print("  - data/sample_market_data.json")
        print("  - data/sample_news_data.json")
        print("  - data/demo_market.db")
        
        print("\nNext steps:")
        print("  1. Run 'python main.py monitor' for continuous monitoring")
        print("  2. Run 'python main.py summary' for market overview")
        print("  3. Run 'python main.py stock ATW' for specific stock info")
        print("  4. Check the README.md for full documentation")
        
    except Exception as e:
        print(f"\n❌ Error during demo: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
