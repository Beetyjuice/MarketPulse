"""
News Scraper and RSS Aggregator for Moroccan Financial News
Monitors multiple news sources for market-relevant news and events
"""

import feedparser
import requests
from bs4 import BeautifulSoup
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any, Set
import json
import re
import hashlib
import time
import logging
from abc import ABC, abstractmethod
from concurrent.futures import ThreadPoolExecutor, as_completed

import sys
sys.path.append('..')
from utils.helpers import (
    clean_text, parse_date, generate_hash, create_session_with_retry, 
    RateLimiter, logger
)
from config.settings import NEWS_SOURCES, KEYWORDS, ScraperConfig

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class NewsArticle:
    """Data class for news articles"""
    title: str
    url: str
    source: str
    published_date: Optional[datetime] = None
    summary: Optional[str] = None
    content: Optional[str] = None
    author: Optional[str] = None
    category: Optional[str] = None
    tags: List[str] = field(default_factory=list)
    relevance_score: float = 0.0
    matched_keywords: List[str] = field(default_factory=list)
    hash_id: str = ""
    scraped_at: datetime = field(default_factory=datetime.now)
    language: str = "fr"
    
    def __post_init__(self):
        if not self.hash_id:
            self.hash_id = generate_hash(f"{self.url}{self.title}")
    
    def to_dict(self) -> Dict:
        return {
            "title": self.title,
            "url": self.url,
            "source": self.source,
            "published_date": self.published_date.isoformat() if self.published_date else None,
            "summary": self.summary,
            "content": self.content,
            "author": self.author,
            "category": self.category,
            "tags": self.tags,
            "relevance_score": self.relevance_score,
            "matched_keywords": self.matched_keywords,
            "hash_id": self.hash_id,
            "scraped_at": self.scraped_at.isoformat(),
            "language": self.language
        }


@dataclass
class RSSFeed:
    """Data class for RSS feed information"""
    name: str
    url: str
    last_checked: Optional[datetime] = None
    last_updated: Optional[datetime] = None
    etag: Optional[str] = None
    modified: Optional[str] = None
    articles_count: int = 0
    is_active: bool = True


class KeywordMatcher:
    """Matches news content against predefined keywords"""
    
    def __init__(self, keywords: Dict[str, List[str]] = None):
        self.keywords = keywords or KEYWORDS
        self._compile_patterns()
    
    def _compile_patterns(self):
        """Compile keyword patterns for efficient matching"""
        self.patterns = {}
        for category, words in self.keywords.items():
            # Create regex pattern for whole word matching
            pattern = r'\b(' + '|'.join(re.escape(w) for w in words) + r')\b'
            self.patterns[category] = re.compile(pattern, re.IGNORECASE)
    
    def calculate_relevance(self, text: str) -> Dict[str, Any]:
        """
        Calculate relevance score based on keyword matches
        Returns score and matched keywords
        """
        if not text:
            return {"score": 0.0, "matches": [], "categories": {}}
        
        text = text.lower()
        matches = []
        category_scores = {}
        
        for category, pattern in self.patterns.items():
            found = pattern.findall(text)
            if found:
                unique_found = list(set(found))
                matches.extend(unique_found)
                category_scores[category] = len(unique_found)
        
        # Calculate weighted score
        weights = {
            "market": 2.0,
            "companies": 1.5,
            "events": 1.5,
            "sectors": 1.0,
            "economic": 1.0
        }
        
        total_score = sum(
            category_scores.get(cat, 0) * weights.get(cat, 1.0) 
            for cat in weights
        )
        
        # Normalize score (0-100 scale)
        normalized_score = min(100, total_score * 5)
        
        return {
            "score": normalized_score,
            "matches": list(set(matches)),
            "categories": category_scores
        }


