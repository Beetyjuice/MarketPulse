"""
Simple REST API Server for Morocco Market Data
Provides HTTP endpoints for accessing market data, news, and alerts
"""

import json
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
from datetime import datetime
import threading
import logging
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)


class MarketAPIHandler(BaseHTTPRequestHandler):
    """HTTP request handler for market data API"""
    
    # Shared state (set by server initialization)
    market_monitor = None
    alert_engine = None
    
    def _set_headers(self, status: int = 200, content_type: str = "application/json"):
        """Set response headers"""
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()
    
    def _send_json(self, data: Any, status: int = 200):
        """Send JSON response"""
        self._set_headers(status)
        response = json.dumps(data, indent=2, ensure_ascii=False, default=str)
        self.wfile.write(response.encode('utf-8'))
    
    def _send_error(self, message: str, status: int = 400):
        """Send error response"""
        self._send_json({"error": message, "status": status}, status)
    
    def _parse_path(self):
        """Parse URL path and query parameters"""
        parsed = urlparse(self.path)
        path = parsed.path.rstrip('/')
        params = parse_qs(parsed.query)
        # Convert single-value params to simple values
        params = {k: v[0] if len(v) == 1 else v for k, v in params.items()}
        return path, params
    
    def do_OPTIONS(self):
        """Handle CORS preflight requests"""
        self._set_headers(200)
    
    def do_GET(self):
        """Handle GET requests"""
        path, params = self._parse_path()
        
        try:
            # Route requests
            if path == "" or path == "/":
                self._handle_root()
            elif path == "/api/health":
                self._handle_health()
            elif path == "/api/stocks":
                self._handle_stocks(params)
            elif path.startswith("/api/stocks/"):
                ticker = path.split("/")[-1]
                self._handle_stock_detail(ticker)
            elif path == "/api/indices":
                self._handle_indices()
            elif path == "/api/news":
                self._handle_news(params)
            elif path == "/api/summary":
                self._handle_summary()
            elif path == "/api/gainers":
                self._handle_gainers(params)
            elif path == "/api/losers":
                self._handle_losers(params)
            elif path == "/api/active":
                self._handle_most_active(params)
            elif path == "/api/alerts":
                self._handle_alerts()
            elif path == "/api/scrape":
                self._handle_scrape(params)
            else:
                self._send_error("Not found", 404)
        
        except Exception as e:
            logger.error(f"API error: {e}")
            self._send_error(str(e), 500)
    
    def do_POST(self):
        """Handle POST requests"""
        path, params = self._parse_path()
        
        try:
            # Read request body
            content_length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(content_length).decode('utf-8')
            data = json.loads(body) if body else {}
            
            if path == "/api/scrape/stocks":
                self._handle_scrape_stocks()
            elif path == "/api/scrape/news":
                self._handle_scrape_news()
            elif path == "/api/alerts":
                self._handle_create_alert(data)
            else:
                self._send_error("Not found", 404)
        
        except json.JSONDecodeError:
            self._send_error("Invalid JSON", 400)
        except Exception as e:
            logger.error(f"API error: {e}")
            self._send_error(str(e), 500)
    
    def _handle_root(self):
        """API root - return available endpoints"""
        endpoints = {
            "name": "Morocco Stock Market API",
            "version": "1.0",
            "endpoints": {
                "GET /api/health": "Health check",
                "GET /api/stocks": "List all stocks",
                "GET /api/stocks/{ticker}": "Get stock detail",
                "GET /api/indices": "Get market indices",
                "GET /api/news": "Get recent news",
                "GET /api/summary": "Get market summary",
                "GET /api/gainers": "Get top gainers",
                "GET /api/losers": "Get top losers",
                "GET /api/active": "Get most active stocks",
                "GET /api/alerts": "Get alert history",
                "POST /api/scrape/stocks": "Trigger stock scrape",
                "POST /api/scrape/news": "Trigger news scrape",
                "POST /api/alerts": "Create new alert"
            },
            "timestamp": datetime.now().isoformat()
        }
        self._send_json(endpoints)
    
    def _handle_health(self):
        """Health check endpoint"""
        self._send_json({
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "database": "connected" if self.market_monitor else "not initialized"
        })
    
    def _handle_stocks(self, params: Dict):
        """Get all stocks"""
        if not self.market_monitor:
            self._send_error("Monitor not initialized", 500)
            return
        
        stocks = self.market_monitor.db.get_latest_stocks()
        
        # Apply filters
        sector = params.get('sector')
        if sector:
            stocks = [s for s in stocks if s.get('sector') == sector]
        
        min_var = params.get('min_variation')
        if min_var:
            stocks = [s for s in stocks if (s.get('variation_pct') or 0) >= float(min_var)]
        
        # Pagination
        limit = int(params.get('limit', 100))
        offset = int(params.get('offset', 0))
        
        self._send_json({
            "count": len(stocks),
            "stocks": stocks[offset:offset+limit]
        })
    
    def _handle_stock_detail(self, ticker: str):
        """Get detailed stock information"""
        if not self.market_monitor:
            self._send_error("Monitor not initialized", 500)
            return
        
        info = self.market_monitor.get_stock_info(ticker.upper())
        
        if not info.get('current'):
            self._send_error(f"Stock {ticker} not found", 404)
            return
        
        self._send_json(info)
    
    def _handle_indices(self):
        """Get market indices"""
        if not self.market_monitor:
            self._send_error("Monitor not initialized", 500)
            return
        
        indices = self.market_monitor.db.get_latest_indices()
        self._send_json({
            "count": len(indices),
            "indices": indices
        })
    
    def _handle_news(self, params: Dict):
        """Get news articles"""
        if not self.market_monitor:
            self._send_error("Monitor not initialized", 500)
            return
        
        limit = int(params.get('limit', 50))
        min_relevance = float(params.get('min_relevance', 0))
        source = params.get('source')
        
        news = self.market_monitor.db.get_news(
            limit=limit,
            min_relevance=min_relevance,
            source=source
        )
        
        self._send_json({
            "count": len(news),
            "articles": news
        })
    
    def _handle_summary(self):
        """Get market summary"""
        if not self.market_monitor:
            self._send_error("Monitor not initialized", 500)
            return
        
        summary = self.market_monitor.get_market_summary()
        self._send_json(summary)
    
    def _handle_gainers(self, params: Dict):
        """Get top gainers"""
        if not self.market_monitor:
            self._send_error("Monitor not initialized", 500)
            return
        
        limit = int(params.get('limit', 10))
        gainers = self.market_monitor.db.get_top_gainers(limit)
        self._send_json({
            "count": len(gainers),
            "stocks": gainers
        })
    
    def _handle_losers(self, params: Dict):
        """Get top losers"""
        if not self.market_monitor:
            self._send_error("Monitor not initialized", 500)
            return
        
        limit = int(params.get('limit', 10))
        losers = self.market_monitor.db.get_top_losers(limit)
        self._send_json({
            "count": len(losers),
            "stocks": losers
        })
    
    def _handle_most_active(self, params: Dict):
        """Get most active stocks"""
        if not self.market_monitor:
            self._send_error("Monitor not initialized", 500)
            return
        
        limit = int(params.get('limit', 10))
        active = self.market_monitor.db.get_most_active(limit)
        self._send_json({
            "count": len(active),
            "stocks": active
        })
    
    def _handle_alerts(self):
        """Get alert history"""
        if self.alert_engine:
            history = self.alert_engine.get_alert_history(100)
            self._send_json({
                "count": len(history),
                "alerts": history
            })
        else:
            self._send_json({"count": 0, "alerts": []})
    
    def _handle_create_alert(self, data: Dict):
        """Create a new alert"""
        if not self.alert_engine:
            self._send_error("Alert engine not initialized", 500)
            return
        
        from utils.alerts import Alert
        
        alert = Alert(
            id=data.get('id', f"alert_{datetime.now().timestamp()}"),
            name=data.get('name', 'Custom Alert'),
            type=data.get('type', 'price'),
            ticker=data.get('ticker'),
            condition=data.get('condition', 'above'),
            threshold=data.get('threshold'),
            keywords=data.get('keywords', [])
        )
        
        self.alert_engine.add_alert(alert)
        self._send_json({"status": "created", "alert": alert.to_dict()})
    
    def _handle_scrape(self, params: Dict):
        """Trigger scrape via GET (for convenience)"""
        target = params.get('target', 'all')
        
        if target == 'stocks':
            self._handle_scrape_stocks()
        elif target == 'news':
            self._handle_scrape_news()
        else:
            self._handle_scrape_all()
    
    def _handle_scrape_stocks(self):
        """Trigger stock scrape"""
        if not self.market_monitor:
            self._send_error("Monitor not initialized", 500)
            return
        
        result = self.market_monitor.scrape_stocks(export_json=False)
        self._send_json(result)
    
    def _handle_scrape_news(self):
        """Trigger news scrape"""
        if not self.market_monitor:
            self._send_error("Monitor not initialized", 500)
            return
        
        result = self.market_monitor.scrape_news(export_json=False)
        self._send_json(result)
    
    def _handle_scrape_all(self):
        """Trigger full scrape"""
        if not self.market_monitor:
            self._send_error("Monitor not initialized", 500)
            return
        
        result = self.market_monitor.run_once()
        self._send_json(result)
    
    def log_message(self, format, *args):
        """Override to use logging instead of print"""
        logger.info(f"{self.address_string()} - {format % args}")


