# 📁 MarketPulse Project Structure Guide

> **Complete guide to all components and where to edit them**

This document provides a comprehensive overview of the MarketPulse project structure, explaining where each component is located and what you need to edit for customization.

---

## 📂 Directory Overview

```
MarketPulse-GitHub/
├── config/                      # Configuration files
├── dashboard/                   # Streamlit web interface
├── ml_models/                   # Machine learning implementations
├── producers/                   # Kafka data producers
├── processors/                  # Spark stream processors
├── files/                       # Web scraping scripts
├── latex-submission/            # Academic report & presentation
├── docker-compose.enhanced.yml  # Production deployment
├── requirements.txt             # Python dependencies
└── README_ENHANCED.md          # Main project documentation
```

---

## 🎯 Quick Navigation by Task

### For Customization & Manual Editing

| What You Want to Edit | File Location | Line Numbers |
|----------------------|---------------|--------------|
| **Morocco Stock List** | `dashboard/morocco_stocks_data.py` | Lines 7-89 |
| **Data Sources URLs** | `dashboard/morocco_stocks_data.py` | Lines 120-139 |
| **Dashboard Theme/Colors** | `dashboard/enhanced_app.py` | Lines 40-120 |
| **ML Model Architecture** | `ml_models/enhanced_lstm.py` | Lines 80-150 |
| **Kafka Topics** | `config/kafka_config.py` | Lines 10-25 |
| **Database Schema** | `config/cassandra-init.cql` | All |
| **LaTeX Report Content** | `latex-submission/report.tex` | Lines 100-1400 |
| **LaTeX Presentation** | `latex-submission/presentation.tex` | Lines 50-950 |
| **Docker Services** | `docker-compose.enhanced.yml` | All |
| **Web Scraping Sources** | `files/stock_scraper.py` | Lines 20-100 |

---

## 📋 Detailed Component Breakdown

### 1. **Configuration Files** (`config/`)

#### `kafka_config.py`
**Purpose:** Kafka connection and topic configuration
**Edit to:**
- Change Kafka broker addresses
- Modify topic names
- Update partition settings

```python
# Lines 10-15: Broker configuration
KAFKA_BROKERS = ['localhost:9092']  # ← Edit this

# Lines 20-25: Topic names
STOCK_TOPIC = 'stock-prices'        # ← Edit this
NEWS_TOPIC = 'financial-news'       # ← Edit this
```

#### `spark_config.py`
**Purpose:** Spark processing configuration
**Edit to:**
- Adjust memory allocation
- Change number of executors
- Modify batch intervals

```python
# Lines 15-20: Spark resources
SPARK_EXECUTOR_MEMORY = '2g'        # ← Edit this
SPARK_DRIVER_MEMORY = '1g'          # ← Edit this
```

#### `cassandra-init.cql`
**Purpose:** Database schema definition
**Edit to:**
- Add new tables
- Modify column types
- Change primary keys or clustering

```sql
-- Lines 1-30: Stock prices table
CREATE TABLE stock_prices (
    symbol text,                     -- ← Add/modify columns
    timestamp timestamp,
    price_close decimal,
    ...
)
```

---

### 2. **Dashboard** (`dashboard/`)

#### `enhanced_app.py` (Main Dashboard - 1000+ lines)
**Purpose:** Interactive Streamlit web application
**Sections to edit:**

**Lines 40-120: CSS Styling**
```python
# Customize colors, fonts, theme
st.markdown("""
<style>
    .stMetric {
        background-color: #1e2130;  # ← Change colors
    }
</style>
""")
```

**Lines 530-595: Sidebar Configuration**
```python
# Lines 588-592: Market selection
market_type = st.radio(
    "Select Market",
    ["Morocco Stock Exchange", "International Markets"],  # ← Edit options
    index=0  # ← Change default
)
```

**Lines 640-780: Price Chart Tab**
- Edit to add new chart types
- Modify technical indicators displayed
- Change chart colors/styling

**Lines 782-840: Technical Indicators Tab**
- Add new indicators (Fibonacci, Ichimoku, etc.)
- Modify indicator calculations
- Change display format

**Lines 842-877: AI Predictions Tab**
- Modify which models to display
- Change prediction horizon (currently 7 days)
- Edit confidence interval visualization

**Lines 879-907: News & Sentiment Tab**
- Customize news source display
- Modify sentiment color coding
- Edit news feed layout

**Lines 909-934: Correlation Analysis Tab**
- Add new correlation matrices
- Change heatmap colors
- Modify sector groupings