class BaseNewsScraper(ABC):
    """Base class for news scrapers"""
    
    def __init__(self, config: ScraperConfig = None):
        self.config = config or ScraperConfig()
        self.session = create_session_with_retry()
        self.session.headers.update(self.config.headers)
        self.session.headers['User-Agent'] = self.config.user_agent
        self.rate_limiter = RateLimiter(1.0 / self.config.rate_limit_delay)
        self.keyword_matcher = KeywordMatcher()
        self.seen_articles: Set[str] = set()
    
    def _fetch_page(self, url: str) -> Optional[BeautifulSoup]:
        """Fetch and parse a web page"""
        self.rate_limiter.wait()
        
        try:
            response = self.session.get(url, timeout=self.config.timeout)
            response.raise_for_status()
            return BeautifulSoup(response.text, 'html.parser')
        except requests.RequestException as e:
            logger.error(f"Error fetching {url}: {e}")
            return None
    
    def _is_duplicate(self, article: NewsArticle) -> bool:
        """Check if article has already been scraped"""
        if article.hash_id in self.seen_articles:
            return True
        self.seen_articles.add(article.hash_id)
        return False
    
    def _enrich_article(self, article: NewsArticle) -> NewsArticle:
        """Add relevance score and matched keywords to article"""
        text = f"{article.title} {article.summary or ''} {article.content or ''}"
        relevance = self.keyword_matcher.calculate_relevance(text)
        
        article.relevance_score = relevance["score"]
        article.matched_keywords = relevance["matches"]
        
        return article
    
    @abstractmethod
    def scrape(self, max_articles: int = 20) -> List[NewsArticle]:
        """Scrape news articles"""
        pass


class RSSNewsScraper(BaseNewsScraper):
    """Scraper for RSS feeds"""
    
    def __init__(self, source_key: str, config: ScraperConfig = None):
        super().__init__(config)
        self.source_key = source_key
        self.source_config = NEWS_SOURCES.get(source_key, {})
        self.rss_url = self.source_config.get("rss_url")
        self.source_name = self.source_config.get("name", source_key)
    
    def scrape(self, max_articles: int = 20) -> List[NewsArticle]:
        """Fetch articles from RSS feed"""
        articles = []
        
        if not self.rss_url:
            logger.warning(f"No RSS URL for {self.source_key}")
            return articles
        
        try:
            self.rate_limiter.wait()
            feed = feedparser.parse(self.rss_url)
            
            if feed.bozo and feed.bozo_exception:
                logger.warning(f"Feed parsing warning for {self.source_key}: {feed.bozo_exception}")
            
            for entry in feed.entries[:max_articles]:
                try:
                    # Parse publication date
                    pub_date = None
                    if hasattr(entry, 'published_parsed') and entry.published_parsed:
                        pub_date = datetime(*entry.published_parsed[:6])
                    elif hasattr(entry, 'updated_parsed') and entry.updated_parsed:
                        pub_date = datetime(*entry.updated_parsed[:6])
                    
                    # Extract content
                    content = ""
                    if hasattr(entry, 'content') and entry.content:
                        content = entry.content[0].get('value', '')
                    elif hasattr(entry, 'description'):
                        content = entry.description
                    
                    # Clean HTML from content
                    if content:
                        soup = BeautifulSoup(content, 'html.parser')
                        content = clean_text(soup.get_text())
                    
                    # Extract tags/categories
                    tags = []
                    if hasattr(entry, 'tags'):
                        tags = [t.term for t in entry.tags if hasattr(t, 'term')]
                    
                    article = NewsArticle(
                        title=clean_text(entry.get('title', '')),
                        url=entry.get('link', ''),
                        source=self.source_name,
                        published_date=pub_date,
                        summary=clean_text(entry.get('summary', ''))[:500],
                        content=content[:2000] if content else None,
                        author=entry.get('author', ''),
                        category=self.source_config.get("category", ""),
                        tags=tags,
                        language=self.source_config.get("language", "fr")
                    )
                    
                    if not self._is_duplicate(article):
                        article = self._enrich_article(article)
                        articles.append(article)
                
                except Exception as e:
                    logger.warning(f"Error parsing RSS entry: {e}")
            
            logger.info(f"Scraped {len(articles)} articles from {self.source_name} RSS")
            
        except Exception as e:
            logger.error(f"Error fetching RSS feed {self.source_key}: {e}")
        
        return articles


