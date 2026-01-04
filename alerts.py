"""
Real-time Alert System for Morocco Stock Market
Monitors prices, volumes, and news for triggering alerts
"""

import json
import time
import smtplib
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Callable, Any
from dataclasses import dataclass, field
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from threading import Thread, Event
from queue import Queue
import os

logger = logging.getLogger(__name__)


@dataclass
class Alert:
    """Alert definition"""
    id: str
    name: str
    type: str  # 'price', 'variation', 'volume', 'news'
    ticker: Optional[str] = None
    condition: str = ""  # 'above', 'below', 'crosses', 'contains'
    threshold: Optional[float] = None
    keywords: List[str] = field(default_factory=list)
    cooldown_minutes: int = 60
    is_active: bool = True
    last_triggered: Optional[datetime] = None
    trigger_count: int = 0
    
    def to_dict(self) -> Dict:
        return {
            'id': self.id,
            'name': self.name,
            'type': self.type,
            'ticker': self.ticker,
            'condition': self.condition,
            'threshold': self.threshold,
            'keywords': self.keywords,
            'cooldown_minutes': self.cooldown_minutes,
            'is_active': self.is_active,
            'last_triggered': self.last_triggered.isoformat() if self.last_triggered else None,
            'trigger_count': self.trigger_count
        }


@dataclass
class AlertEvent:
    """Triggered alert event"""
    alert_id: str
    alert_name: str
    alert_type: str
    ticker: Optional[str]
    message: str
    current_value: Any
    threshold: Any
    timestamp: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict:
        return {
            'alert_id': self.alert_id,
            'alert_name': self.alert_name,
            'alert_type': self.alert_type,
            'ticker': self.ticker,
            'message': self.message,
            'current_value': self.current_value,
            'threshold': self.threshold,
            'timestamp': self.timestamp.isoformat()
        }


class NotificationChannel:
    """Base class for notification channels"""
    
    def send(self, event: AlertEvent) -> bool:
        raise NotImplementedError


class ConsoleNotification(NotificationChannel):
    """Console/terminal notifications"""
    
    def send(self, event: AlertEvent) -> bool:
        print("\n" + "=" * 60)
        print(f"🚨 ALERT: {event.alert_name}")
        print("=" * 60)
        print(f"Type: {event.alert_type}")
        if event.ticker:
            print(f"Ticker: {event.ticker}")
        print(f"Message: {event.message}")
        print(f"Value: {event.current_value} (threshold: {event.threshold})")
        print(f"Time: {event.timestamp.strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 60 + "\n")
        return True


class FileNotification(NotificationChannel):
    """File-based notifications (JSON log)"""
    
    def __init__(self, filepath: str = "data/alerts.json"):
        self.filepath = filepath
    
    def send(self, event: AlertEvent) -> bool:
        try:
            # Load existing alerts
            alerts = []
            if os.path.exists(self.filepath):
                with open(self.filepath, 'r') as f:
                    try:
                        alerts = json.load(f)
                    except json.JSONDecodeError:
                        alerts = []
            
            # Add new alert
            alerts.append(event.to_dict())
            
            # Save
            with open(self.filepath, 'w') as f:
                json.dump(alerts, f, indent=2, ensure_ascii=False)
            
            return True
        except Exception as e:
            logger.error(f"File notification failed: {e}")
            return False


class EmailNotification(NotificationChannel):
    """Email notifications via SMTP"""
    
    def __init__(self, smtp_server: str, smtp_port: int,
                 username: str, password: str,
                 from_email: str, to_emails: List[str]):
        self.smtp_server = smtp_server
        self.smtp_port = smtp_port
        self.username = username
        self.password = password
        self.from_email = from_email
        self.to_emails = to_emails
    
    def send(self, event: AlertEvent) -> bool:
        try:
            msg = MIMEMultipart()
            msg['From'] = self.from_email
            msg['To'] = ', '.join(self.to_emails)
            msg['Subject'] = f"🚨 Market Alert: {event.alert_name}"
            
            body = f"""
Market Alert Triggered

Alert: {event.alert_name}
Type: {event.alert_type}
{'Ticker: ' + event.ticker if event.ticker else ''}
Message: {event.message}
Current Value: {event.current_value}
Threshold: {event.threshold}
Time: {event.timestamp.strftime('%Y-%m-%d %H:%M:%S')}

---
Morocco Stock Market Monitor
            """
            
            msg.attach(MIMEText(body, 'plain'))
            
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.username, self.password)
                server.send_message(msg)
            
            return True
        except Exception as e:
            logger.error(f"Email notification failed: {e}")
            return False