**Lines 936-1007: Portfolio Management Tab**
- Customize portfolio metrics
- Add new position fields
- Modify P&L calculations

#### `morocco_stocks_data.py` (Morocco Market Data)
**Purpose:** Comprehensive Morocco stock information
**Critical sections:**

**Lines 7-89: Stock Details Dictionary**
```python
MOROCCO_STOCKS_DETAILED = {
    "ATW": {
        "name": "Attijariwafa Bank",  # ← Edit company names
        "sector": "Banking",           # ← Update sectors
        "currency": "MAD"              # ← Change currency
    },
    # ADD NEW STOCKS HERE
    "NEW": {
        "name": "New Company",
        "sector": "Technology",
        "currency": "MAD"
    }
}
```

**Lines 92-95: Stock Dropdown List**
```python
# This auto-generates from MOROCCO_STOCKS_DETAILED
# No need to edit manually
```

**Lines 98-110: Sector Groupings**
```python
MOROCCO_SECTORS = {
    "Banking": ["ATW", "BCP", ...],     # ← Add new sectors
    "New Sector": ["SYM1", "SYM2"],     # ← Add here
}
```

**Lines 120-139: Data Sources**
```python
MOROCCO_DATA_SOURCES = {
    "Official": {
        "Casablanca Stock Exchange": "https://...",  # ← Update URLs
        # ADD NEW SOURCES HERE
        "New Source": "https://newsource.com"
    }
}
```

**Lines 142-193: Prediction Features**
```python
PREDICTION_FEATURES = {
    "Price Data (OHLCV)": [...],       # ← Add new feature categories
    "New Category": [                   # ← Add here
        "Feature 1",
        "Feature 2"
    ]
}
```

---

### 3. **Machine Learning Models** (`ml_models/`)

#### `enhanced_lstm.py` (600+ lines)
**Purpose:** LSTM-based prediction models
**Key sections:**

**Lines 15-40: Model Hyperparameters**
```python
class EnhancedLSTMTrainer:
    def __init__(self,
                 sequence_length=60,      # ← Edit lookback period
                 lstm_units=[100, 50],    # ← Change layer sizes
                 dropout=0.2,             # ← Adjust dropout
                 learning_rate=0.001):    # ← Modify learning rate
```

**Lines 80-150: Model Architecture**
```python
def build_lstm_model(self):
    model.add(LSTM(100, ...))            # ← Add/remove layers
    model.add(Dropout(0.2))              # ← Change regularization
    model.add(Dense(1))                  # ← Modify output
```

**Lines 200-280: Feature Engineering**
```python
def create_features(self, df):
    # ADD NEW FEATURES HERE
    df['new_feature'] = ...              # ← Add custom features
    df['custom_indicator'] = ...         # ← Add indicators
```

**Lines 300-350: Training Configuration**
```python
def train(self):
    history = model.fit(
        epochs=50,                        # ← Change epochs
        batch_size=32,                    # ← Adjust batch size
        validation_split=0.2              # ← Modify val split
    )
```

#### `ensemble_model.py` (700+ lines)
**Purpose:** Ensemble of LSTM + GRU + Transformer
**Key sections:**

**Lines 50-120: Individual Model Architectures**
```python
def build_lstm_branch(self):
    # Edit LSTM architecture

def build_gru_branch(self):
    # Edit GRU architecture

def build_transformer_branch(self):
    # Edit Transformer architecture
```

**Lines 200-280: Meta-Learner**
```python
def build_meta_learner(self):
    # Combines predictions from all models
    # Edit combination strategy here
```

**Lines 400-450: Ensemble Training**
```python
def train_ensemble(self):
    # Train all models
    # Edit training order, epochs, etc.
```

#### `prediction_service.py` (400+ lines)
**Purpose:** Real-time prediction inference
**Key sections:**

**Lines 30-80: Model Loading**
```python
def load_models(self):
    # Load trained models
    # Edit model paths here
```

**Lines 150-220: Prediction Logic**
```python
def predict(self, symbol, days_ahead=7):  # ← Change forecast horizon
    # Generate predictions
```

**Lines 250-300: Confidence Intervals**
```python
def predict_with_confidence(self):
    # Monte Carlo Dropout for uncertainty
    # Edit number of iterations
```

---

### 4. **Data Producers** (`producers/`)

#### `morocco_stock_producer.py` (400+ lines)
**Purpose:** Fetches and publishes Morocco stock data to Kafka
**Key sections:**