class WebNewsScraper(BaseNewsScraper):
    """Scraper for web pages without RSS feeds"""
    
    def __init__(self, source_key: str, config: ScraperConfig = None):
        super().__init__(config)
        self.source_key = source_key
        self.source_config = NEWS_SOURCES.get(source_key, {})
        self.news_url = self.source_config.get("news_url")
        self.base_url = self.source_config.get("base_url")
        self.source_name = self.source_config.get("name", source_key)
        
        # Define scraping rules per source
        self.scraping_rules = self._get_scraping_rules()
    
    def _get_scraping_rules(self) -> Dict:
        """Define CSS selectors and extraction rules for each source"""
        rules = {
            "ammc": {
                "article_selector": "article, .news-item, .actualite-item",
                "title_selector": "h2, h3, .title",
                "link_selector": "a",
                "date_selector": ".date, .published-date, time",
                "summary_selector": "p, .summary, .excerpt"
            },
            "leseco": {
                "article_selector": "article, .post, .news-item",
                "title_selector": "h2 a, h3 a, .entry-title a",
                "link_selector": "a",
                "date_selector": ".date, time, .post-date",
                "summary_selector": ".excerpt, .entry-summary, p"
            },
            "medias24": {
                "article_selector": ".article-item, article, .news-block",
                "title_selector": "h2, h3, .title",
                "link_selector": "a",
                "date_selector": ".date, time, .published",
                "summary_selector": ".summary, .excerpt, p"
            },
            "default": {
                "article_selector": "article, .post, .news-item, .article-item",
                "title_selector": "h2, h3, .title, .headline",
                "link_selector": "a",
                "date_selector": ".date, time, .published, .post-date",
                "summary_selector": ".summary, .excerpt, p"
            }
        }
        return rules.get(self.source_key, rules["default"])
    
    def scrape(self, max_articles: int = 20) -> List[NewsArticle]:
        """Scrape articles from news website"""
        articles = []
        
        if not self.news_url:
            logger.warning(f"No news URL for {self.source_key}")
            return articles
        
        soup = self._fetch_page(self.news_url)
        if not soup:
            return articles
        
        rules = self.scraping_rules
        
        # Find all article containers
        article_elements = soup.select(rules["article_selector"])[:max_articles]
        
        for element in article_elements:
            try:
                # Extract title
                title_elem = element.select_one(rules["title_selector"])
                if not title_elem:
                    continue
                title = clean_text(title_elem.get_text())
                
                # Extract link
                link_elem = element.select_one(rules["link_selector"])
                link = ""
                if link_elem and link_elem.get('href'):
                    link = link_elem.get('href')
                    if not link.startswith('http'):
                        link = f"{self.base_url.rstrip('/')}/{link.lstrip('/')}"
                elif title_elem.get('href'):
                    link = title_elem.get('href')
                    if not link.startswith('http'):
                        link = f"{self.base_url.rstrip('/')}/{link.lstrip('/')}"
                
                if not title or not link:
                    continue
                
                # Extract date
                pub_date = None
                date_elem = element.select_one(rules["date_selector"])
                if date_elem:
                    date_text = clean_text(date_elem.get_text())
                    pub_date = parse_date(date_text)
                
                # Extract summary
                summary = ""
                summary_elem = element.select_one(rules["summary_selector"])
                if summary_elem:
                    summary = clean_text(summary_elem.get_text())[:500]
                
                article = NewsArticle(
                    title=title,
                    url=link,
                    source=self.source_name,
                    published_date=pub_date,
                    summary=summary,
                    category=self.source_config.get("category", ""),
                    language=self.source_config.get("language", "fr")
                )
                
                if not self._is_duplicate(article):
                    article = self._enrich_article(article)
                    articles.append(article)
            
            except Exception as e:
                logger.warning(f"Error parsing article element: {e}")
        
        logger.info(f"Scraped {len(articles)} articles from {self.source_name}")
        return articles


