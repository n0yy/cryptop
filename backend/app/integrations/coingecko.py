import httpx
from typing import Optional, Dict, List

from app.config import settings
from app.utils.logger import logger
from app.utils.cache import cache_get, cache_set


class CoinGeckoClient:
    def __init__(self):
        self.base_url = settings.COINGECKO_BASE_URL
        self.api_key = settings.COINGECKO_API_KEY
    
    async def get_current_price(self, symbol: str) -> Optional[float]:
        cache_key = f"coingecko:price:{symbol}"
        cached = await cache_get(cache_key)
        
        if cached:
            return cached.get("price")
        
        try:
            symbol = symbol.lower().replace("-usd", "").replace("usd", "")
            
            async with httpx.AsyncClient() as client:
                url = f"{self.base_url}/simple/price"
                params = {
                    "ids": symbol,
                    "vs_currencies": "usd"
                }
                
                if self.api_key:
                    params["x_cg_pro_api_key"] = self.api_key
                
                response = await client.get(url, params=params, timeout=10.0)
                response.raise_for_status()
                
                data = response.json()
                price = data.get(symbol, {}).get("usd")
                
                if price:
                    await cache_set(cache_key, {"price": price}, ttl=60)
                
                return price
        
        except Exception as e:
            logger.error(f"Error fetching price from CoinGecko: {e}")
            return None
    
    async def get_coin_data(self, symbol: str) -> Dict:
        try:
            symbol = symbol.lower().replace("-usd", "").replace("usd", "")
            
            async with httpx.AsyncClient() as client:
                url = f"{self.base_url}/coins/{symbol}"
                params = {
                    "localization": "false",
                    "tickers": "false",
                    "community_data": "false",
                    "developer_data": "false"
                }
                
                if self.api_key:
                    params["x_cg_pro_api_key"] = self.api_key
                
                response = await client.get(url, params=params, timeout=10.0)
                response.raise_for_status()
                
                data = response.json()
                market_data = data.get("market_data", {})
                
                return {
                    "current_price": market_data.get("current_price", {}).get("usd"),
                    "market_cap": market_data.get("market_cap", {}).get("usd"),
                    "volume_24h": market_data.get("total_volume", {}).get("usd"),
                    "price_change_24h": market_data.get("price_change_percentage_24h")
                }
        
        except Exception as e:
            logger.error(f"Error fetching coin data from CoinGecko: {e}")
            return {}
    
    async def get_price_history(self, symbol: str, days: str = "90") -> List:
        try:
            symbol = symbol.lower().replace("-usd", "").replace("usd", "")
            days_num = int(days.replace("d", ""))
            
            async with httpx.AsyncClient() as client:
                url = f"{self.base_url}/coins/{symbol}/market_chart"
                params = {
                    "vs_currency": "usd",
                    "days": days_num
                }
                
                if self.api_key:
                    params["x_cg_pro_api_key"] = self.api_key
                
                response = await client.get(url, params=params, timeout=10.0)
                response.raise_for_status()
                
                data = response.json()
                return data.get("prices", [])
        
        except Exception as e:
            logger.error(f"Error fetching price history from CoinGecko: {e}")
            return []
