"""
Alert components for the dashboard
"""

import streamlit as st
from datetime import datetime

class AlertSystem:
    def __init__(self):
        self.alerts = []

    def add_alert(self, symbol, condition, message, severity="info", alert_type="general"):
        """Add a new alert"""
        alert = {
            "timestamp": datetime.now(),
            "symbol": symbol,
            "condition": condition,
            "message": message,
            "severity": severity,
            "type": alert_type
        }
        self.alerts.append(alert)

        # Keep only the last 10 alerts
        if len(self.alerts) > 10:
            self.alerts = self.alerts[-10:]

    def get_active_alerts(self):
        """Get all active alerts"""
        return self.alerts

    def display_alerts(self):
        """Display alerts in the dashboard"""
        if not self.alerts:
            st.info("Aucune alerte active pour le moment")
            return

        for alert in self.alerts:
            if alert["severity"] == "error" or alert["type"] == "anomaly":
                st.error(f"🚨 {alert['symbol']}: {alert['message']}")
            elif alert["severity"] == "warning":
                st.warning(f"⚠️ {alert['symbol']}: {alert['message']}")
            else:
                st.info(f"ℹ️ {alert['symbol']}: {alert['message']}")

    def check_price_alerts(self, current_price, symbol, threshold_percent=5.0):
        """Check for price-based alerts"""
        # This is a simplified version - in a real system, you'd compare with previous prices
        # For now, we'll just add a placeholder alert
        self.add_alert(
            symbol=symbol,
            condition="price_change",
            message=f"Changement de prix important détecté pour {symbol}",
            severity="warning",
            alert_type="price"
        )

    def check_anomaly_alerts(self, symbol, anomaly_type, description, severity="medium"):
        """Check for anomaly-based alerts"""
        self.add_alert(
            symbol=symbol,
            condition=anomaly_type,
            message=f"Anomalie détectée: {description}",
            severity=severity,
            alert_type="anomaly"
        )

    def check_sentiment_alerts(self, symbol, sentiment_score, headline):
        """Check for sentiment-based alerts"""
        if sentiment_score < -0.7:
            self.add_alert(
                symbol=symbol,
                condition="negative_sentiment",
                message=f"Sentiment très négatif détecté: {headline[:50]}...",
                severity="warning",
                alert_type="sentiment"
            )
        elif sentiment_score > 0.7:
            self.add_alert(
                symbol=symbol,
                condition="positive_sentiment",
                message=f"Sentiment très positif détecté: {headline[:50]}...",
                severity="info",
                alert_type="sentiment"
            )

# Global alert system instance
alert_system = AlertSystem()