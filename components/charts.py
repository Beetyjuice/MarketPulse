"""
Chart components for the dashboard
"""

import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import streamlit as st

def create_ohlc_chart(data, symbol):
    """Create an OHLC (Open-High-Low-Close) chart"""
    if data.empty:
        st.warning("Aucune donnée disponible pour le graphique OHLC")
        return None
    
    fig = go.Figure(data=go.Candlestick(
        x=data['timestamp'],
        open=data['open'],
        high=data['high'],
        low=data['low'],
        close=data['close']
    ))
    
    fig.update_layout(
        title=f"Prix de {symbol}",
        xaxis_title="Date",
        yaxis_title="Prix ($)",
        height=500
    )
    
    return fig

def create_volume_chart(data, symbol):
    """Create a volume chart"""
    if data.empty:
        st.warning("Aucune donnée disponible pour le graphique de volume")
        return None
    
    fig = px.bar(
        data, 
        x='timestamp', 
        y='volume',
        title=f"Volume des Transactions - {symbol}"
    )
    
    return fig

def create_prediction_chart(predictions, symbol):
    """Create a prediction chart"""
    if predictions.empty:
        st.warning("Aucune donnée de prédiction disponible")
        return None
    
    fig = px.line(
        predictions, 
        x='timestamp', 
        y='predicted_price',
        title=f"Prédictions de Prix - {symbol}"
    )
    
    return fig

def create_sentiment_chart(sentiment_data, symbol):
    """Create a sentiment analysis chart"""
    if sentiment_data.empty:
        st.warning("Aucune donnée de sentiment disponible")
        return None
    
    fig = px.bar(
        sentiment_data, 
        x='timestamp', 
        y='sentiment_score',
        color='sentiment_label',
        title=f"Score de Sentiment - {symbol}"
    )
    
    return fig