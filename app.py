"""
MarketPulse Dashboard: Real-Time Sentiment & Price Anomaly Detection System
"""

import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import uuid
import json

# Set page config
st.set_page_config(
    page_title="MarketPulse Dashboard",
    page_icon="🚨",
    layout="wide"
)

# Initialize session state
if 'connected' not in st.session_state:
    st.session_state.connected = False

# Title
st.title("🚨 MarketPulse: Real-Time Sentiment & Price Anomaly Detection System")

# Sidebar
st.sidebar.header("Configuration")

# Connect to Cassandra (with error handling for Python 3.12 compatibility)
def connect_to_cassandra():
    try:
        # Try to import cassandra
        from cassandra.cluster import Cluster
        cluster = Cluster(['localhost'])  # Update with your Cassandra host
        session = cluster.connect()
        session.execute("USE market_pulse")
        return session
    except ImportError as e:
        st.error(f"Erreur d'importation du driver Cassandra: {e}")
        st.info("Le driver Cassandra n'est pas disponible. Utilisation de données simulées.")
        return None
    except Exception as e:
        st.error(f"Erreur de connexion à Cassandra: {e}")
        st.info("Connexion à Cassandra échouée. Utilisation de données simulées.")
        return None

# Load data from Cassandra or use simulated data
def load_stock_data(symbol, days=30):
    """Load stock price data for a given symbol"""
    session = connect_to_cassandra()
    if session:
        # Try to load from Cassandra
        query = f"""
        SELECT * FROM stock_prices
        WHERE symbol = %s
        ORDER BY timestamp DESC
        LIMIT {days * 100}  -- Assuming ~100 records per day
        """

        try:
            rows = session.execute(query, [symbol])
            data = []
            for row in rows:
                data.append({
                    'timestamp': row.timestamp,
                    'symbol': row.symbol,
                    'open': float(row.price_open) if row.price_open else 0,
                    'high': float(row.price_high) if row.price_high else 0,
                    'low': float(row.price_low) if row.price_low else 0,
                    'close': float(row.price_close) if row.price_close else 0,
                    'volume': row.volume or 0,
                    'rolling_avg': float(row.rolling_avg) if row.rolling_avg else 0,
                    'z_score': float(row.z_score) if row.z_score else 0,
                    'is_anomaly': row.is_anomaly or False
                })
            return pd.DataFrame(data)
        except Exception as e:
            st.error(f"Erreur lors du chargement des données depuis Cassandra: {e}")
            return pd.DataFrame()
    else:
        # Generate simulated data
        st.info("Utilisation de données simulées pour le développement")
        import random
        from datetime import datetime, timedelta

        data = []
        base_price = random.uniform(100, 300)
        for i in range(days):
            date = datetime.now() - timedelta(days=i)
            # Generate realistic stock price movements
            change = random.uniform(-0.05, 0.05)  # -5% to +5% daily change
            open_price = base_price
            close_price = base_price * (1 + change)
            high_price = max(open_price, close_price) * (1 + random.uniform(0, 0.02))
            low_price = min(open_price, close_price) * (1 - random.uniform(0, 0.02))

            # Simulate anomalies occasionally
            is_anomaly = random.random() < 0.05  # 5% chance of anomaly
            z_score = random.uniform(2.5, 4.0) if is_anomaly else random.uniform(-1.5, 1.5)

            data.append({
                'timestamp': date,
                'symbol': symbol,
                'open': open_price,
                'high': high_price,
                'low': low_price,
                'close': close_price,
                'volume': random.randint(1000000, 5000000),
                'rolling_avg': base_price,
                'z_score': z_score,
                'is_anomaly': is_anomaly
            })
            base_price = close_price

        return pd.DataFrame(data)

