# 📊 MarketPulse: Real-Time Sentiment & Price Anomaly Detection System

MarketPulse is an advanced real-time financial market analysis platform that combines technical price analysis with financial news sentiment analysis to detect anomalies and predict market movements. This is a true Big Data project that processes both structured (stock prices) and unstructured data (news/social sentiment) in real-time, satisfying the "Velocity" and "Variety" pillars of Big Data.

## 🚀 High-Level Architecture

The data flows through the system as follows:

```
MarketPulse/
│
├── docker-compose.yml          # Docker configuration for Kafka, Spark, Cassandra
├── requirements.txt            # Python dependencies
├── README.md                   # Project documentation
│
├── data/                       # Data storage
│   ├── raw/                    # Raw downloaded data
│   │   ├── news_data.csv
│   │   └── stock_prices.csv
│   └── processed/              # Processed data
│
├── models/                     # Trained AI models
│   ├── lstm_model.h5
│   └── finbert_sentiment/
│
├── producers/                  # Scripts that SEND data to Kafka
│   ├── __init__.py
│   ├── price_producer.py       # Fetches and sends stock prices
│   └── news_producer.py        # Fetches and sends financial news
│
├── processors/                 # Spark scripts that PROCESS data
│   ├── __init__.py
│   └── spark_processor.py      # Real-time stream processing and anomaly detection
│
├── ml_models/                  # Scripts for creating AI models
│   ├── __init__.py
│   ├── train_lstm.py           # Trains price prediction model
│   └── train_sentiment.py      # Trains sentiment analysis model
│
├── dashboard/                  # Visualization interface
│   ├── app.py                  # Streamlit dashboard application
│   └── components/
│       ├── charts.py
│       └── alerts.py
│
├── notebooks/                  # Jupyter notebooks for exploration
│   ├── 01_data_exploration.ipynb
│   ├── 02_model_training.ipynb
│   └── 03_testing.ipynb
│
├── config/                     # Configuration files
│   ├── kafka_config.py
│   ├── spark_config.py
│   └── cassandra_config.py
│
└── utils/                      # Utility functions
    ├── __init__.py
    ├── data_loader.py
    └── helpers.py
```

## 🎯 Key Features

- **Real-time Data Processing**: Apache Kafka for high-throughput data streams
- **Big Data Processing**: Apache Spark for distributed stream processing
- **Anomaly Detection**: Identifies unusual market patterns combining price and sentiment
- **Sentiment Analysis**: FinBERT for financial news sentiment classification
- **Price Prediction**: LSTM neural networks for price forecasting
- **Time-series Storage**: Cassandra optimized for time-series financial data
- **Interactive Dashboard**: Real-time alerts and visualization

## 🛠️ Technology Stack

| Component | Tool | Purpose |
|-----------|------|---------|
| **Ingestion** | Apache Kafka | Handles high-throughput data streams, decouples producers from consumers |
| **Processing** | Apache Spark | Distributed processing engine with Structured Streaming |
| **Storage** | Cassandra | NoSQL database optimized for heavy write-loads and time-series data |
| **AI/ML** | PyTorch/TensorFlow | Build prediction models |
| **NLP** | FinBERT | Pre-trained BERT model specifically for financial sentiment |
| **Visualization** | Streamlit | Interactive dashboard for real-time alerts |
| **Orchestration** | Docker | Containerize services for easy deployment |

## 🚀 Getting Started

### Prerequisites

- Python 3.8+
- pip
- Docker Desktop (optional, for full system deployment)

### Installation

1. Clone the repository
2. Install Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```

### Option 1: Local Development (Recommended for Phase 1)
For academic projects and quick development, use local PySpark:

1. Install PySpark locally:
   ```bash
   pip install pyspark==3.5.0
   ```

2. Run the system components directly:
   ```bash
   # Start the data producers
   python producers/price_producer.py
   python producers/news_producer.py

   # Run the Spark processor for anomaly detection (local mode)
   python processors/spark_processor.py

   # Launch the dashboard
   streamlit run dashboard/app.py
   ```

### Option 2: Full System Deployment with Docker (For Production)
For the complete Big Data pipeline:

1. Start all services:
   ```bash
   docker-compose up -d
   ```

2. If Docker is not available, you can run individual components:
   - Kafka and Zookeeper: Download from Apache Kafka website
   - Spark: Download from Apache Spark website
   - Cassandra: Download from Apache Cassandra website

3. Verify services are running:
   - Spark UI: `http://localhost:8080`
   - Kafka UI: `http://localhost:8082`
   - Cassandra: Port `9042`
   - Spark History Server: `http://localhost:18080`

### Running the System Components

1. **Start the data producers:**
   ```bash
   python producers/price_producer.py
   python producers/news_producer.py
   ```