class NewsAggregator:
    """Aggregates news from multiple sources"""
    
    def __init__(self, config: ScraperConfig = None):
        self.config = config or ScraperConfig()
        self.scrapers: Dict[str, BaseNewsScraper] = {}
        self.articles: List[NewsArticle] = []
        self.keyword_matcher = KeywordMatcher()
        self._initialize_scrapers()
    
    def _initialize_scrapers(self):
        """Initialize scrapers for all configured news sources"""
        for source_key, source_config in NEWS_SOURCES.items():
            if source_config.get("rss_url"):
                self.scrapers[source_key] = RSSNewsScraper(source_key, self.config)
            else:
                self.scrapers[source_key] = WebNewsScraper(source_key, self.config)
    
    def scrape_all(self, max_per_source: int = 10, 
                   min_relevance: float = 0.0,
                   categories: List[str] = None) -> List[NewsArticle]:
        """
        Scrape all news sources
        
        Args:
            max_per_source: Maximum articles per source
            min_relevance: Minimum relevance score (0-100)
            categories: Filter by source categories (e.g., ['financial_news', 'market'])
        
        Returns:
            List of NewsArticle objects sorted by relevance
        """
        all_articles = []
        
        # Filter scrapers by category if specified
        scrapers_to_use = self.scrapers
        if categories:
            scrapers_to_use = {
                k: v for k, v in self.scrapers.items()
                if NEWS_SOURCES.get(k, {}).get("category") in categories
            }
        
        # Scrape sources in parallel
        with ThreadPoolExecutor(max_workers=5) as executor:
            futures = {
                executor.submit(scraper.scrape, max_per_source): source_key
                for source_key, scraper in scrapers_to_use.items()
            }
            
            for future in as_completed(futures):
                source_key = futures[future]
                try:
                    articles = future.result()
                    all_articles.extend(articles)
                except Exception as e:
                    logger.error(f"Error scraping {source_key}: {e}")
        
        # Filter by relevance
        if min_relevance > 0:
            all_articles = [a for a in all_articles if a.relevance_score >= min_relevance]
        
        # Sort by relevance score (descending) then by date
        all_articles.sort(key=lambda x: (
            -x.relevance_score,
            -(x.published_date.timestamp() if x.published_date else 0)
        ))
        
        self.articles = all_articles
        return all_articles
    
    def scrape_source(self, source_key: str, max_articles: int = 20) -> List[NewsArticle]:
        """Scrape a specific news source"""
        if source_key not in self.scrapers:
            logger.error(f"Unknown source: {source_key}")
            return []
        
        return self.scrapers[source_key].scrape(max_articles)
    
    def get_top_stories(self, n: int = 10) -> List[NewsArticle]:
        """Get top N most relevant stories"""
        if not self.articles:
            self.scrape_all()
        
        return sorted(
            self.articles, 
            key=lambda x: -x.relevance_score
        )[:n]
    
    def get_recent_news(self, hours: int = 24) -> List[NewsArticle]:
        """Get news from the last N hours"""
        if not self.articles:
            self.scrape_all()
        
        cutoff = datetime.now() - timedelta(hours=hours)
        recent = [
            a for a in self.articles 
            if a.published_date and a.published_date > cutoff
        ]
        
        return sorted(recent, key=lambda x: -x.published_date.timestamp())
    
    def search_news(self, query: str) -> List[NewsArticle]:
        """Search articles by keyword"""
        if not self.articles:
            self.scrape_all()
        
        query = query.lower()
        results = []
        
        for article in self.articles:
            text = f"{article.title} {article.summary or ''} {article.content or ''}".lower()
            if query in text:
                results.append(article)
        
        return sorted(results, key=lambda x: -x.relevance_score)
    
    def get_news_by_company(self, company_name: str) -> List[NewsArticle]:
        """Get news related to a specific company"""
        if not self.articles:
            self.scrape_all()
        
        company_lower = company_name.lower()
        results = []
        
        for article in self.articles:
            text = f"{article.title} {article.summary or ''} {article.content or ''}".lower()
            if company_lower in text:
                results.append(article)
        
        return sorted(results, key=lambda x: -x.relevance_score)
    
    def export_to_json(self, filepath: str, articles: List[NewsArticle] = None):
        """Export articles to JSON file"""
        articles = articles or self.articles
        
        data = {
            "timestamp": datetime.now().isoformat(),
            "total_articles": len(articles),
            "articles": [a.to_dict() for a in articles],
            "sources": list(self.scrapers.keys())
        }
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Exported {len(articles)} articles to {filepath}")
    
    def get_summary_report(self) -> Dict:
        """Generate summary report of scraped news"""
        if not self.articles:
            return {"error": "No articles scraped"}
        
        # Count by source
        by_source = {}
        for article in self.articles:
            by_source[article.source] = by_source.get(article.source, 0) + 1
        
        # Count by category
        by_category = {}
        for article in self.articles:
            cat = article.category or "uncategorized"
            by_category[cat] = by_category.get(cat, 0) + 1
        
        # Get top keywords
        all_keywords = []
        for article in self.articles:
            all_keywords.extend(article.matched_keywords)
        
        keyword_counts = {}
        for kw in all_keywords:
            keyword_counts[kw] = keyword_counts.get(kw, 0) + 1
        
        top_keywords = sorted(
            keyword_counts.items(), 
            key=lambda x: -x[1]
        )[:20]
        
        return {
            "total_articles": len(self.articles),
            "by_source": by_source,
            "by_category": by_category,
            "top_keywords": top_keywords,
            "avg_relevance": sum(a.relevance_score for a in self.articles) / len(self.articles),
            "high_relevance_count": len([a for a in self.articles if a.relevance_score >= 50])
        }


