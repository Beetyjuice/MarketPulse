"""
Market Analysis Module
Technical indicators, trends, and analytics for Moroccan stocks
"""

from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple
import statistics
import math
import logging

logger = logging.getLogger(__name__)


@dataclass
class TechnicalIndicators:
    """Technical indicators for a stock"""
    ticker: str
    timestamp: datetime
    sma_5: Optional[float] = None
    sma_20: Optional[float] = None
    sma_50: Optional[float] = None
    ema_12: Optional[float] = None
    ema_26: Optional[float] = None
    macd: Optional[float] = None
    macd_signal: Optional[float] = None
    rsi_14: Optional[float] = None
    bollinger_upper: Optional[float] = None
    bollinger_middle: Optional[float] = None
    bollinger_lower: Optional[float] = None
    atr_14: Optional[float] = None
    volume_sma_20: Optional[float] = None
    price_momentum: Optional[float] = None
    trend: str = "neutral"  # bullish, bearish, neutral
    
    def to_dict(self) -> Dict:
        return {
            'ticker': self.ticker,
            'timestamp': self.timestamp.isoformat(),
            'sma_5': self.sma_5,
            'sma_20': self.sma_20,
            'sma_50': self.sma_50,
            'ema_12': self.ema_12,
            'ema_26': self.ema_26,
            'macd': self.macd,
            'macd_signal': self.macd_signal,
            'rsi_14': self.rsi_14,
            'bollinger_upper': self.bollinger_upper,
            'bollinger_middle': self.bollinger_middle,
            'bollinger_lower': self.bollinger_lower,
            'atr_14': self.atr_14,
            'volume_sma_20': self.volume_sma_20,
            'price_momentum': self.price_momentum,
            'trend': self.trend
        }