class WebhookNotification(NotificationChannel):
    """Webhook notifications (Slack, Discord, Teams, etc.)"""
    
    def __init__(self, webhook_url: str, platform: str = "slack"):
        self.webhook_url = webhook_url
        self.platform = platform
    
    def send(self, event: AlertEvent) -> bool:
        import requests
        
        try:
            if self.platform == "slack":
                payload = {
                    "text": f"🚨 *{event.alert_name}*",
                    "attachments": [{
                        "color": "#ff0000" if event.alert_type == "price" else "#ffaa00",
                        "fields": [
                            {"title": "Type", "value": event.alert_type, "short": True},
                            {"title": "Ticker", "value": event.ticker or "N/A", "short": True},
                            {"title": "Message", "value": event.message, "short": False},
                            {"title": "Value", "value": str(event.current_value), "short": True},
                            {"title": "Threshold", "value": str(event.threshold), "short": True},
                        ]
                    }]
                }
            elif self.platform == "discord":
                payload = {
                    "content": f"🚨 **{event.alert_name}**",
                    "embeds": [{
                        "title": event.message,
                        "fields": [
                            {"name": "Ticker", "value": event.ticker or "N/A", "inline": True},
                            {"name": "Value", "value": str(event.current_value), "inline": True},
                        ],
                        "color": 16711680  # Red
                    }]
                }
            else:
                payload = event.to_dict()
            
            response = requests.post(self.webhook_url, json=payload, timeout=10)
            return response.status_code == 200
        except Exception as e:
            logger.error(f"Webhook notification failed: {e}")
            return False


class TelegramNotification(NotificationChannel):
    """Telegram bot notifications"""
    
    def __init__(self, bot_token: str, chat_id: str):
        self.bot_token = bot_token
        self.chat_id = chat_id
    
    def send(self, event: AlertEvent) -> bool:
        import requests
        
        try:
            message = f"""
🚨 *{event.alert_name}*

📊 Type: {event.alert_type}
{'🏷 Ticker: ' + event.ticker if event.ticker else ''}
📝 {event.message}
📈 Value: `{event.current_value}`
🎯 Threshold: `{event.threshold}`
🕐 {event.timestamp.strftime('%H:%M:%S')}
            """
            
            url = f"https://api.telegram.org/bot{self.bot_token}/sendMessage"
            payload = {
                "chat_id": self.chat_id,
                "text": message,
                "parse_mode": "Markdown"
            }
            
            response = requests.post(url, json=payload, timeout=10)
            return response.status_code == 200
        except Exception as e:
            logger.error(f"Telegram notification failed: {e}")
            return False


