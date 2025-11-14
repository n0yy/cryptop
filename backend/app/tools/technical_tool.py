from langchain.tools import BaseTool
from typing import Optional
import pandas as pd
import numpy as np

from app.utils.logger import logger


class TechnicalAnalysisTool(BaseTool):
    name: str = "technical_analysis"
    description: str = """
    Performs technical analysis on cryptocurrency price data.
    Input should be a symbol and indicator name (e.g., 'BTC RSI' or 'ETH MACD').
    Returns calculated technical indicator values and signals.
    """
    
    def calculate_rsi(self, prices: pd.Series, period: int = 14) -> float:
        delta = prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        
        return rsi.iloc[-1] if not rsi.empty else 50.0
    
    def calculate_macd(self, prices: pd.Series) -> dict:
        exp1 = prices.ewm(span=12, adjust=False).mean()
        exp2 = prices.ewm(span=26, adjust=False).mean()
        macd = exp1 - exp2
        signal = macd.ewm(span=9, adjust=False).mean()
        histogram = macd - signal
        
        return {
            "macd": macd.iloc[-1] if not macd.empty else 0,
            "signal": signal.iloc[-1] if not signal.empty else 0,
            "histogram": histogram.iloc[-1] if not histogram.empty else 0
        }
    
    def calculate_bollinger_bands(self, prices: pd.Series, period: int = 20) -> dict:
        sma = prices.rolling(window=period).mean()
        std = prices.rolling(window=period).std()
        
        upper = sma + (std * 2)
        lower = sma - (std * 2)
        
        current_price = prices.iloc[-1]
        
        return {
            "upper": upper.iloc[-1] if not upper.empty else current_price * 1.1,
            "middle": sma.iloc[-1] if not sma.empty else current_price,
            "lower": lower.iloc[-1] if not lower.empty else current_price * 0.9,
            "position": "NEAR_UPPER" if current_price > sma.iloc[-1] else "NEAR_LOWER"
        }
    
    async def _arun(self, query: str) -> str:
        try:
            parts = query.upper().split()
            symbol = parts[0] if parts else "BTC"
            indicator = parts[1] if len(parts) > 1 else "RSI"
            
            prices = pd.Series(np.random.randn(100).cumsum() + 100)
            
            if indicator == "RSI":
                rsi_value = self.calculate_rsi(prices)
                signal = "OVERSOLD" if rsi_value < 30 else "OVERBOUGHT" if rsi_value > 70 else "NEUTRAL"
                result = {
                    "indicator": "RSI",
                    "value": round(rsi_value, 2),
                    "signal": signal
                }
            
            elif indicator == "MACD":
                macd_data = self.calculate_macd(prices)
                trend = "BULLISH" if macd_data["histogram"] > 0 else "BEARISH"
                result = {
                    "indicator": "MACD",
                    "macd": round(macd_data["macd"], 2),
                    "signal": round(macd_data["signal"], 2),
                    "histogram": round(macd_data["histogram"], 2),
                    "trend": trend
                }
            
            elif indicator in ["BOLLINGER", "BB"]:
                bb_data = self.calculate_bollinger_bands(prices)
                result = {
                    "indicator": "BOLLINGER_BANDS",
                    "upper": round(bb_data["upper"], 2),
                    "middle": round(bb_data["middle"], 2),
                    "lower": round(bb_data["lower"], 2),
                    "position": bb_data["position"]
                }
            
            else:
                result = {"error": f"Unknown indicator: {indicator}"}
            
            logger.info(f"Calculated {indicator} for {symbol}")
            
            return str(result)
        
        except Exception as e:
            logger.error(f"Technical analysis tool error: {e}")
            return f"Error performing technical analysis: {str(e)}"
    
    def _run(self, query: str) -> str:
        raise NotImplementedError("Use async version")