class MarketAPIServer:
    """API server wrapper"""
    
    def __init__(self, host: str = "0.0.0.0", port: int = 8080):
        self.host = host
        self.port = port
        self.server: Optional[HTTPServer] = None
        self._thread: Optional[threading.Thread] = None
    
    def initialize(self, market_monitor=None, alert_engine=None):
        """Initialize with market monitor and alert engine"""
        MarketAPIHandler.market_monitor = market_monitor
        MarketAPIHandler.alert_engine = alert_engine
    
    def start(self, background: bool = True):
        """Start the API server"""
        self.server = HTTPServer((self.host, self.port), MarketAPIHandler)
        
        logger.info(f"API server starting on http://{self.host}:{self.port}")
        
        if background:
            self._thread = threading.Thread(target=self.server.serve_forever, daemon=True)
            self._thread.start()
        else:
            self.server.serve_forever()
    
    def stop(self):
        """Stop the API server"""
        if self.server:
            self.server.shutdown()
            logger.info("API server stopped")


def start_api_server(port: int = 8080):
    """Convenience function to start the API server"""
    from main import MarketMonitor
    from utils.alerts import AlertEngine
    
    # Initialize components
    monitor = MarketMonitor()
    alert_engine = AlertEngine()
    
    # Create and start server
    server = MarketAPIServer(port=port)
    server.initialize(market_monitor=monitor, alert_engine=alert_engine)
    
    print(f"\n{'='*60}")
    print(f"Morocco Market API Server")
    print(f"{'='*60}")
    print(f"Running on http://localhost:{port}")
    print(f"\nEndpoints:")
    print(f"  GET  /api/stocks          - List all stocks")
    print(f"  GET  /api/stocks/{{ticker}} - Stock detail")
    print(f"  GET  /api/indices         - Market indices")
    print(f"  GET  /api/news            - Recent news")
    print(f"  GET  /api/summary         - Market summary")
    print(f"  GET  /api/gainers         - Top gainers")
    print(f"  GET  /api/losers          - Top losers")
    print(f"  POST /api/scrape/stocks   - Trigger stock scrape")
    print(f"  POST /api/scrape/news     - Trigger news scrape")
    print(f"\nPress Ctrl+C to stop")
    print(f"{'='*60}\n")
    
    try:
        server.start(background=False)
    except KeyboardInterrupt:
        print("\nShutting down...")
        server.stop()


if __name__ == "__main__":
    import sys
    
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8080
    start_api_server(port)