def load_predictions(symbol, days=7):
    """Load predictions for a given symbol"""
    session = connect_to_cassandra()
    if session:
        # Try to load from Cassandra
        query = f"""
        SELECT * FROM predictions
        WHERE symbol = %s
        ORDER BY timestamp DESC
        LIMIT {days * 10}
        """

        try:
            rows = session.execute(query, [symbol])
            data = []
            for row in rows:
                data.append({
                    'timestamp': row.timestamp,
                    'symbol': row.symbol,
                    'predicted_price': float(row.predicted_price) if row.predicted_price else 0,
                    'confidence': float(row.confidence) if row.confidence else 0
                })
            return pd.DataFrame(data)
        except Exception as e:
            st.error(f"Erreur lors du chargement des prédictions depuis Cassandra: {e}")
            return pd.DataFrame()
    else:
        # Generate simulated data
        import random
        from datetime import datetime, timedelta

        data = []
        base_price = random.uniform(100, 300)
        for i in range(days):
            date = datetime.now() - timedelta(days=i)
            data.append({
                'timestamp': date,
                'symbol': symbol,
                'predicted_price': base_price * (1 + random.uniform(-0.03, 0.03)),
                'confidence': random.uniform(0.6, 0.95)
            })
        return pd.DataFrame(data)

def load_sentiment_data(symbol, days=7):
    """Load sentiment analysis data for a given symbol"""
    session = connect_to_cassandra()
    if session:
        # Try to load from Cassandra
        query = f"""
        SELECT * FROM sentiment_analysis
        WHERE symbol = %s
        ORDER BY timestamp DESC
        LIMIT {days * 10}
        """

        try:
            rows = session.execute(query, [symbol])
            data = []
            for row in rows:
                data.append({
                    'timestamp': row.timestamp,
                    'symbol': row.symbol,
                    'sentiment_score': float(row.sentiment_score) if row.sentiment_score else 0,
                    'sentiment_label': row.sentiment_label or 'neutral'
                })
            return pd.DataFrame(data)
        except Exception as e:
            st.error(f"Erreur lors du chargement des données de sentiment depuis Cassandra: {e}")
            return pd.DataFrame()
    else:
        # Generate simulated data
        import random
        from datetime import datetime, timedelta

        data = []
        for i in range(days):
            date = datetime.now() - timedelta(days=i)
            sentiment_score = random.uniform(-1.0, 1.0)
            if sentiment_score > 0.3:
                sentiment_label = 'positive'
            elif sentiment_score < -0.3:
                sentiment_label = 'negative'
            else:
                sentiment_label = 'neutral'

            data.append({
                'timestamp': date,
                'symbol': symbol,
                'sentiment_score': sentiment_score,
                'sentiment_label': sentiment_label
            })
        return pd.DataFrame(data)

def load_anomalies(symbol, days=7):
    """Load anomaly data for a given symbol"""
    session = connect_to_cassandra()
    if session:
        # Try to load from Cassandra
        query = f"""
        SELECT * FROM anomalies
        WHERE symbol = %s
        ORDER BY timestamp DESC
        LIMIT {days * 10}
        """

        try:
            rows = session.execute(query, [symbol])
            data = []
            for row in rows:
                data.append({
                    'timestamp': row.timestamp,
                    'symbol': row.symbol,
                    'anomaly_type': row.anomaly_type or 'unknown',
                    'description': row.description or 'No description',
                    'severity': row.severity or 'medium'
                })
            return pd.DataFrame(data)
        except Exception as e:
            st.error(f"Erreur lors du chargement des anomalies depuis Cassandra: {e}")
            return pd.DataFrame()
    else:
        # Generate simulated data
        import random
        from datetime import datetime, timedelta

        data = []
        for i in range(days):
            date = datetime.now() - timedelta(days=i)
            # Generate anomalies occasionally
            if random.random() < 0.1:  # 10% chance of anomaly
                anomaly_types = ['price_spike', 'volume_anomaly', 'sentiment_divergence', 'market_manipulation']
                severities = ['low', 'medium', 'high']
                data.append({
                    'timestamp': date,
                    'symbol': symbol,
                    'anomaly_type': random.choice(anomaly_types),
                    'description': f'Anomalie détectée pour {symbol}',
                    'severity': random.choice(severities)
                })
        return pd.DataFrame(data)