**Lines 20-60: Scraper Integration**
```python
class MoroccoStockProducer:
    def __init__(self):
        self.scrapers = {
            'casablanca': CasablancaScraper(),  # ← Add new scrapers
            'bmce': BMCEScraper(),
            # ADD NEW SCRAPERS HERE
        }
```

**Lines 100-150: Data Collection**
```python
def fetch_stock_data(self, symbol):
    # Scrape from multiple sources
    # Edit priority, retry logic
```

**Lines 200-250: Kafka Publishing**
```python
def publish_to_kafka(self, data):
    # Send to Kafka topic
    # Edit topic, partition key
```

**Lines 300-350: Scheduling**
```python
def run_continuous(self):
    schedule.every(5).minutes.do(...)    # ← Change frequency
```

#### `news_producer.py` (300+ lines)
**Purpose:** Fetches news and publishes to Kafka
**Key sections:**

**Lines 30-80: News Sources**
```python
NEWS_SOURCES = [
    'https://www.medias24.com',          # ← Add new sources
    'https://www.lavieeco.com',
    # ADD NEW NEWS SOURCES HERE
]
```

**Lines 150-200: Sentiment Analysis**
```python
def analyze_sentiment(self, text):
    # FinBERT sentiment scoring
    # Edit model, threshold
```

---

### 5. **Stream Processors** (`processors/`)

#### `spark_processor.py` (500+ lines)
**Purpose:** Spark Structured Streaming for real-time processing
**Key sections:**

**Lines 50-100: Stream Source**
```python
df = spark \
    .readStream \
    .format("kafka") \
    .option("kafka.bootstrap.servers", "...")  # ← Edit Kafka config
    .option("subscribe", "stock-prices")       # ← Change topics
    .load()
```

**Lines 150-250: Stream Transformations**
```python
def process_stream(df):
    # Calculate technical indicators
    # ADD NEW CALCULATIONS HERE
    df = df.withColumn('new_metric', ...)
```

**Lines 300-350: Anomaly Detection**
```python
def detect_anomalies(df):
    # Z-score based detection
    # Edit threshold (currently ±3)
    threshold = 3.0                       # ← Modify threshold
```

**Lines 400-450: Sink Configuration**
```python
query = df \
    .writeStream \
    .format("cassandra") \
    .option("checkpointLocation", "...")  # ← Edit checkpoint path
    .start()
```

---

### 6. **Web Scraping Scripts** (`files/`)

#### `stock_scraper.py`
**Purpose:** Scrape stock prices from Morocco exchanges
**Edit to:**

**Lines 20-50: Target URLs**
```python
CASABLANCA_URL = "https://www.casablanca-bourse.com"  # ← Update URLs
BMCE_URL = "https://www.bmcek.co.ma"
# ADD NEW EXCHANGE URLs HERE
```

**Lines 100-200: HTML Parsing**
```python
def parse_stock_page(self, html):
    soup = BeautifulSoup(html)
    price = soup.find('div', class_='price')  # ← Update selectors
    # EDIT CSS SELECTORS FOR NEW SITES
```

**Lines 250-300: Data Validation**
```python
def validate_data(self, data):
    # Check for missing/invalid data
    # ADD CUSTOM VALIDATION RULES
```

#### `news_scraper.py`
**Purpose:** Scrape financial news
**Edit to:**

**Lines 30-80: News Site URLs**
```python
NEWS_SITES = {
    'medias24': 'https://www.medias24.com/marches',  # ← Add sites
    # ADD NEW NEWS SITES HERE
}
```

**Lines 150-250: Article Extraction**
```python
def extract_article(self, url):
    # Parse article HTML
    title = soup.find('h1')               # ← Update selectors
    content = soup.find('article')
```

---

### 7. **LaTeX Submission** (`latex-submission/`)

#### `report.tex` (1600+ lines, 44 pages)
**Purpose:** Academic technical report
**Sections to edit:**

**Lines 99-115: Title Page Information**
```latex
% Authors
Your Name\\              % ← CHANGE THIS
Student ID: 12345\\      % ← CHANGE THIS

% Supervisor
Supervisor Name\\        % ← CHANGE THIS

% Institution
Your University\\        % ← CHANGE THIS
```

**Lines 130-150: Abstract**
```latex
\begin{abstract}
MarketPulse is...        % ← EDIT ABSTRACT
\end{abstract}
```

**Lines 180-400: Introduction Section**
```latex
\section{Introduction}
% Edit introduction text, objectives, contributions
```