class TechnicalAnalyzer:
    """Calculate technical indicators for stocks"""
    
    @staticmethod
    def sma(prices: List[float], period: int) -> Optional[float]:
        """Simple Moving Average"""
        if len(prices) < period:
            return None
        return statistics.mean(prices[-period:])
    
    @staticmethod
    def ema(prices: List[float], period: int) -> Optional[float]:
        """Exponential Moving Average"""
        if len(prices) < period:
            return None
        
        multiplier = 2 / (period + 1)
        ema = prices[0]
        
        for price in prices[1:]:
            ema = (price - ema) * multiplier + ema
        
        return ema
    
    @staticmethod
    def rsi(prices: List[float], period: int = 14) -> Optional[float]:
        """Relative Strength Index"""
        if len(prices) < period + 1:
            return None
        
        gains = []
        losses = []
        
        for i in range(1, len(prices)):
            change = prices[i] - prices[i-1]
            if change > 0:
                gains.append(change)
                losses.append(0)
            else:
                gains.append(0)
                losses.append(abs(change))
        
        avg_gain = statistics.mean(gains[-period:])
        avg_loss = statistics.mean(losses[-period:])
        
        if avg_loss == 0:
            return 100
        
        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))
        
        return round(rsi, 2)
    
    @staticmethod
    def macd(prices: List[float]) -> Tuple[Optional[float], Optional[float]]:
        """MACD and Signal Line"""
        ema_12 = TechnicalAnalyzer.ema(prices, 12)
        ema_26 = TechnicalAnalyzer.ema(prices, 26)
        
        if ema_12 is None or ema_26 is None:
            return None, None
        
        macd_line = ema_12 - ema_26
        
        # Calculate signal line (9-day EMA of MACD)
        # For simplicity, we'll approximate it
        signal = macd_line * 0.9  # Simplified
        
        return round(macd_line, 4), round(signal, 4)
    
    @staticmethod
    def bollinger_bands(prices: List[float], period: int = 20, 
                        num_std: float = 2) -> Tuple[Optional[float], Optional[float], Optional[float]]:
        """Bollinger Bands (upper, middle, lower)"""
        if len(prices) < period:
            return None, None, None
        
        middle = statistics.mean(prices[-period:])
        std = statistics.stdev(prices[-period:])
        
        upper = middle + (std * num_std)
        lower = middle - (std * num_std)
        
        return round(upper, 2), round(middle, 2), round(lower, 2)
    
    @staticmethod
    def atr(highs: List[float], lows: List[float], closes: List[float], 
            period: int = 14) -> Optional[float]:
        """Average True Range"""
        if len(highs) < period + 1:
            return None
        
        true_ranges = []
        for i in range(1, len(highs)):
            tr1 = highs[i] - lows[i]
            tr2 = abs(highs[i] - closes[i-1])
            tr3 = abs(lows[i] - closes[i-1])
            true_ranges.append(max(tr1, tr2, tr3))
        
        return round(statistics.mean(true_ranges[-period:]), 2)
    
    @staticmethod
    def momentum(prices: List[float], period: int = 10) -> Optional[float]:
        """Price Momentum"""
        if len(prices) < period + 1:
            return None
        
        return round(((prices[-1] / prices[-period-1]) - 1) * 100, 2)
    
    @staticmethod
    def determine_trend(sma_5: float, sma_20: float, sma_50: float,
                        current_price: float) -> str:
        """Determine trend based on moving averages"""
        if sma_5 is None or sma_20 is None:
            return "neutral"
        
        # Strong bullish: price > SMA5 > SMA20 > SMA50
        if sma_50 and current_price > sma_5 > sma_20 > sma_50:
            return "strong_bullish"
        # Bullish: price above all SMAs
        elif current_price > sma_5 and current_price > sma_20:
            return "bullish"
        # Strong bearish: price < SMA5 < SMA20 < SMA50
        elif sma_50 and current_price < sma_5 < sma_20 < sma_50:
            return "strong_bearish"
        # Bearish: price below all SMAs
        elif current_price < sma_5 and current_price < sma_20:
            return "bearish"
        else:
            return "neutral"
    
    def analyze(self, ticker: str, prices: List[float],
                highs: List[float] = None, lows: List[float] = None,
                volumes: List[float] = None) -> TechnicalIndicators:
        """
        Calculate all technical indicators for a stock
        
        Args:
            ticker: Stock ticker symbol
            prices: List of closing prices (oldest to newest)
            highs: List of high prices
            lows: List of low prices
            volumes: List of trading volumes
        """
        if not prices:
            return TechnicalIndicators(ticker=ticker, timestamp=datetime.now())
        
        current_price = prices[-1]
        
        # Calculate indicators
        sma_5 = self.sma(prices, 5)
        sma_20 = self.sma(prices, 20)
        sma_50 = self.sma(prices, 50)
        
        ema_12 = self.ema(prices, 12)
        ema_26 = self.ema(prices, 26)
        
        macd_val, macd_sig = self.macd(prices)
        rsi = self.rsi(prices)
        
        bb_upper, bb_middle, bb_lower = self.bollinger_bands(prices)
        
        atr = None
        if highs and lows:
            atr = self.atr(highs, lows, prices)
        
        vol_sma = None
        if volumes:
            vol_sma = self.sma(volumes, 20)
        
        momentum = self.momentum(prices)
        
        trend = self.determine_trend(sma_5, sma_20, sma_50, current_price)
        
        return TechnicalIndicators(
            ticker=ticker,
            timestamp=datetime.now(),
            sma_5=sma_5,
            sma_20=sma_20,
            sma_50=sma_50,
            ema_12=ema_12,
            ema_26=ema_26,
            macd=macd_val,
            macd_signal=macd_sig,
            rsi_14=rsi,
            bollinger_upper=bb_upper,
            bollinger_middle=bb_middle,
            bollinger_lower=bb_lower,
            atr_14=atr,
            volume_sma_20=vol_sma,
            price_momentum=momentum,
            trend=trend
        )