class AlertEngine:
    """
    Main alert engine that monitors data and triggers alerts
    """
    
    def __init__(self):
        self.alerts: Dict[str, Alert] = {}
        self.channels: List[NotificationChannel] = []
        self.event_queue: Queue = Queue()
        self.stop_event = Event()
        self._alert_history: List[AlertEvent] = []
        
        # Add default console channel
        self.add_channel(ConsoleNotification())
        self.add_channel(FileNotification())
    
    def add_channel(self, channel: NotificationChannel):
        """Add a notification channel"""
        self.channels.append(channel)
    
    def add_alert(self, alert: Alert):
        """Add an alert"""
        self.alerts[alert.id] = alert
        logger.info(f"Added alert: {alert.name}")
    
    def remove_alert(self, alert_id: str):
        """Remove an alert"""
        if alert_id in self.alerts:
            del self.alerts[alert_id]
            logger.info(f"Removed alert: {alert_id}")
    
    def _can_trigger(self, alert: Alert) -> bool:
        """Check if alert can be triggered (cooldown)"""
        if not alert.is_active:
            return False
        
        if alert.last_triggered:
            cooldown = timedelta(minutes=alert.cooldown_minutes)
            if datetime.now() - alert.last_triggered < cooldown:
                return False
        
        return True
    
    def _trigger_alert(self, alert: Alert, message: str, 
                       current_value: Any, threshold: Any):
        """Trigger an alert and send notifications"""
        if not self._can_trigger(alert):
            return
        
        # Create event
        event = AlertEvent(
            alert_id=alert.id,
            alert_name=alert.name,
            alert_type=alert.type,
            ticker=alert.ticker,
            message=message,
            current_value=current_value,
            threshold=threshold
        )
        
        # Update alert
        alert.last_triggered = datetime.now()
        alert.trigger_count += 1
        
        # Store in history
        self._alert_history.append(event)
        
        # Send to all channels
        for channel in self.channels:
            try:
                channel.send(event)
            except Exception as e:
                logger.error(f"Failed to send to channel: {e}")
        
        logger.info(f"Alert triggered: {alert.name}")
    
    def check_price_alerts(self, stock_data: Dict):
        """Check price-related alerts"""
        ticker = stock_data.get('ticker')
        price = stock_data.get('price')
        variation = stock_data.get('variation_pct') or stock_data.get('variation')
        volume = stock_data.get('volume')
        
        for alert in self.alerts.values():
            if not alert.is_active:
                continue
            
            # Skip if ticker doesn't match
            if alert.ticker and alert.ticker != ticker:
                continue
            
            # Price alerts
            if alert.type == 'price' and price is not None:
                if alert.condition == 'above' and price > alert.threshold:
                    self._trigger_alert(
                        alert,
                        f"{ticker} price is above {alert.threshold} MAD",
                        price,
                        alert.threshold
                    )
                elif alert.condition == 'below' and price < alert.threshold:
                    self._trigger_alert(
                        alert,
                        f"{ticker} price is below {alert.threshold} MAD",
                        price,
                        alert.threshold
                    )
            
            # Variation alerts
            elif alert.type == 'variation' and variation is not None:
                if alert.condition == 'above' and variation > alert.threshold:
                    self._trigger_alert(
                        alert,
                        f"{ticker} variation is +{variation}% (above {alert.threshold}%)",
                        variation,
                        alert.threshold
                    )
                elif alert.condition == 'below' and variation < -alert.threshold:
                    self._trigger_alert(
                        alert,
                        f"{ticker} variation is {variation}% (below -{alert.threshold}%)",
                        variation,
                        -alert.threshold
                    )
            
            # Volume alerts
            elif alert.type == 'volume' and volume is not None:
                if alert.condition == 'above' and volume > alert.threshold:
                    self._trigger_alert(
                        alert,
                        f"{ticker} volume is {volume:,} (above {alert.threshold:,})",
                        volume,
                        alert.threshold
                    )
    
    def check_news_alerts(self, article: Dict):
        """Check news-related alerts"""
        title = article.get('title', '').lower()
        content = article.get('content', '').lower() + article.get('summary', '').lower()
        relevance = article.get('relevance_score', 0)
        
        for alert in self.alerts.values():
            if not alert.is_active or alert.type != 'news':
                continue
            
            # Check keywords
            matched_keywords = []
            for keyword in alert.keywords:
                if keyword.lower() in title or keyword.lower() in content:
                    matched_keywords.append(keyword)
            
            if matched_keywords:
                # Check if ticker is mentioned (if specified)
                if alert.ticker:
                    ticker_mentioned = alert.ticker.lower() in title or alert.ticker.lower() in content
                    if not ticker_mentioned:
                        continue
                
                self._trigger_alert(
                    alert,
                    f"News alert: {article.get('title', '')[:100]}",
                    f"Keywords: {', '.join(matched_keywords)}",
                    f"Relevance: {relevance}"
                )
    
    def check_market_alerts(self, market_data: Dict):
        """Check market-wide alerts (indices, etc.)"""
        for alert in self.alerts.values():
            if not alert.is_active or alert.type != 'market':
                continue
            
            # Check MASI variation
            masi_var = market_data.get('masi_variation')
            if masi_var is not None:
                if alert.condition == 'above' and masi_var > alert.threshold:
                    self._trigger_alert(
                        alert,
                        f"MASI variation is +{masi_var}%",
                        masi_var,
                        alert.threshold
                    )
                elif alert.condition == 'below' and masi_var < -alert.threshold:
                    self._trigger_alert(
                        alert,
                        f"MASI variation is {masi_var}%",
                        masi_var,
                        -alert.threshold
                    )
    
    def get_alert_history(self, limit: int = 100) -> List[Dict]:
        """Get recent alert history"""
        return [e.to_dict() for e in self._alert_history[-limit:]]
    
    def save_alerts(self, filepath: str = "data/alerts_config.json"):
        """Save alert configurations"""
        data = {
            'alerts': [a.to_dict() for a in self.alerts.values()],
            'saved_at': datetime.now().isoformat()
        }
        
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    
    def load_alerts(self, filepath: str = "data/alerts_config.json"):
        """Load alert configurations"""
        if not os.path.exists(filepath):
            return
        
        with open(filepath, 'r') as f:
            data = json.load(f)
        
        for alert_data in data.get('alerts', []):
            alert = Alert(
                id=alert_data['id'],
                name=alert_data['name'],
                type=alert_data['type'],
                ticker=alert_data.get('ticker'),
                condition=alert_data.get('condition', ''),
                threshold=alert_data.get('threshold'),
                keywords=alert_data.get('keywords', []),
                cooldown_minutes=alert_data.get('cooldown_minutes', 60),
                is_active=alert_data.get('is_active', True)
            )
            self.add_alert(alert)


