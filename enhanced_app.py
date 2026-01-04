"""
MarketPulse Enhanced Dashboard: Advanced Stock Market Analysis & Prediction System
Features: Candlestick charts, Technical indicators, Correlation analysis, News sentiment, Portfolio management
"""

import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import json
import sys
import os

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import Morocco stocks data
from dashboard.morocco_stocks_data import (
    MOROCCO_STOCKS_DETAILED,
    MOROCCO_STOCKS,
    MOROCCO_SECTORS,
    MOROCCO_DATA_SOURCES,
    PREDICTION_FEATURES,
    get_stock_info,
    format_price_mad,
    get_currency_symbol
)

# Set page config FIRST
st.set_page_config(
    page_title="MarketPulse Pro Dashboard",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling (supports both light and dark themes)
st.markdown("""
<style>
    .main .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
    }

    /* Light theme support for metric boxes */
    [data-testid="stMetricValue"] {
        font-weight: 600;
    }

    /* Ensure metric boxes have good contrast in both themes */
    div[data-testid="metric-container"] {
        background-color: rgba(240, 242, 246, 0.05);
        border: 1px solid rgba(49, 51, 63, 0.2);
        padding: 15px;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }

    /* Light theme: darker text for better readability */
    @media (prefers-color-scheme: light) {
        div[data-testid="metric-container"] {
            background-color: rgba(240, 242, 246, 0.8);
            border: 1px solid rgba(49, 51, 63, 0.15);
        }
        [data-testid="stMetricLabel"] {
            color: #31333F !important;
        }
        [data-testid="stMetricValue"] {
            color: #0E1117 !important;
        }
        h1, h2, h3 {
            color: #0E1117 !important;
        }
    }

    /* Dark theme colors */
    @media (prefers-color-scheme: dark) {
        div[data-testid="metric-container"] {
            background-color: rgba(30, 33, 48, 0.8);
            border: 1px solid rgba(49, 51, 63, 0.4);
        }
        h1 {
            color: #00d4aa !important;
        }
    }

    /* Tab styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    .stTabs [data-baseweb="tab"] {
        border-radius: 8px 8px 0px 0px;
        padding: 10px 16px;
    }

    /* News headlines - better contrast in light theme */
    .news-headline {
        padding: 10px;
        border-radius: 5px;
        margin: 5px 0;
        background-color: rgba(240, 242, 246, 0.3);
    }

    @media (prefers-color-scheme: light) {
        .news-headline {
            background-color: rgba(240, 242, 246, 0.9);
            border: 1px solid rgba(49, 51, 63, 0.1);
            color: #0E1117;
        }
    }

    /* Expandable sections */
    .streamlit-expanderHeader {
        font-weight: 600;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'watchlist' not in st.session_state:
    st.session_state.watchlist = ["AAPL", "GOOGL", "MSFT"]
if 'portfolio' not in st.session_state:
    st.session_state.portfolio = {}
if 'chart_settings' not in st.session_state:
    st.session_state.chart_settings = {
        'show_ma': True,
        'show_volume': True,
        'show_indicators': True,
        'chart_type': 'candlestick'
    }
if 'refresh_rate' not in st.session_state:
    st.session_state.refresh_rate = 60  # seconds
if 'is_morocco_market' not in st.session_state:
    st.session_state.is_morocco_market = False

# International stocks for comparison
INTERNATIONAL_STOCKS = ["AAPL", "GOOGL", "MSFT", "TSLA", "AMZN", "META", "NFLX", "NVDA"]

def get_technical_indicators(df):
    """Calculate technical indicators"""
    data = df.copy()

    # Simple Moving Averages
    data['SMA_20'] = data['close'].rolling(window=20).mean()
    data['SMA_50'] = data['close'].rolling(window=50).mean()
    data['SMA_200'] = data['close'].rolling(window=200).mean()

    # Exponential Moving Averages
    data['EMA_12'] = data['close'].ewm(span=12, adjust=False).mean()
    data['EMA_26'] = data['close'].ewm(span=26, adjust=False).mean()

    # MACD
    data['MACD'] = data['EMA_12'] - data['EMA_26']
    data['MACD_Signal'] = data['MACD'].ewm(span=9, adjust=False).mean()
    data['MACD_Hist'] = data['MACD'] - data['MACD_Signal']

    # RSI
    delta = data['close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    rs = gain / loss
    data['RSI'] = 100 - (100 / (1 + rs))

    # Bollinger Bands
    data['BB_Middle'] = data['close'].rolling(window=20).mean()
    bb_std = data['close'].rolling(window=20).std()
    data['BB_Upper'] = data['BB_Middle'] + (bb_std * 2)
    data['BB_Lower'] = data['BB_Middle'] - (bb_std * 2)

    # Stochastic Oscillator
    low_14 = data['low'].rolling(window=14).min()
    high_14 = data['high'].rolling(window=14).max()
    data['Stoch_K'] = 100 * ((data['close'] - low_14) / (high_14 - low_14))
    data['Stoch_D'] = data['Stoch_K'].rolling(window=3).mean()

    # ATR (Average True Range)
    high_low = data['high'] - data['low']
    high_close = np.abs(data['high'] - data['close'].shift())
    low_close = np.abs(data['low'] - data['close'].shift())
    ranges = pd.concat([high_low, high_close, low_close], axis=1)
    true_range = ranges.max(axis=1)
    data['ATR'] = true_range.rolling(window=14).mean()

    return data

def load_stock_data_simulation(symbol, days=90):
    """Generate realistic simulated stock data with technical indicators"""
    import random

    data = []
    base_price = random.uniform(50, 500)
    volume_base = random.randint(1000000, 10000000)

    for i in range(days, 0, -1):
        date = datetime.now() - timedelta(days=i)

        # Realistic price movements with trend
        trend = random.uniform(-0.001, 0.002)  # Slight upward bias
        volatility = random.uniform(-0.03, 0.03)
        change = trend + volatility

        open_price = base_price
        close_price = base_price * (1 + change)
        high_price = max(open_price, close_price) * (1 + abs(random.gauss(0, 0.01)))
        low_price = min(open_price, close_price) * (1 - abs(random.gauss(0, 0.01)))

        # Volume with occasional spikes
        volume_multiplier = random.uniform(0.7, 1.3)
        if random.random() < 0.05:  # 5% spike chance
            volume_multiplier = random.uniform(2, 5)
        volume = int(volume_base * volume_multiplier)

        # Anomaly detection
        z_score = random.gauss(0, 1)
        is_anomaly = abs(z_score) > 2.0

        data.append({
            'timestamp': date,
            'symbol': symbol,
            'open': open_price,
            'high': high_price,
            'low': low_price,
            'close': close_price,
            'volume': volume,
            'z_score': z_score,
            'is_anomaly': is_anomaly
        })

        base_price = close_price

    df = pd.DataFrame(data)
    df = get_technical_indicators(df)
    return df

def load_predictions_simulation(symbol, current_price, days=10):
    """Simulate model predictions"""
    import random

    predictions = []

    for i in range(days):
        date = datetime.now() + timedelta(days=i+1)

        # Different model predictions
        lstm_pred = current_price * (1 + random.gauss(0.01, 0.02))
        gru_pred = current_price * (1 + random.gauss(0.01, 0.018))
        transformer_pred = current_price * (1 + random.gauss(0.012, 0.022))
        ensemble_pred = (lstm_pred + gru_pred + transformer_pred) / 3

        predictions.append({
            'date': date,
            'lstm': lstm_pred,
            'gru': gru_pred,
            'transformer': transformer_pred,
            'ensemble': ensemble_pred,
            'confidence': random.uniform(0.7, 0.95)
        })

        current_price = ensemble_pred

    return pd.DataFrame(predictions)

def load_news_sentiment_simulation(symbol, days=30):
    """Simulate news sentiment data"""
    import random

    news_templates = [
        "{symbol} reports strong quarterly earnings",
        "{symbol} announces new product launch",
        "{symbol} faces regulatory challenges",
        "Market analysts upgrade {symbol} outlook",
        "{symbol} stock shows resilience amid market volatility",
        "Institutional investors increase {symbol} holdings",
        "{symbol} CEO discusses future strategy",
        "Economic indicators impact {symbol} performance"
    ]

    news_data = []

    for i in range(days * 2):  # 2 news items per day on average
        if random.random() < 0.5:  # 50% chance of news
            date = datetime.now() - timedelta(days=random.randint(0, days))
            headline = random.choice(news_templates).format(symbol=symbol)

            sentiment_score = random.gauss(0, 0.4)
            if sentiment_score > 0.3:
                sentiment_label = 'positive'
            elif sentiment_score < -0.3:
                sentiment_label = 'negative'
            else:
                sentiment_label = 'neutral'

            news_data.append({
                'timestamp': date,
                'headline': headline,
                'sentiment_score': sentiment_score,
                'sentiment_label': sentiment_label,
                'relevance': random.uniform(0.6, 1.0)
            })

    return pd.DataFrame(news_data).sort_values('timestamp', ascending=False)

def create_candlestick_chart(df, symbol, show_volume=True, show_ma=True, show_bb=True, currency="USD"):
    """Create advanced candlestick chart with indicators"""

    # Create subplots
    rows = 3 if show_volume else 2
    row_heights = [0.6, 0.2, 0.2] if show_volume else [0.7, 0.3]

    # Determine price label based on currency
    price_label = "Price (MAD)" if currency == "MAD" else "Price ($)"

    fig = make_subplots(
        rows=rows, cols=1,
        shared_xaxes=True,
        vertical_spacing=0.03,
        row_heights=row_heights,
        subplot_titles=(f'{symbol} Price Chart', 'Technical Indicators', 'Volume') if show_volume
                      else (f'{symbol} Price Chart', 'Technical Indicators')
    )

    # Candlestick
    fig.add_trace(
        go.Candlestick(
            x=df['timestamp'],
            open=df['open'],
            high=df['high'],
            low=df['low'],
            close=df['close'],
            name='OHLC',
            increasing_line_color='#00ff00',
            decreasing_line_color='#ff0000'
        ),
        row=1, col=1
    )

    # Moving Averages
    if show_ma and 'SMA_20' in df.columns:
        fig.add_trace(
            go.Scatter(x=df['timestamp'], y=df['SMA_20'],
                      name='SMA 20', line=dict(color='orange', width=1)),
            row=1, col=1
        )
        fig.add_trace(
            go.Scatter(x=df['timestamp'], y=df['SMA_50'],
                      name='SMA 50', line=dict(color='blue', width=1)),
            row=1, col=1
        )

    # Bollinger Bands
    if show_bb and 'BB_Upper' in df.columns:
        fig.add_trace(
            go.Scatter(x=df['timestamp'], y=df['BB_Upper'],
                      name='BB Upper', line=dict(color='gray', width=1, dash='dash'),
                      opacity=0.5),
            row=1, col=1
        )
        fig.add_trace(
            go.Scatter(x=df['timestamp'], y=df['BB_Lower'],
                      name='BB Lower', line=dict(color='gray', width=1, dash='dash'),
                      fill='tonexty', opacity=0.3),
            row=1, col=1
        )

    # Highlight anomalies
    if 'is_anomaly' in df.columns:
        anomalies = df[df['is_anomaly'] == True]
        if not anomalies.empty:
            fig.add_trace(
                go.Scatter(
                    x=anomalies['timestamp'],
                    y=anomalies['close'],
                    mode='markers',
                    marker=dict(color='red', size=12, symbol='x', line=dict(width=2)),
                    name='Anomalies'
                ),
                row=1, col=1
            )

    # RSI
    if 'RSI' in df.columns:
        fig.add_trace(
            go.Scatter(x=df['timestamp'], y=df['RSI'],
                      name='RSI', line=dict(color='purple', width=2)),
            row=2, col=1
        )
        # Overbought/Oversold lines
        fig.add_hline(y=70, line_dash="dash", line_color="red", opacity=0.5, row=2, col=1)
        fig.add_hline(y=30, line_dash="dash", line_color="green", opacity=0.5, row=2, col=1)

    # Volume
    if show_volume:
        colors = ['red' if row['close'] < row['open'] else 'green' for _, row in df.iterrows()]
        fig.add_trace(
            go.Bar(x=df['timestamp'], y=df['volume'],
                   name='Volume', marker_color=colors, opacity=0.5),
            row=3, col=1
        )

    # Update layout
    fig.update_layout(
        height=800,
        xaxis_rangeslider_visible=False,
        hovermode='x unified',
        template='plotly_dark',
        showlegend=True,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )

    # Update y-axes
    fig.update_yaxes(title_text=price_label, row=1, col=1)
    fig.update_yaxes(title_text="RSI", row=2, col=1, range=[0, 100])
    if show_volume:
        fig.update_yaxes(title_text="Volume", row=3, col=1)

    return fig

def create_macd_chart(df):
    """Create MACD indicator chart"""
    if 'MACD' not in df.columns:
        return None

    fig = go.Figure()

    # MACD Line
    fig.add_trace(go.Scatter(
        x=df['timestamp'], y=df['MACD'],
        name='MACD', line=dict(color='blue', width=2)
    ))

    # Signal Line
    fig.add_trace(go.Scatter(
        x=df['timestamp'], y=df['MACD_Signal'],
        name='Signal', line=dict(color='orange', width=2)
    ))

    # Histogram
    colors = ['green' if val > 0 else 'red' for val in df['MACD_Hist']]
    fig.add_trace(go.Bar(
        x=df['timestamp'], y=df['MACD_Hist'],
        name='Histogram', marker_color=colors, opacity=0.5
    ))

    fig.update_layout(
        title='MACD Indicator',
        xaxis_title='Date',
        yaxis_title='MACD',
        height=300,
        template='plotly_dark',
        hovermode='x unified'
    )

    return fig

def create_correlation_heatmap(symbols):
    """Create correlation matrix for multiple stocks"""
    # Simulate correlation data
    corr_matrix = np.random.rand(len(symbols), len(symbols))
    corr_matrix = (corr_matrix + corr_matrix.T) / 2  # Make symmetric
    np.fill_diagonal(corr_matrix, 1)  # Diagonal = 1

    fig = go.Figure(data=go.Heatmap(
        z=corr_matrix,
        x=symbols,
        y=symbols,
        colorscale='RdBu',
        zmid=0,
        text=np.round(corr_matrix, 2),
        texttemplate='%{text}',
        textfont={"size": 10},
        colorbar=dict(title="Correlation")
    ))

    fig.update_layout(
        title='Stock Correlation Matrix',
        height=500,
        template='plotly_dark'
    )

    return fig

def create_sentiment_timeline(news_df, price_df):
    """Create timeline showing news sentiment vs price"""
    fig = make_subplots(
        rows=2, cols=1,
        shared_xaxes=True,
        vertical_spacing=0.1,
        row_heights=[0.6, 0.4],
        subplot_titles=('Price Movement', 'News Sentiment')
    )

    # Price line
    fig.add_trace(
        go.Scatter(x=price_df['timestamp'], y=price_df['close'],
                  name='Close Price', line=dict(color='cyan', width=2)),
        row=1, col=1
    )

    # Sentiment scatter
    colors = news_df['sentiment_label'].map({
        'positive': 'green',
        'negative': 'red',
        'neutral': 'gray'
    })

    fig.add_trace(
        go.Scatter(
            x=news_df['timestamp'],
            y=news_df['sentiment_score'],
            mode='markers',
            marker=dict(
                size=news_df['relevance'] * 20,
                color=colors,
                opacity=0.7,
                line=dict(width=1, color='white')
            ),
            name='News Sentiment',
            text=news_df['headline'],
            hovertemplate='<b>%{text}</b><br>Sentiment: %{y:.2f}<extra></extra>'
        ),
        row=2, col=1
    )

    # Add sentiment zones
    fig.add_hrect(y0=0.3, y1=1.0, line_width=0, fillcolor="green", opacity=0.1, row=2, col=1)
    fig.add_hrect(y0=-1.0, y1=-0.3, line_width=0, fillcolor="red", opacity=0.1, row=2, col=1)

    fig.update_layout(
        height=600,
        template='plotly_dark',
        hovermode='x unified',
        showlegend=True
    )

    fig.update_yaxes(title_text="Price ($)", row=1, col=1)
    fig.update_yaxes(title_text="Sentiment Score", row=2, col=1, range=[-1, 1])

    return fig

def create_prediction_comparison(predictions_df):
    """Compare predictions from different models"""
    fig = go.Figure()

    # Add traces for each model
    fig.add_trace(go.Scatter(
        x=predictions_df['date'], y=predictions_df['lstm'],
        name='LSTM', mode='lines+markers', line=dict(color='blue', width=2)
    ))

    fig.add_trace(go.Scatter(
        x=predictions_df['date'], y=predictions_df['gru'],
        name='GRU', mode='lines+markers', line=dict(color='green', width=2)
    ))

    fig.add_trace(go.Scatter(
        x=predictions_df['date'], y=predictions_df['transformer'],
        name='Transformer', mode='lines+markers', line=dict(color='orange', width=2)
    ))

    fig.add_trace(go.Scatter(
        x=predictions_df['date'], y=predictions_df['ensemble'],
        name='Ensemble', mode='lines+markers',
        line=dict(color='red', width=3, dash='dash')
    ))

    fig.update_layout(
        title='Model Predictions Comparison',
        xaxis_title='Date',
        yaxis_title='Predicted Price ($)',
        height=400,
        template='plotly_dark',
        hovermode='x unified'
    )

    return fig

# ==================== MAIN DASHBOARD ====================

# Header
st.title("📈 MarketPulse Pro - Advanced Stock Market Analysis")
st.markdown("*Real-time market analysis with AI-powered predictions*")

# Sidebar
with st.sidebar:
    st.header("⚙️ Dashboard Settings")

    # Market selection
    market_type = st.radio(
        "Select Market",
        ["Morocco Stock Exchange (Casablanca)", "International Markets"],
        index=0  # Default to Morocco market
    )

    # Update session state
    st.session_state.is_morocco_market = market_type.startswith("Morocco")

    # Symbol selection based on market
    if st.session_state.is_morocco_market:
        stock_options = MOROCCO_STOCKS
        selected_symbol = st.selectbox(
            "📊 Select Stock Symbol",
            stock_options,
            index=0,
            format_func=lambda x: x  # Display full "TICKER - Company Name"
        )
        # Extract ticker from selection
        ticker_symbol = selected_symbol.split(" - ")[0] if " - " in selected_symbol else selected_symbol
        stock_info = get_stock_info(ticker_symbol)
    else:
        stock_options = INTERNATIONAL_STOCKS
        selected_symbol = st.selectbox(
            "📊 Select Stock Symbol",
            stock_options,
            index=0
        )
        ticker_symbol = selected_symbol
        stock_info = {"name": selected_symbol, "sector": "International", "currency": "USD"}

    # Display stock information
    if st.session_state.is_morocco_market:
        st.info(f"""
        **Company:** {stock_info['name']}
        **Sector:** {stock_info['sector']}
        **Currency:** {stock_info['currency']}
        """)

    # Time range
    time_range = st.selectbox(
        "📅 Time Range",
        ["1W", "1M", "3M", "6M", "1Y", "2Y"],
        index=2
    )

    time_map = {"1W": 7, "1M": 30, "3M": 90, "6M": 180, "1Y": 365, "2Y": 730}
    days = time_map[time_range]

    st.markdown("---")

    # Chart settings
    st.subheader("📈 Chart Settings")
    chart_type = st.selectbox(
        "Chart Type",
        ["Candlestick", "Line", "Area"]
    )

    show_volume = st.checkbox("Show Volume", value=True)
    show_ma = st.checkbox("Show Moving Averages", value=True)
    show_bb = st.checkbox("Show Bollinger Bands", value=True)
    show_indicators = st.checkbox("Show Technical Indicators", value=True)

    st.markdown("---")

    # Data Sources Section
    if st.session_state.is_morocco_market:
        with st.expander("📚 Data Sources"):
            st.markdown("### Official Sources")
            for name, url in MOROCCO_DATA_SOURCES["Official"].items():
                st.markdown(f"- [{name}]({url})")

            st.markdown("### Financial Portals")
            for name, url in MOROCCO_DATA_SOURCES["Financial Portals"].items():
                st.markdown(f"- [{name}]({url})")

            st.markdown("### News Sources")
            for name, url in MOROCCO_DATA_SOURCES["News Sources"].items():
                st.markdown(f"- [{name}]({url})")

    # Prediction Features Section
    with st.expander("🤖 AI Prediction Features"):
        st.markdown("### Features Used for Predictions")

        for category, features in PREDICTION_FEATURES.items():
            st.markdown(f"**{category}:**")
            for feature in features:
                st.markdown(f"- {feature}")

    st.markdown("---")

    # Watchlist
    st.subheader("👀 Watchlist")
    for stock in st.session_state.watchlist:
        col1, col2 = st.columns([3, 1])
        col1.write(stock)
        if col2.button("×", key=f"remove_{stock}"):
            st.session_state.watchlist.remove(stock)
            st.rerun()

    new_stock = st.text_input("Add to watchlist")
    if st.button("Add") and new_stock:
        if new_stock not in st.session_state.watchlist:
            st.session_state.watchlist.append(new_stock)
            st.rerun()

# Load data
with st.spinner("Loading market data..."):
    stock_data = load_stock_data_simulation(ticker_symbol, days)
    current_price = stock_data.iloc[-1]['close']
    predictions = load_predictions_simulation(ticker_symbol, current_price, 10)
    news_sentiment = load_news_sentiment_simulation(ticker_symbol, 30)

# Helper function to format prices based on currency
def format_price(price, currency="USD"):
    """Format price with appropriate currency symbol"""
    if currency == "MAD":
        return format_price_mad(price)
    else:
        return f"${price:.2f}"

# Key Metrics
col1, col2, col3, col4, col5 = st.columns(5)

latest_data = stock_data.iloc[-1]
prev_data = stock_data.iloc[-2]

price_change = latest_data['close'] - prev_data['close']
price_change_pct = (price_change / prev_data['close']) * 100

# Get currency for formatting
currency = stock_info['currency']

col1.metric(
    "Current Price",
    format_price(latest_data['close'], currency),
    f"{price_change:+.2f} ({price_change_pct:+.2f}%)"
)

col2.metric(
    "Volume",
    f"{latest_data['volume']:,.0f}",
    f"{((latest_data['volume'] - prev_data['volume']) / prev_data['volume'] * 100):+.1f}%"
)

col3.metric(
    "RSI",
    f"{latest_data['RSI']:.1f}" if 'RSI' in latest_data else "N/A",
    "Overbought" if latest_data.get('RSI', 50) > 70 else "Oversold" if latest_data.get('RSI', 50) < 30 else "Neutral"
)

col4.metric(
    "Predicted (1d)",
    format_price(predictions.iloc[0]['ensemble'], currency),
    f"{((predictions.iloc[0]['ensemble'] - current_price) / current_price * 100):+.2f}%"
)

anomaly_count = stock_data['is_anomaly'].sum()
col5.metric(
    "Anomalies",
    anomaly_count,
    "⚠️" if anomaly_count > 0 else "✓"
)

# Main content tabs
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "📊 Price Chart",
    "📈 Technical Indicators",
    "🤖 AI Predictions",
    "📰 News & Sentiment",
    "🔥 Correlation Analysis",
    "💼 Portfolio"
])

with tab1:
    st.subheader(f"Price Chart - {stock_info['name']} ({ticker_symbol})")

    # Main candlestick chart
    fig_candle = create_candlestick_chart(
        stock_data,
        ticker_symbol,
        show_volume=show_volume,
        show_ma=show_ma,
        show_bb=show_bb,
        currency=currency
    )
    st.plotly_chart(fig_candle, use_container_width=True)

    # Stats
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Open", format_price(latest_data['open'], currency))
    col2.metric("High", format_price(latest_data['high'], currency))
    col3.metric("Low", format_price(latest_data['low'], currency))
    col4.metric("Close", format_price(latest_data['close'], currency))

with tab2:
    st.subheader("Technical Indicators")

    # MACD
    if show_indicators:
        fig_macd = create_macd_chart(stock_data)
        if fig_macd:
            st.plotly_chart(fig_macd, use_container_width=True)

        # Indicator values
        col1, col2, col3, col4 = st.columns(4)

        col1.metric("RSI (14)", f"{latest_data['RSI']:.2f}" if 'RSI' in latest_data else "N/A")
        col2.metric("MACD", f"{latest_data['MACD']:.2f}" if 'MACD' in latest_data else "N/A")
        col3.metric("ATR (14)", f"{latest_data['ATR']:.2f}" if 'ATR' in latest_data else "N/A")
        col4.metric("Stoch %K", f"{latest_data['Stoch_K']:.2f}" if 'Stoch_K' in latest_data else "N/A")

        # Indicator explanation
        with st.expander("📚 Indicator Guide"):
            st.markdown("""
            **RSI (Relative Strength Index)**: Measures momentum
            - > 70: Overbought (potential sell signal)
            - < 30: Oversold (potential buy signal)

            **MACD (Moving Average Convergence Divergence)**: Trend-following indicator
            - MACD > Signal: Bullish
            - MACD < Signal: Bearish

            **Bollinger Bands**: Volatility indicator
            - Price near upper band: Overbought
            - Price near lower band: Oversold

            **ATR (Average True Range)**: Volatility measure
            - Higher values = More volatility
            """)

with tab3:
    st.subheader("🤖 AI Model Predictions")

    # Model comparison
    fig_predictions = create_prediction_comparison(predictions)
    st.plotly_chart(fig_predictions, use_container_width=True)

    # Prediction details
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("### 📊 Ensemble Prediction")
        next_pred = predictions.iloc[0]
        st.metric(
            "Next Day Prediction",
            f"${next_pred['ensemble']:.2f}",
            f"{((next_pred['ensemble'] - current_price) / current_price * 100):+.2f}%"
        )
        st.progress(next_pred['confidence'])
        st.caption(f"Confidence: {next_pred['confidence']:.1%}")

        st.markdown("### 📈 7-Day Forecast")
        weekly_pred = predictions.iloc[6]
        st.metric(
            "7-Day Prediction",
            f"${weekly_pred['ensemble']:.2f}",
            f"{((weekly_pred['ensemble'] - current_price) / current_price * 100):+.2f}%"
        )

    with col2:
        st.markdown("### 🎯 Model Performance")

        # Simulated model metrics
        metrics_data = {
            'Model': ['LSTM', 'GRU', 'Transformer', 'Ensemble'],
            'RMSE': [2.34, 2.28, 2.41, 1.95],
            'MAE': [1.87, 1.82, 1.95, 1.54],
            'R²': [0.92, 0.93, 0.91, 0.95],
            'Dir. Acc.': ['87%', '88%', '85%', '91%']
        }

        st.dataframe(
            pd.DataFrame(metrics_data),
            use_container_width=True,
            hide_index=True
        )

    # Prediction table
    st.markdown("### 📅 Detailed Predictions")
    pred_table = predictions[['date', 'ensemble', 'confidence']].copy()
    pred_table['date'] = pred_table['date'].dt.strftime('%Y-%m-%d')
    price_col_name = f'Predicted Price ({currency})'
    pred_table.columns = ['Date', price_col_name, 'Confidence']
    pred_table[price_col_name] = pred_table[price_col_name].apply(lambda x: format_price(x, currency))
    st.dataframe(pred_table, use_container_width=True, hide_index=True)

with tab4:
    st.subheader("📰 News & Sentiment Analysis")

    if not news_sentiment.empty:
        # Sentiment timeline
        fig_sentiment = create_sentiment_timeline(news_sentiment, stock_data)
        st.plotly_chart(fig_sentiment, use_container_width=True)

        # Sentiment summary
        col1, col2, col3 = st.columns(3)

        sentiment_counts = news_sentiment['sentiment_label'].value_counts()
        col1.metric("😊 Positive", sentiment_counts.get('positive', 0))
        col2.metric("😐 Neutral", sentiment_counts.get('neutral', 0))
        col3.metric("😟 Negative", sentiment_counts.get('negative', 0))

        # News feed
        st.markdown("### 📢 Latest News")
        for _, news in news_sentiment.head(10).iterrows():
            sentiment_color = {
                'positive': '🟢',
                'negative': '🔴',
                'neutral': '🟡'
            }.get(news['sentiment_label'], '⚪')

            st.markdown(f"""
            <div class="news-headline">
            <strong>{sentiment_color} {news['headline']}</strong><br>
            <em>{news['timestamp'].strftime('%Y-%m-%d %H:%M')} | Sentiment: {news['sentiment_score']:.2f} | Relevance: {news['relevance']:.0%}</em>
            </div>
            """, unsafe_allow_html=True)

with tab5:
    st.subheader("🔥 Market Correlation Analysis")

    # Correlation heatmap
    watchlist_symbols = st.session_state.watchlist[:10]  # Limit to 10
    fig_corr = create_correlation_heatmap(watchlist_symbols)
    st.plotly_chart(fig_corr, use_container_width=True)

    st.info("💡 Correlation values range from -1 (perfect negative) to +1 (perfect positive). Values near 0 indicate no correlation.")

    # Sector analysis
    st.markdown("### 📊 Sector Distribution")

    # Simulated sector data
    sector_data = pd.DataFrame({
        'Sector': ['Technology', 'Finance', 'Healthcare', 'Energy', 'Consumer'],
        'Weight': [35, 25, 20, 12, 8]
    })

    fig_sector = px.pie(
        sector_data,
        values='Weight',
        names='Sector',
        title='Portfolio Sector Allocation',
        template='plotly_dark'
    )
    st.plotly_chart(fig_sector, use_container_width=True)

with tab6:
    st.subheader("💼 Portfolio Management")

    col1, col2 = st.columns([2, 1])

    with col1:
        st.markdown("### 📊 Portfolio Overview")

        # Simulated portfolio
        if not st.session_state.portfolio:
            st.session_state.portfolio = {
                'AAPL': {'shares': 10, 'avg_price': 150.00},
                'GOOGL': {'shares': 5, 'avg_price': 140.00},
                'MSFT': {'shares': 8, 'avg_price': 350.00}
            }

        portfolio_data = []
        total_value = 0
        total_cost = 0

        for symbol, info in st.session_state.portfolio.items():
            current_price_sim = np.random.uniform(100, 500)  # Simulate current price
            shares = info['shares']
            avg_price = info['avg_price']

            current_value = shares * current_price_sim
            cost_basis = shares * avg_price
            gain_loss = current_value - cost_basis
            gain_loss_pct = (gain_loss / cost_basis) * 100

            total_value += current_value
            total_cost += cost_basis

            portfolio_data.append({
                'Symbol': symbol,
                'Shares': shares,
                'Avg Price': f"${avg_price:.2f}",
                'Current Price': f"${current_price_sim:.2f}",
                'Value': f"${current_value:.2f}",
                'Gain/Loss': f"${gain_loss:+.2f}",
                'Return': f"{gain_loss_pct:+.2f}%"
            })

        st.dataframe(pd.DataFrame(portfolio_data), use_container_width=True, hide_index=True)

        # Portfolio metrics
        total_gain = total_value - total_cost
        total_return = (total_gain / total_cost) * 100

        col1, col2, col3 = st.columns(3)
        col1.metric("Portfolio Value", f"${total_value:.2f}")
        col2.metric("Total Cost", f"${total_cost:.2f}")
        col3.metric("Total Return", f"${total_gain:+.2f}", f"{total_return:+.2f}%")

    with col2:
        st.markdown("### ➕ Add Position")

        new_symbol = st.text_input("Symbol")
        new_shares = st.number_input("Shares", min_value=1, value=1)
        new_price = st.number_input("Avg Price", min_value=0.01, value=100.00)

        if st.button("Add to Portfolio"):
            if new_symbol:
                st.session_state.portfolio[new_symbol] = {
                    'shares': new_shares,
                    'avg_price': new_price
                }
                st.success(f"Added {new_shares} shares of {new_symbol}")
                st.rerun()

# Footer
st.markdown("---")
col1, col2, col3 = st.columns(3)
col1.markdown("*MarketPulse Pro v2.0*")
col2.markdown("*Powered by Advanced AI Models*")
col3.markdown(f"*Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*")