class MarketAnalytics:
    """Market-wide analytics and insights"""
    
    def __init__(self, db=None):
        self.db = db
        self.analyzer = TechnicalAnalyzer()
    
    def calculate_market_breadth(self, stocks: List[Dict]) -> Dict:
        """
        Calculate market breadth indicators
        """
        advancing = 0
        declining = 0
        unchanged = 0
        new_highs = 0
        new_lows = 0
        
        total_volume = 0
        advancing_volume = 0
        declining_volume = 0
        
        for stock in stocks:
            variation = stock.get('variation_pct') or stock.get('variation') or 0
            volume = stock.get('volume') or 0
            
            total_volume += volume
            
            if variation > 0:
                advancing += 1
                advancing_volume += volume
            elif variation < 0:
                declining += 1
                declining_volume += volume
            else:
                unchanged += 1
            
            # Check for new highs/lows (simplified)
            high = stock.get('high') or stock.get('price')
            low = stock.get('low') or stock.get('price')
            price = stock.get('price') or 0
            
            if high and price >= high * 0.99:  # Within 1% of high
                new_highs += 1
            if low and price <= low * 1.01:  # Within 1% of low
                new_lows += 1
        
        total = advancing + declining + unchanged
        
        # Advance/Decline ratio
        ad_ratio = advancing / declining if declining > 0 else float('inf')
        
        # Advance/Decline line (cumulative)
        ad_line = advancing - declining
        
        # Up/Down volume ratio
        ud_volume_ratio = advancing_volume / declining_volume if declining_volume > 0 else float('inf')
        
        return {
            'advancing': advancing,
            'declining': declining,
            'unchanged': unchanged,
            'total': total,
            'advance_decline_ratio': round(ad_ratio, 2),
            'advance_decline_line': ad_line,
            'new_highs': new_highs,
            'new_lows': new_lows,
            'high_low_ratio': new_highs / new_lows if new_lows > 0 else float('inf'),
            'total_volume': total_volume,
            'advancing_volume': advancing_volume,
            'declining_volume': declining_volume,
            'up_down_volume_ratio': round(ud_volume_ratio, 2),
            'breadth_percentage': round((advancing / total) * 100, 1) if total > 0 else 0,
            'market_sentiment': self._determine_sentiment(ad_ratio, new_highs, new_lows)
        }
    
    def _determine_sentiment(self, ad_ratio: float, new_highs: int, 
                            new_lows: int) -> str:
        """Determine overall market sentiment"""
        if ad_ratio > 2 and new_highs > new_lows * 2:
            return "very_bullish"
        elif ad_ratio > 1.5:
            return "bullish"
        elif ad_ratio < 0.5 and new_lows > new_highs * 2:
            return "very_bearish"
        elif ad_ratio < 0.75:
            return "bearish"
        else:
            return "neutral"
    
    def sector_analysis(self, stocks: List[Dict]) -> Dict:
        """Analyze performance by sector"""
        sectors = {}
        
        for stock in stocks:
            sector = stock.get('sector', 'Unknown')
            if sector not in sectors:
                sectors[sector] = {
                    'stocks': [],
                    'total_variation': 0,
                    'total_volume': 0,
                    'count': 0
                }
            
            sectors[sector]['stocks'].append(stock)
            sectors[sector]['total_variation'] += stock.get('variation_pct', 0) or 0
            sectors[sector]['total_volume'] += stock.get('volume', 0) or 0
            sectors[sector]['count'] += 1
        
        # Calculate averages
        for sector in sectors:
            count = sectors[sector]['count']
            if count > 0:
                sectors[sector]['avg_variation'] = round(
                    sectors[sector]['total_variation'] / count, 2
                )
            else:
                sectors[sector]['avg_variation'] = 0
            
            # Top performer in sector
            sorted_stocks = sorted(
                sectors[sector]['stocks'],
                key=lambda x: x.get('variation_pct', 0) or 0,
                reverse=True
            )
            if sorted_stocks:
                sectors[sector]['top_performer'] = sorted_stocks[0].get('ticker')
                sectors[sector]['worst_performer'] = sorted_stocks[-1].get('ticker')
        
        # Rank sectors by performance
        ranked_sectors = sorted(
            sectors.items(),
            key=lambda x: x[1]['avg_variation'],
            reverse=True
        )
        
        return {
            'sectors': dict(ranked_sectors),
            'best_sector': ranked_sectors[0][0] if ranked_sectors else None,
            'worst_sector': ranked_sectors[-1][0] if ranked_sectors else None
        }
    
    def find_unusual_activity(self, stocks: List[Dict], 
                              volume_threshold: float = 2.0) -> List[Dict]:
        """
        Find stocks with unusual trading activity
        
        Args:
            stocks: Current stock data
            volume_threshold: Multiple of average volume to flag
        """
        unusual = []
        
        for stock in stocks:
            flags = []
            
            # Volume spike
            volume = stock.get('volume', 0)
            avg_volume = stock.get('volume_sma_20') or volume
            if avg_volume > 0 and volume > avg_volume * volume_threshold:
                flags.append(f"Volume spike: {volume:,} vs avg {avg_volume:,.0f}")
            
            # Large price move
            variation = abs(stock.get('variation_pct', 0) or 0)
            if variation > 5:
                flags.append(f"Large move: {variation:.1f}%")
            
            # Gap up/down
            open_price = stock.get('open', 0)
            prev_close = stock.get('previous_close', 0)
            if open_price and prev_close:
                gap = ((open_price - prev_close) / prev_close) * 100
                if abs(gap) > 3:
                    direction = "up" if gap > 0 else "down"
                    flags.append(f"Gap {direction}: {gap:.1f}%")
            
            # Price at extreme (high/low)
            price = stock.get('price', 0)
            high = stock.get('high', 0)
            low = stock.get('low', 0)
            if price and high and price >= high * 0.99:
                flags.append("At day high")
            if price and low and price <= low * 1.01:
                flags.append("At day low")
            
            if flags:
                unusual.append({
                    'ticker': stock.get('ticker'),
                    'name': stock.get('name'),
                    'price': price,
                    'variation': stock.get('variation_pct'),
                    'volume': volume,
                    'flags': flags
                })
        
        return sorted(unusual, key=lambda x: len(x['flags']), reverse=True)
    
    def generate_daily_report(self, stocks: List[Dict], 
                              indices: List[Dict] = None) -> Dict:
        """Generate comprehensive daily market report"""
        
        # Market breadth
        breadth = self.calculate_market_breadth(stocks)
        
        # Sector analysis
        sectors = self.sector_analysis(stocks)
        
        # Unusual activity
        unusual = self.find_unusual_activity(stocks)
        
        # Top gainers and losers
        sorted_by_var = sorted(
            [s for s in stocks if s.get('variation_pct') is not None],
            key=lambda x: x.get('variation_pct', 0),
            reverse=True
        )
        
        top_gainers = sorted_by_var[:5]
        top_losers = sorted_by_var[-5:][::-1]
        
        # Most active by volume
        sorted_by_vol = sorted(
            [s for s in stocks if s.get('volume')],
            key=lambda x: x.get('volume', 0),
            reverse=True
        )
        most_active = sorted_by_vol[:5]
        
        return {
            'date': datetime.now().strftime('%Y-%m-%d'),
            'timestamp': datetime.now().isoformat(),
            'summary': {
                'total_stocks': len(stocks),
                'market_sentiment': breadth['market_sentiment'],
                'advancing': breadth['advancing'],
                'declining': breadth['declining'],
                'breadth_pct': breadth['breadth_percentage']
            },
            'indices': indices or [],
            'breadth': breadth,
            'sectors': sectors,
            'top_gainers': [
                {'ticker': s.get('ticker'), 'name': s.get('name'), 
                 'price': s.get('price'), 'variation': s.get('variation_pct')}
                for s in top_gainers
            ],
            'top_losers': [
                {'ticker': s.get('ticker'), 'name': s.get('name'), 
                 'price': s.get('price'), 'variation': s.get('variation_pct')}
                for s in top_losers
            ],
            'most_active': [
                {'ticker': s.get('ticker'), 'name': s.get('name'), 
                 'volume': s.get('volume'), 'variation': s.get('variation_pct')}
                for s in most_active
            ],
            'unusual_activity': unusual[:10]
        }


