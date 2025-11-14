from typing import Dict, List
import pandas as pd
import numpy as np

from app.integrations.coingecko import CoinGeckoClient
from app.utils.logger import logger


class TechnicalAnalyzer:
    def __init__(self):
        self.coingecko = CoinGeckoClient()
    
    async def analyze(
        self,
        symbol: str,
        indicators: List[str],
        timeframes: List[str],
        period: str = "90d"
    ) -> Dict:
        price_data = await self._fetch_price_history(symbol, period)
        
        if price_data.empty:
            return {"indicators": {}, "chart_url": None}
        
        indicator_results = {}
        
        for indicator in indicators:
            if indicator == "RSI":
                indicator_results["RSI"] = self._calculate_rsi(price_data)
            elif indicator == "MACD":
                indicator_results["MACD"] = self._calculate_macd(price_data)
            elif indicator == "BOLLINGER_BANDS":
                indicator_results["BOLLINGER_BANDS"] = self._calculate_bollinger_bands(price_data)
            elif indicator == "SMA":
                indicator_results["SMA"] = self._calculate_sma(price_data)
            elif indicator == "EMA":
                indicator_results["EMA"] = self._calculate_ema(price_data)
        
        chart_url = await self._generate_chart(symbol, price_data, indicator_results)
        
        return {
            "indicators": indicator_results,
            "chart_url": chart_url
        }
    
    async def _fetch_price_history(self, symbol: str, period: str) -> pd.DataFrame:
        try:
            data = await self.coingecko.get_price_history(symbol, period)
            
            df = pd.DataFrame(data, columns=["timestamp", "price"])
            df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms")
            df.set_index("timestamp", inplace=True)
            
            return df
        except Exception as e:
            logger.error(f"Error fetching price history: {e}")
            return pd.DataFrame()
    
    def _calculate_rsi(self, df: pd.DataFrame, period: int = 14) -> Dict:
        delta = df["price"].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        
        current_rsi = rsi.iloc[-1] if not rsi.empty else 50.0
        
        signal = "OVERSOLD" if current_rsi < 30 else "OVERBOUGHT" if current_rsi > 70 else "NEUTRAL"
        
        return {
            "value": round(current_rsi, 2),
            "signal": signal
        }
    
    def _calculate_macd(self, df: pd.DataFrame) -> Dict:
        exp1 = df["price"].ewm(span=12, adjust=False).mean()
        exp2 = df["price"].ewm(span=26, adjust=False).mean()
        macd = exp1 - exp2
        signal = macd.ewm(span=9, adjust=False).mean()
        histogram = macd - signal
        
        trend = "BULLISH" if histogram.iloc[-1] > 0 else "BEARISH"
        
        return {
            "value": round(macd.iloc[-1], 2),
            "signal": round(signal.iloc[-1], 2),
            "histogram": round(histogram.iloc[-1], 2),
            "trend": trend
        }
    
    def _calculate_bollinger_bands(self, df: pd.DataFrame, period: int = 20) -> Dict:
        sma = df["price"].rolling(window=period).mean()
        std = df["price"].rolling(window=period).std()
        
        upper = sma + (std * 2)
        lower = sma - (std * 2)
        
        current_price = df["price"].iloc[-1]
        current_sma = sma.iloc[-1]
        
        position = "NEAR_UPPER" if current_price > current_sma else "NEAR_LOWER"
        
        return {
            "upper": round(upper.iloc[-1], 2),
            "middle": round(sma.iloc[-1], 2),
            "lower": round(lower.iloc[-1], 2),
            "position": position
        }
    
    def _calculate_sma(self, df: pd.DataFrame, period: int = 20) -> Dict:
        sma = df["price"].rolling(window=period).mean()
        
        return {
            "value": round(sma.iloc[-1], 2),
            "period": period
        }
    
    def _calculate_ema(self, df: pd.DataFrame, period: int = 20) -> Dict:
        ema = df["price"].ewm(span=period, adjust=False).mean()
        
        return {
            "value": round(ema.iloc[-1], 2),
            "period": period
        }
    
    async def _generate_chart(self, symbol: str, df: pd.DataFrame, indicators: Dict) -> str:
        return f"https://cdn.example.com/charts/{symbol}-{pd.Timestamp.now().strftime('%Y%m%d')}.png"