# Pre-configured alert templates
def create_price_alert(ticker: str, condition: str, threshold: float,
                       name: str = None) -> Alert:
    """Create a price alert"""
    return Alert(
        id=f"price_{ticker}_{condition}_{threshold}",
        name=name or f"{ticker} {condition} {threshold} MAD",
        type="price",
        ticker=ticker,
        condition=condition,
        threshold=threshold
    )


def create_variation_alert(ticker: str, threshold: float,
                           name: str = None) -> Alert:
    """Create a variation alert (triggers on big moves)"""
    return Alert(
        id=f"var_{ticker}_{threshold}",
        name=name or f"{ticker} moves more than {threshold}%",
        type="variation",
        ticker=ticker,
        condition="above",
        threshold=threshold
    )


def create_volume_alert(ticker: str, threshold: int,
                        name: str = None) -> Alert:
    """Create a volume spike alert"""
    return Alert(
        id=f"vol_{ticker}_{threshold}",
        name=name or f"{ticker} volume above {threshold:,}",
        type="volume",
        ticker=ticker,
        condition="above",
        threshold=threshold
    )


def create_news_alert(keywords: List[str], ticker: str = None,
                      name: str = None) -> Alert:
    """Create a news alert for specific keywords"""
    return Alert(
        id=f"news_{'_'.join(keywords[:3])}",
        name=name or f"News about {', '.join(keywords)}",
        type="news",
        ticker=ticker,
        keywords=keywords
    )


def create_market_alert(threshold: float, name: str = None) -> Alert:
    """Create a market-wide alert (MASI movement)"""
    return Alert(
        id=f"market_{threshold}",
        name=name or f"Market moves more than {threshold}%",
        type="market",
        condition="above",
        threshold=threshold
    )


if __name__ == "__main__":
    # Demo the alert system
    print("Alert System Demo")
    print("=" * 60)
    
    engine = AlertEngine()
    
    # Add some sample alerts
    engine.add_alert(create_price_alert("ATW", "above", 750))
    engine.add_alert(create_price_alert("IAM", "below", 100))
    engine.add_alert(create_variation_alert("*", 5.0))  # Any stock
    engine.add_alert(create_news_alert(["dividende", "résultats"], ticker="ATW"))
    engine.add_alert(create_market_alert(2.0))
    
    # Simulate stock data that would trigger alerts
    test_stock = {
        'ticker': 'ATW',
        'name': 'Attijariwafa Bank',
        'price': 760.0,  # Above 750 threshold
        'variation_pct': 6.0,  # Above 5% threshold
        'volume': 50000
    }
    
    print("\nChecking price alerts with test data...")
    engine.check_price_alerts(test_stock)
    
    # Simulate news
    test_news = {
        'title': 'Attijariwafa Bank annonce un dividende exceptionnel',
        'summary': 'La banque a décidé de distribuer un dividende record...',
        'relevance_score': 85.0
    }
    
    print("\nChecking news alerts with test article...")
    engine.check_news_alerts(test_news)
    
    # Show history
    print("\n" + "=" * 60)
    print("Alert History:")
    for event in engine.get_alert_history():
        print(f"  - {event['alert_name']}: {event['message']}")
    
    # Save configuration
    engine.save_alerts()
    print("\nAlerts saved to data/alerts_config.json")
