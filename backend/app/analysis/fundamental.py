from typing import Dict, List
import asyncio

from app.integrations.coingecko import CoinGeckoClient
from app.integrations.coinmarketcap import CoinMarketCapClient
from app.analysis.sentiment import SentimentAnalyzer
from app.utils.logger import logger


class FundamentalAnalyzer:
    def __init__(self):
        self.coingecko = CoinGeckoClient()
        self.cmc = CoinMarketCapClient()
        self.sentiment_analyzer = SentimentAnalyzer()
    
    async def analyze(
        self,
        symbol: str,
        sources: List[str],
        include_onchain: bool = True,
        include_sentiment: bool = True,
        timeframe: str = "30d"
    ) -> Dict:
        tasks = []
        
        if "COINGECKO" in sources:
            tasks.append(self._fetch_coingecko_data(symbol))
        
        if "COINMARKETCAP" in sources:
            tasks.append(self._fetch_cmc_data(symbol))
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        market_data = self._aggregate_market_data(results)
        
        onchain_metrics = {}
        if include_onchain:
            onchain_metrics = await self._fetch_onchain_metrics(symbol)
        
        sentiment = {}
        if include_sentiment:
            sentiment = await self.sentiment_analyzer.analyze(symbol)
        
        recommendation = self._generate_recommendation(market_data, onchain_metrics, sentiment)
        
        return {
            "market_cap": market_data.get("market_cap", 0),
            "volume_24h": market_data.get("volume_24h", 0),
            "onchain_metrics": onchain_metrics,
            "sentiment": sentiment,
            "recommendation": recommendation["action"],
            "confidence": recommendation["confidence"]
        }
    
    async def _fetch_coingecko_data(self, symbol: str) -> Dict:
        try:
            data = await self.coingecko.get_coin_data(symbol)
            return {
                "source": "coingecko",
                "market_cap": data.get("market_cap"),
                "volume_24h": data.get("volume_24h"),
                "price": data.get("current_price")
            }
        except Exception as e:
            logger.error(f"Error fetching CoinGecko data: {e}")
            return {}
    
    async def _fetch_cmc_data(self, symbol: str) -> Dict:
        try:
            data = await self.cmc.get_quote(symbol)
            return {
                "source": "coinmarketcap",
                "market_cap": data.get("market_cap"),
                "volume_24h": data.get("volume_24h"),
                "price": data.get("price")
            }
        except Exception as e:
            logger.error(f"Error fetching CMC data: {e}")
            return {}
    
    def _aggregate_market_data(self, results: List[Dict]) -> Dict:
        valid_results = [r for r in results if isinstance(r, dict) and r]
        
        if not valid_results:
            return {}
        
        market_cap = sum(r.get("market_cap", 0) for r in valid_results) / len(valid_results)
        volume_24h = sum(r.get("volume_24h", 0) for r in valid_results) / len(valid_results)
        
        return {
            "market_cap": market_cap,
            "volume_24h": volume_24h
        }
    
    async def _fetch_onchain_metrics(self, symbol: str) -> Dict:
        return {
            "activeAddresses": 1000000,
            "whaleMovements": 15,
            "tvl": 25000000000
        }
    
    def _generate_recommendation(self, market_data: Dict, onchain: Dict, sentiment: Dict) -> Dict:
        score = 0.5
        
        if sentiment.get("score", 0.5) > 0.6:
            score += 0.2
        elif sentiment.get("score", 0.5) < 0.4:
            score -= 0.2
        
        if market_data.get("volume_24h", 0) > 10000000000:
            score += 0.1
        
        if score > 0.65:
            action = "BUY"
        elif score < 0.35:
            action = "SELL"
        else:
            action = "HOLD"
        
        return {
            "action": action,
            "confidence": min(abs(score - 0.5) * 2, 1.0)
        }