def load_multimodal_analysis(symbol, days=7):
    """Load multimodal analysis data for a given symbol"""
    session = connect_to_cassandra()
    if session:
        # Try to load from Cassandra
        query = f"""
        SELECT * FROM multimodal_analysis
        WHERE symbol = %s
        ORDER BY price_timestamp DESC
        LIMIT {days * 10}
        """

        try:
            rows = session.execute(query, [symbol])
            data = []
            for row in rows:
                data.append({
                    'price_timestamp': row.price_timestamp,
                    'news_timestamp': row.news_timestamp,
                    'symbol': row.symbol,
                    'price_close': float(row.price_close) if row.price_close else 0,
                    'headline': row.headline or 'No headline',
                    'sentiment_score': float(row.sentiment_score) if row.sentiment_score else 0,
                    'anomaly_signal': row.anomaly_signal or 'NORMAL'
                })
            return pd.DataFrame(data)
        except Exception as e:
            st.error(f"Erreur lors du chargement de l'analyse multimodale depuis Cassandra: {e}")
            return pd.DataFrame()
    else:
        # Generate simulated data
        import random
        from datetime import datetime, timedelta

        data = []
        for i in range(days):
            date = datetime.now() - timedelta(days=i)
            # Generate multimodal analysis data
            if random.random() < 0.15:  # 15% chance of signal
                signals = ['NEGATIVE_SENTIMENT_PRICE_DROP', 'POSITIVE_SENTIMENT_PRICE_RISE', 'DIVERGENCE', 'NORMAL']
                data.append({
                    'price_timestamp': date,
                    'news_timestamp': date,
                    'symbol': symbol,
                    'price_close': random.uniform(100, 300),
                    'headline': f'Headline for {symbol} on {date.strftime("%Y-%m-%d")}',
                    'sentiment_score': random.uniform(-1.0, 1.0),
                    'anomaly_signal': random.choice(signals)
                })
        return pd.DataFrame(data)

# Main dashboard
col1, col2 = st.columns([1, 3])

with col1:
    st.subheader("Paramètres")
    selected_symbol = st.selectbox(
        "Sélectionnez un symbole",
        ["AAPL", "GOOGL", "MSFT", "TSLA", "AMZN", "META", "NFLX", "NVDA"]
    )

    time_range = st.selectbox(
        "Plage de temps",
        ["1D", "1W", "1M", "3M", "6M", "1Y"],
        index=2
    )

    # Time range mapping
    time_map = {
        "1D": 1,
        "1W": 7,
        "1M": 30,
        "3M": 90,
        "6M": 180,
        "1Y": 365
    }

    days = time_map[time_range]

# Load data
stock_data = load_stock_data(selected_symbol, days)
predictions = load_predictions(selected_symbol, 7)
sentiment_data = load_sentiment_data(selected_symbol, 7)
anomalies = load_anomalies(selected_symbol, 7)
multimodal_data = load_multimodal_analysis(selected_symbol, 7)

# Display metrics
if not stock_data.empty:
    latest_price = stock_data.iloc[0]['close']
    price_change = ((stock_data.iloc[0]['close'] - stock_data.iloc[-1]['close']) / stock_data.iloc[-1]['close']) * 100

    # Count anomalies in the data
    anomaly_count = stock_data[stock_data['is_anomaly'] == True].shape[0]

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Prix Actuel", f"${latest_price:.2f}", f"{price_change:+.2f}%")
    col2.metric("Volume", f"{stock_data['volume'].iloc[0]:,}" if not stock_data.empty else "N/A")
    col3.metric("Confiance Prédiction", f"{predictions['confidence'].iloc[0]:.2f}" if not predictions.empty else "N/A")
    col4.metric("Anomalies Détectées", anomaly_count)

# Charts
st.subheader(f"Analyse pour {selected_symbol}")

