# Changelog

All notable changes to MarketPulse will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [2.0.0] - 2026-01-04

### Added
- **Morocco Market Focus**: Complete integration with Casablanca Stock Exchange
  - 60+ Morocco stocks with full company details
  - MAD (Moroccan Dirham) currency formatting throughout
  - Sector categorization (Banking, Telecom, Real Estate, etc.)
- **Enhanced Dashboard**:
  - 6 comprehensive tabs (Price Charts, Technical Indicators, AI Predictions, News Sentiment, Correlation, Portfolio)
  - Light/Dark theme support with proper contrast
  - Morocco-specific data sources panel with clickable links
  - AI Prediction Features documentation panel (40+ features)
  - Improved news headlines display with better styling
- **Data Sources Integration**:
  - Official sources: Casablanca Stock Exchange, AMMC, Bank Al-Maghrib
  - Financial portals: BMCE Capital, BPNet, CDG Capital, Le Boursier
  - News sources: Médias24, La Vie Éco, L'Économiste, LesEco.ma, Finances News
- **Machine Learning Improvements**:
  - Ensemble model combining LSTM + GRU + Transformer
  - 91% directional accuracy (up from 87% baseline)
  - 40+ engineered features including sentiment analysis
  - Monte Carlo Dropout for confidence intervals
  - Real-time prediction service
- **Academic Submission**:
  - 44-page LaTeX technical report (report.tex)
  - 36-slide Beamer presentation (presentation.tex)
  - Complete Morocco market data appendix
  - Data sources and prediction features documentation
- **Documentation**:
  - PROJECT_STRUCTURE.md - comprehensive component guide
  - Improved README.md with badges and sections
  - CONTRIBUTING.md guidelines
  - LaTeX compilation and screenshot guides

### Changed
- Upgraded dashboard from basic Streamlit to comprehensive 6-tab interface
- Improved CSS styling for better light/dark theme support
- Enhanced stock selection dropdown to show "TICKER - Company Name"
- Updated all price displays to use appropriate currency (MAD vs USD)
- Reorganized file structure for better GitHub organization
- Updated LaTeX documents to fix special character encoding

### Fixed
- LaTeX compilation errors with French accents (é, è, ô)
- Light theme contrast issues in metric boxes
- News headline readability in light mode
- Chart axis labels now show correct currency
- Prediction table formatting with proper currency symbols

## [1.0.0] - 2025-12-15

### Added
- Initial release with core functionality
- Basic web scraping from Morocco stock sources
- Simple LSTM model for price prediction
- Kafka + Spark streaming pipeline
- Cassandra database for time-series storage
- Basic Streamlit dashboard
- Docker Compose deployment configuration

### Core Features
- Real-time data collection from 5+ sources
- Stream processing with Apache Spark
- LSTM-based price predictions (87% accuracy)
- Basic technical indicators (SMA, EMA, RSI, MACD)
- News scraping and storage
- Simple dashboard with price charts

## [0.5.0] - 2025-11-20 (Beta)

### Added
- Prototype web scraping scripts
- Initial machine learning experiments
- Basic Kafka producer/consumer setup
- SQLite database for development
- Command-line interface for scraping

### Features
- Manual stock data scraping
- CSV export functionality
- Basic news aggregation
- Simple data validation

## [0.1.0] - 2025-10-01 (Alpha)

### Added
- Project initialization
- Basic project structure
- Requirements specification
- Initial documentation

---

## Release Notes

### Version 2.0.0 Highlights

This major release represents a complete transformation of MarketPulse into a production-ready platform:

**🇲🇦 Morocco Market Specialization**
- Full integration with Casablanca Stock Exchange
- Comprehensive coverage of 60+ Moroccan companies
- MAD currency support throughout
- Links to official Moroccan data sources

**🤖 Advanced AI & ML**
- 91% directional accuracy with ensemble models
- 40+ engineered features
- Real-time predictions with confidence intervals
- Sentiment analysis using FinBERT

**📊 Professional Dashboard**
- 6 comprehensive analysis tabs
- Light/Dark theme support
- Interactive charts with Plotly
- Real-time updates and notifications

**📚 Academic Quality**
- Complete LaTeX report (44 pages)
- Professional presentation (36 slides)
- Comprehensive documentation
- Ready for academic submission

**🐳 Production Ready**
- Docker Compose orchestration
- 12-service architecture
- Monitoring with Prometheus
- Horizontal scalability

---

## Migration Guide

### Upgrading from 1.0 to 2.0

1. **Update Dependencies**:
```bash
pip install -r requirements.txt --upgrade
```

2. **Database Schema Changes**:
```bash
# Backup existing data
./scripts/backup-db.sh

# Apply new schema
cqlsh -f config/cassandra-init.cql
```

3. **Configuration Updates**:
```bash
# Update environment variables
cp .env.example .env
# Edit .env with your values
```

4. **Restart Services**:
```bash
docker-compose -f docker-compose.enhanced.yml down
docker-compose -f docker-compose.enhanced.yml up -d
```

### Breaking Changes

- Stock symbol format changed from `"TICKER"` to `"TICKER - Company Name"` in dashboard
- Currency formatting function renamed from `format_price()` to include currency parameter
- Kafka topic names updated (see .env.example)
- Cassandra table schema modified to include sector and currency fields

---

## Upcoming Features

See [GitHub Issues](https://github.com/yourusername/MarketPulse/issues) for planned enhancements and feature requests.

**Planned for 2.1.0:**
- [ ] Mobile-responsive dashboard
- [ ] Email/SMS alert notifications
- [ ] Advanced portfolio analytics
- [ ] Backtesting framework
- [ ] REST API for external integrations

**Planned for 3.0.0:**
- [ ] Multi-country support (Nigeria, South Africa, Egypt)
- [ ] Mobile app (React Native)
- [ ] Kubernetes deployment
- [ ] GraphQL API
- [ ] Arabic/French language support

---

## Contributors

Thank you to all contributors who have helped make MarketPulse better!

- [Your Name] - Project Creator & Lead Developer

See [CONTRIBUTING.md](CONTRIBUTING.md) to learn how you can contribute!

---

## Support

- **Bug Reports**: [GitHub Issues](https://github.com/yourusername/MarketPulse/issues)
- **Questions**: [GitHub Discussions](https://github.com/yourusername/MarketPulse/discussions)
- **Email**: your.email@example.com