**Lines 1466-1590: Morocco Market Appendix**
```latex
\section{Morocco Stock Market Data}
% This section contains:
% - Stock tables (lines 1472-1505)
% - Data sources (lines 1507-1533)
% - Prediction features (lines 1535-1589)
% EDIT TO ADD MORE STOCKS OR FEATURES
```

#### `presentation.tex` (965 lines, 36 slides)
**Purpose:** Beamer presentation slides
**Sections to edit:**

**Lines 35-37: Title Slide**
```latex
\author{Your Name}       % ← CHANGE THIS
\institute{Your University \\ Department}  % ← CHANGE THIS
```

**Lines 240-284: Morocco Stocks Slide**
```latex
\begin{frame}{Morocco Stock Market Coverage}
    % Edit stock listings, add more sectors
\end{frame}
```

**Lines 286-325: Data Sources Slide**
```latex
\begin{frame}{Data Sources - Comprehensive Coverage}
    % Edit data source lists
\end{frame}
```

**Lines 397-467: Prediction Features Slides**
```latex
\begin{frame}{AI Prediction Features - 40+ Features}
    % Edit feature lists
\end{frame}
```

#### `compile.sh`
**Purpose:** Automated LaTeX compilation script
**No editing needed** - just run: `./compile.sh`

---

### 8. **Docker Deployment** (`docker-compose.enhanced.yml`)

**Purpose:** Production deployment orchestration
**Services configuration:**

**Lines 1-50: Service Overview**
```yaml
services:
  zookeeper:      # Kafka coordination
  kafka:          # Message broker
  spark-master:   # Spark cluster head
  spark-worker-1: # Spark executor
  spark-worker-2: # Spark executor
  cassandra:      # Database
  redis:          # Cache
  producer:       # Data producer
  processor:      # Stream processor
  dashboard:      # Web UI
  prometheus:     # Monitoring
```

**Lines 100-150: Kafka Configuration**
```yaml
kafka:
  environment:
    KAFKA_ADVERTISED_LISTENERS: ...        # ← Edit for remote access
    KAFKA_NUM_PARTITIONS: 3                # ← Change partitions
```

**Lines 200-250: Spark Configuration**
```yaml
spark-master:
  environment:
    SPARK_MASTER_MEMORY: 2g                # ← Adjust memory
```

**Lines 300-350: Cassandra Configuration**
```yaml
cassandra:
  environment:
    MAX_HEAP_SIZE: 1G                      # ← Adjust heap
    CASSANDRA_CLUSTER_NAME: MarketPulse    # ← Rename cluster
```

**Lines 450-500: Dashboard Service**
```yaml
dashboard:
  ports:
    - "8501:8501"                          # ← Change port
  environment:
    STREAMLIT_SERVER_PORT: 8501
```

---

## 🔧 Common Customization Tasks

### **Add a New Stock to Morocco List**

1. **Edit:** `dashboard/morocco_stocks_data.py`
2. **Location:** Lines 7-89 (MOROCCO_STOCKS_DETAILED dictionary)
3. **Add:**
```python
"NEW": {
    "name": "New Company Name",
    "sector": "Your Sector",
    "currency": "MAD"
}
```
4. **Update sector grouping:** Lines 98-110

### **Change Dashboard Colors/Theme**

1. **Edit:** `dashboard/enhanced_app.py`
2. **Location:** Lines 40-120 (CSS section)
3. **Modify:**
```python
st.markdown("""
<style>
    div[data-testid="metric-container"] {
        background-color: #YOUR_COLOR;  # ← Change
    }
</style>
""")
```

### **Add a New Data Source**

1. **Edit:** `dashboard/morocco_stocks_data.py`
2. **Location:** Lines 120-139
3. **Add:**
```python
MOROCCO_DATA_SOURCES = {
    "Official": {
        "New Source": "https://newsource.com"  # ← Add here
    }
}
```

### **Modify ML Model Architecture**

1. **Edit:** `ml_models/enhanced_lstm.py`
2. **Location:** Lines 80-150
3. **Change:**
```python
model.add(LSTM(200, ...))  # Increase units from 100 to 200
model.add(Dense(50))       # Add new layer
```

### **Change Prediction Horizon**

1. **Edit:** `ml_models/prediction_service.py`
2. **Location:** Line 152
3. **Modify:**
```python
def predict(self, symbol, days_ahead=14):  # Change from 7 to 14
```

### **Add New Technical Indicator**