class NewsWatchdog:
    """
    Continuous news monitoring service
    Watches for new articles and alerts on high-relevance content
    """
    
    def __init__(self, config: ScraperConfig = None):
        self.aggregator = NewsAggregator(config)
        self.seen_hashes: Set[str] = set()
        self.callbacks: List[callable] = []
        self.is_running = False
    
    def add_callback(self, callback: callable):
        """Add callback function for new article alerts"""
        self.callbacks.append(callback)
    
    def _notify(self, article: NewsArticle):
        """Notify all callbacks of new article"""
        for callback in self.callbacks:
            try:
                callback(article)
            except Exception as e:
                logger.error(f"Callback error: {e}")
    
    def check_new_articles(self, min_relevance: float = 30.0) -> List[NewsArticle]:
        """Check for new articles since last check"""
        new_articles = []
        
        # Scrape all sources
        articles = self.aggregator.scrape_all(max_per_source=5)
        
        for article in articles:
            if article.hash_id not in self.seen_hashes:
                self.seen_hashes.add(article.hash_id)
                
                if article.relevance_score >= min_relevance:
                    new_articles.append(article)
                    self._notify(article)
        
        return new_articles
    
    def run(self, interval_seconds: int = 900, min_relevance: float = 30.0):
        """
        Run continuous monitoring
        
        Args:
            interval_seconds: Check interval (default 15 minutes)
            min_relevance: Minimum relevance score for alerts
        """
        self.is_running = True
        logger.info(f"Starting news watchdog (interval: {interval_seconds}s)")
        
        while self.is_running:
            try:
                new_articles = self.check_new_articles(min_relevance)
                if new_articles:
                    logger.info(f"Found {len(new_articles)} new relevant articles")
                
                time.sleep(interval_seconds)
            
            except KeyboardInterrupt:
                logger.info("Watchdog stopped by user")
                break
            except Exception as e:
                logger.error(f"Watchdog error: {e}")
                time.sleep(60)  # Wait before retry
    
    def stop(self):
        """Stop the watchdog"""
        self.is_running = False


# Example callback function
def print_alert(article: NewsArticle):
    """Simple callback to print new article alerts"""
    print(f"\n{'='*60}")
    print(f"NEW ARTICLE ALERT - Relevance: {article.relevance_score:.1f}")
    print(f"{'='*60}")
    print(f"Title: {article.title}")
    print(f"Source: {article.source}")
    print(f"URL: {article.url}")
    print(f"Keywords: {', '.join(article.matched_keywords[:5])}")
    print(f"{'='*60}\n")


if __name__ == "__main__":
    # Test the news aggregator
    print("=" * 60)
    print("Testing Moroccan News Aggregator")
    print("=" * 60)
    
    aggregator = NewsAggregator()
    
    # Test RSS sources
    print("\n--- Testing RSS Sources ---")
    rss_sources = [k for k, v in NEWS_SOURCES.items() if v.get("rss_url")]
    print(f"RSS sources available: {rss_sources}")
    
    # Scrape all sources
    print("\n--- Scraping All Sources ---")
    articles = aggregator.scrape_all(max_per_source=5, min_relevance=0)
    print(f"Total articles scraped: {len(articles)}")
    
    # Show top stories
    print("\n--- Top 5 Most Relevant Stories ---")
    for i, article in enumerate(aggregator.get_top_stories(5), 1):
        print(f"\n{i}. [{article.relevance_score:.1f}] {article.title[:80]}...")
        print(f"   Source: {article.source}")
        print(f"   Keywords: {', '.join(article.matched_keywords[:5])}")
    
    # Summary report
    print("\n--- Summary Report ---")
    report = aggregator.get_summary_report()
    print(f"Total articles: {report['total_articles']}")
    print(f"Average relevance: {report['avg_relevance']:.1f}")
    print(f"High relevance (>50): {report['high_relevance_count']}")
    print(f"\nTop keywords: {report['top_keywords'][:10]}")
    
    # Export to JSON
    print("\n--- Exporting to JSON ---")
    aggregator.export_to_json("data/news_data.json")