if __name__ == "__main__":
    # Demo technical analysis
    print("Technical Analysis Demo")
    print("=" * 60)
    
    # Sample price data for testing
    sample_prices = [
        100, 102, 101, 103, 105, 104, 106, 108, 107, 109,
        111, 110, 112, 114, 113, 115, 117, 116, 118, 120,
        119, 121, 123, 122, 124, 126, 125, 127, 129, 128
    ]
    
    analyzer = TechnicalAnalyzer()
    indicators = analyzer.analyze("TEST", sample_prices)
    
    print(f"\nTechnical Indicators for TEST:")
    print(f"  SMA(5):  {indicators.sma_5}")
    print(f"  SMA(20): {indicators.sma_20}")
    print(f"  RSI(14): {indicators.rsi_14}")
    print(f"  MACD:    {indicators.macd}")
    print(f"  Trend:   {indicators.trend}")
    print(f"  Momentum: {indicators.price_momentum}%")
    
    # Demo market analytics
    print("\n" + "=" * 60)
    print("Market Analytics Demo")
    print("=" * 60)
    
    sample_stocks = [
        {'ticker': 'ATW', 'name': 'Attijariwafa', 'price': 744.90, 
         'variation_pct': 2.03, 'volume': 15000, 'sector': 'Banques'},
        {'ticker': 'BCP', 'name': 'BCP', 'price': 287.90, 
         'variation_pct': -0.72, 'volume': 8000, 'sector': 'Banques'},
        {'ticker': 'IAM', 'name': 'Maroc Telecom', 'price': 111.10, 
         'variation_pct': 1.93, 'volume': 25000, 'sector': 'Télécommunications'},
        {'ticker': 'LHM', 'name': 'LafargeHolcim', 'price': 1850.00, 
         'variation_pct': 0.54, 'volume': 5000, 'sector': 'Matériaux'},
        {'ticker': 'ADH', 'name': 'Addoha', 'price': 35.89, 
         'variation_pct': -0.25, 'volume': 12000, 'sector': 'Immobilier'},
    ]
    
    analytics = MarketAnalytics()
    
    breadth = analytics.calculate_market_breadth(sample_stocks)
    print(f"\nMarket Breadth:")
    print(f"  Advancing: {breadth['advancing']}")
    print(f"  Declining: {breadth['declining']}")
    print(f"  A/D Ratio: {breadth['advance_decline_ratio']}")
    print(f"  Sentiment: {breadth['market_sentiment']}")
    
    sectors = analytics.sector_analysis(sample_stocks)
    print(f"\nSector Analysis:")
    print(f"  Best Sector: {sectors['best_sector']}")
    print(f"  Worst Sector: {sectors['worst_sector']}")