1. **Edit:** `dashboard/enhanced_app.py`
2. **Location:** Lines 87-180 (get_technical_indicators function)
3. **Add:**
```python
# Fibonacci Retracement
data['fib_236'] = ...
data['fib_382'] = ...
```

### **Update Personal Info in LaTeX**

1. **Edit:** `latex-submission/report.tex`
2. **Location:** Lines 99-115
3. **Replace:**
```latex
Your Name\\              % Line 100
Student ID: 12345\\      % Line 101
Your University\\        % Line 106
```

### **Add New Kafka Topic**

1. **Edit:** `config/kafka_config.py`
2. **Location:** Lines 20-25
3. **Add:**
```python
NEW_TOPIC = 'new-data-topic'
```

### **Change Database Schema**

1. **Edit:** `config/cassandra-init.cql`
2. **Add new table:**
```sql
CREATE TABLE new_table (
    id uuid PRIMARY KEY,
    data text,
    timestamp timestamp
);
```

### **Modify Scraping Frequency**

1. **Edit:** `producers/morocco_stock_producer.py`
2. **Location:** Line 340
3. **Change:**
```python
schedule.every(10).minutes.do(...)  # Change from 5 to 10 minutes
```

---

## 📝 Files You Should NEVER Edit

These files are auto-generated or system files:

- `*.pyc` - Python bytecode (compiled)
- `__pycache__/` - Python cache directory
- `*.aux`, `*.log`, `*.toc`, `*.out` - LaTeX auxiliary files
- `*.pdf` - Compiled PDFs (edit .tex instead)
- `.DS_Store` - macOS system file
- `logs/` - Application logs

---

## 🚀 Quick Start for Manual Editing

### 1. **Before You Start**
```bash
cd MarketPulse-GitHub
git init
git add .
git commit -m "Initial commit"
```

### 2. **Make Your Changes**
- Use this guide to locate the file
- Edit using your favorite editor (VS Code, PyCharm, etc.)
- Test locally before committing

### 3. **Test Your Changes**

**Dashboard:**
```bash
streamlit run dashboard/enhanced_app.py
# Open http://localhost:8501
```

**ML Models:**
```bash
python ml_models/enhanced_lstm.py
```

**LaTeX:**
```bash
cd latex-submission
./compile.sh
```

**Docker Stack:**
```bash
docker-compose -f docker-compose.enhanced.yml up
```

### 4. **Commit Changes**
```bash
git add <modified-files>
git commit -m "Description of changes"
git push origin main
```

---

## 📚 Additional Documentation

- **Main README:** `README_ENHANCED.md` - Project overview and setup
- **Deployment Guide:** `DEPLOYMENT_GUIDE.md` - Production deployment steps
- **LaTeX Guide:** `latex-submission/README.md` - LaTeX compilation help
- **Screenshot Guide:** `latex-submission/SCREENSHOT_GUIDE.md` - Dashboard screenshots
- **Submission Checklist:** `latex-submission/SUBMISSION_CHECKLIST.md` - Pre-submission tasks

---

## 🎓 Educational Notes

### **Project Architecture Pattern**
This project follows a **Lambda Architecture** pattern:
- **Batch Layer:** Historical data processing (ML training)
- **Speed Layer:** Real-time streaming (Kafka + Spark)
- **Serving Layer:** Query interface (Cassandra + Dashboard)

### **Key Design Decisions**

1. **Why Kafka?** - Decouples data producers from consumers, enables replay
2. **Why Spark Streaming?** - Scalable stream processing with exactly-once semantics
3. **Why Cassandra?** - Optimized for time-series data, horizontal scalability
4. **Why Ensemble Models?** - Reduces variance, improves robustness
5. **Why Streamlit?** - Rapid prototyping, Python-native, reactive updates

---

## 🛠️ Troubleshooting

### **Can't Find a Component?**
Use grep to search:
```bash
grep -r "function_name" .
grep -r "class_name" .
```

### **File Path Confusion?**
This guide uses paths relative to `MarketPulse-GitHub/`

### **Want to See Full Code?**
All files are text-based - open with any editor

---

## 📞 Need Help?

- Check inline code comments (most files have detailed comments)
- See docstrings in Python functions
- Review LaTeX comments (lines starting with %)
- Consult the main README files

---

**Last Updated:** January 2026
**Project Version:** 2.0
**Total Files:** 50+
**Total Lines of Code:** 15,000+

---

## ✨ Happy Coding!

This project is yours to customize and extend. The structure is designed to be modular - change one component without breaking others. Good luck with your GitHub upload and future development!