2. **Start the Spark processor for anomaly detection:**
   ```bash
   python processors/spark_processor.py
   ```

3. **Launch the dashboard:**
   ```bash
   streamlit run dashboard/app.py
   ```

4. **Run the analysis notebooks:**
   - Launch Jupyter: `jupyter notebook`
   - Open and run the notebooks in the `notebooks/` directory

### System Architecture

The MarketPulse system follows a complete Big Data architecture:

1. **Ingestion Layer:** Kafka producers collect real-time stock prices and financial news
2. **Processing Layer:** Spark Structured Streaming processes data streams and detects anomalies
3. **Storage Layer:** Cassandra stores time-series financial data and analysis results
4. **AI/ML Layer:** LSTM and FinBERT models analyze patterns and predict anomalies
5. **Visualization Layer:** Streamlit dashboard provides real-time monitoring and alerts

### Anomaly Detection Features

The system implements multiple anomaly detection methods:
- Statistical anomalies using z-score calculations
- Multimodal analysis combining price and sentiment data
- Divergence detection between sentiment and price movements
- Real-time alerting for detected anomalies

## 📋 Development Approach

### For Academic Projects (Phase 1)
Use the local development approach:
- ✅ Faster setup (5 minutes vs 2+ hours)
- ✅ Less complexity
- ✅ Sufficient for demonstrating concepts
- ✅ Works with limited RAM

### For Production Deployment (Phase 2-4)
Use the Docker approach:
- ✅ Complete Big Data pipeline
- ✅ Scalable architecture
- ✅ Production-ready
- ✅ All services integrated

## 🚀 Quick Start Without Docker (Recommended for Academic Projects)

### 📋 Quick Setup (5 minutes)

#### Step 1: Install Dependencies
```bash
pip install -r requirements.txt
```

#### Step 2: Install PySpark Locally
```bash
pip install pyspark==3.5.0
```

---

### 🎯 Run the System Components

#### Option A: Run All Components Separately (Recommended)

**Terminal 1 - Start Price Producer:**
```bash
python producers/price_producer.py
```

**Terminal 2 - Start News Producer:**
```bash
python producers/news_producer.py
```

**Terminal 3 - Start Spark Processor:**
```bash
python processors/spark_processor.py
```

**Terminal 4 - Start Dashboard:**
```bash
streamlit run dashboard/app.py
```

#### Option B: Run Individual Components

**Just the Dashboard (with simulated data):**
```bash
streamlit run dashboard/app.py
```
> *This will work immediately with simulated data*

**Just the Data Producers:**
```bash
python producers/price_producer.py
python producers/news_producer.py
```

**Just the Processing:**
```bash
python processors/spark_processor.py
```

---

### 🌐 Access the Dashboard

Open your browser and go to:
```
http://localhost:8501
```

---

### 📊 What You'll See

- **Real-time stock prices** (simulated or real)
- **Anomaly detection** markers
- **Sentiment analysis** charts
- **Multimodal analysis** signals
- **Live alerts** for detected anomalies

---

### 🧪 Run Analysis Notebooks

```bash
# Start Jupyter
jupyter notebook

# Then open and run:
notebooks/01_data_exploration.ipynb
notebooks/02_model_training.ipynb
notebooks/03_testing.ipynb
notebooks/04_multimodal_analysis.ipynb
```

---

### ⚡ Quick Test

To verify everything works:

1. **Start dashboard only:**
   ```bash
   streamlit run dashboard/app.py
   ```

2. **Open browser at `http://localhost:8501`**

3. **You should see:**
   - AAPL stock data (simulated)
   - Price charts with anomalies
   - Sentiment analysis
   - Anomaly alerts

---

### 🚀 Complete Workflow

1. **Start producers** → Generate data
2. **Run processor** → Analyze data and detect anomalies
3. **Launch dashboard** → Visualize results
4. **Monitor alerts** → Real-time anomaly detection

---

### 📝 No Docker Required

✅ All components work locally
✅ Uses simulated data when external services unavailable
✅ Full functionality preserved
✅ Perfect for academic projects

## 📊 System Flow

1. **Ingestion**: Python scripts fetch data from APIs and push to Apache Kafka
2. **Processing**: Apache Spark consumes Kafka streams, cleans data, and calculates rolling averages
3. **Storage**: Processed data stored in Cassandra (optimized for time-series)
4. **AI Analysis**: Hybrid models (LSTM + FinBERT) detect anomalies and generate signals
5. **Visualization**: Dashboard shows live alerts and analytics

## 🤝 Contributing

Contributions are welcome! Please open an issue to discuss changes you wish to make.

## 📄 License

This project is licensed under the MIT License.# MarketPulse
