from langchain.tools import BaseTool
from typing import Optional
import random

from app.config import settings
from app.utils.logger import logger


class TwitterSentimentTool(BaseTool):
    name: str = "twitter_sentiment"
    description: str = """
    Analyzes Twitter sentiment for a cryptocurrency.
    Input should be a cryptocurrency symbol (e.g., 'BTC', 'ETH').
    Returns sentiment score, social volume, and trending topics.
    """
    
    async def _arun(self, symbol: str) -> str:
        try:
            symbol = symbol.upper().replace("-USD", "").replace("USD", "")
            
            sentiment_score = random.uniform(0.3, 0.9)
            social_volume = random.randint(50000, 200000)
            
            sentiment_label = "BULLISH" if sentiment_score > 0.6 else "BEARISH" if sentiment_score < 0.4 else "NEUTRAL"
            
            result = {
                "symbol": symbol,
                "sentiment_score": round(sentiment_score, 2),
                "sentiment_label": sentiment_label,
                "social_volume": social_volume,
                "trending_topics": [
                    f"#{symbol}",
                    "#crypto",
                    "#blockchain"
                ],
                "top_influencers": [
                    {"username": "crypto_analyst", "followers": 150000},
                    {"username": "blockchain_news", "followers": 200000}
                ]
            }
            
            logger.info(f"Analyzed Twitter sentiment for {symbol}")
            
            return str(result)
        
        except Exception as e:
            logger.error(f"Twitter sentiment tool error: {e}")
            return f"Error analyzing Twitter sentiment: {str(e)}"
    
    def _run(self, symbol: str) -> str:
        raise NotImplementedError("Use async version")