if not stock_data.empty:
    # OHLC Chart with anomalies highlighted
    fig = go.Figure(data=go.Candlestick(
        x=stock_data['timestamp'],
        open=stock_data['open'],
        high=stock_data['high'],
        low=stock_data['low'],
        close=stock_data['close']
    ))

    # Add anomalies as scatter points
    anomalies_data = stock_data[stock_data['is_anomaly'] == True]
    if not anomalies_data.empty:
        fig.add_trace(go.Scatter(
            x=anomalies_data['timestamp'],
            y=anomalies_data['close'],
            mode='markers',
            marker=dict(color='red', size=10, symbol='x'),
            name='Anomalies',
            text='Anomaly Detected'
        ))

    # Add rolling average
    fig.add_trace(go.Scatter(
        x=stock_data['timestamp'],
        y=stock_data['rolling_avg'],
        mode='lines',
        name='Moving Average',
        line=dict(color='orange', width=2)
    ))

    fig.update_layout(
        title=f"Prix de {selected_symbol} avec Détection d'Anomalies",
        xaxis_title="Date",
        yaxis_title="Prix ($)",
        height=500
    )

    st.plotly_chart(fig, use_container_width=True)

    # Volume chart
    fig_vol = px.bar(
        stock_data,
        x='timestamp',
        y='volume',
        title="Volume des Transactions"
    )
    st.plotly_chart(fig_vol, use_container_width=True)

# Predictions, Sentiment, and Anomalies
if not predictions.empty or not sentiment_data.empty or not anomalies.empty:
    col1, col2, col3 = st.columns(3)

    with col1:
        if not predictions.empty:
            st.subheader("Prédictions de Prix")
            fig_pred = px.line(
                predictions,
                x='timestamp',
                y='predicted_price',
                title="Prédictions de Prix"
            )
            st.plotly_chart(fig_pred, use_container_width=True)

    with col2:
        if not sentiment_data.empty:
            st.subheader("Analyse de Sentiment")
            fig_sent = px.bar(
                sentiment_data,
                x='timestamp',
                y='sentiment_score',
                color='sentiment_label',
                title="Score de Sentiment"
            )
            st.plotly_chart(fig_sent, use_container_width=True)

    with col3:
        if not anomalies.empty:
            st.subheader("Anomalies Détectées")
            fig_anom = px.scatter(
                anomalies,
                x='timestamp',
                y='severity',
                color='anomaly_type',
                title="Anomalies Détectées",
                hover_data=['description']
            )
            st.plotly_chart(fig_anom, use_container_width=True)

# Multimodal Analysis
if not multimodal_data.empty:
    st.subheader("Analyse Multimodale: Prix + Sentiment")
    st.write("Corrélation entre les mouvements de prix et les sentiments des actualités")

    # Show multimodal signals
    signal_counts = multimodal_data['anomaly_signal'].value_counts()
    st.bar_chart(signal_counts)

# Additional information
st.subheader("Informations Supplémentaires")
tab1, tab2, tab3, tab4 = st.tabs(["Données Brutes", "Statistiques", "Alertes", "Anomalies"])

with tab1:
    if not stock_data.empty:
        st.dataframe(stock_data.head(10))
    else:
        st.info("Aucune donnée disponible")

with tab2:
    if not stock_data.empty:
        st.write("Statistiques descriptives:")
        st.write(stock_data[['open', 'high', 'low', 'close', 'volume', 'z_score']].describe())
    else:
        st.info("Aucune donnée disponible")

with tab3:
    st.write("Système d'alertes:")
    # Show recent anomalies as alerts
    if not anomalies.empty:
        for _, row in anomalies.head(5).iterrows():
            if row['severity'] == 'high':
                st.error(f"🔴 {row['anomaly_type']}: {row['description']}")
            elif row['severity'] == 'medium':
                st.warning(f"🟡 {row['anomaly_type']}: {row['description']}")
            else:
                st.info(f"🔵 {row['anomaly_type']}: {row['description']}")
    else:
        st.info("Aucune alerte active pour le moment")

with tab4:
    if not anomalies.empty:
        st.write("Détail des anomalies récentes:")
        st.dataframe(anomalies[['timestamp', 'anomaly_type', 'description', 'severity']])
    else:
        st.info("Aucune anomalie détectée récemment")

# Footer
st.markdown("---")
st.markdown("*MarketPulse - Système de détection d'anomalies en temps réel*")