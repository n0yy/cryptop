from langchain.tools import BaseTool
from typing import Optional
from pydantic import Field
import httpx

from app.config import settings
from app.utils.logger import logger


class CoinGeckoTool(BaseTool):
    name: str = "coingecko_market_data"
    description: str = """
    Fetches real-time cryptocurrency market data from CoinGecko.
    Input should be a cryptocurrency symbol (e.g., 'bitcoin', 'ethereum').
    Returns current price, market cap, volume, and price changes.
    """
    
    async def _arun(self, symbol: str) -> str:
        try:
            symbol = symbol.lower().replace("-usd", "").replace("usd", "")
            
            async with httpx.AsyncClient() as client:
                url = f"{settings.COINGECKO_BASE_URL}/coins/{symbol}"
                params = {
                    "localization": "false",
                    "tickers": "false",
                    "community_data": "false",
                    "developer_data": "false"
                }
                
                if settings.COINGECKO_API_KEY:
                    params["x_cg_pro_api_key"] = settings.COINGECKO_API_KEY
                
                response = await client.get(url, params=params, timeout=10.0)
                response.raise_for_status()
                
                data = response.json()
                market_data = data.get("market_data", {})
                
                result = {
                    "symbol": symbol,
                    "name": data.get("name"),
                    "current_price": market_data.get("current_price", {}).get("usd"),
                    "market_cap": market_data.get("market_cap", {}).get("usd"),
                    "total_volume": market_data.get("total_volume", {}).get("usd"),
                    "price_change_24h": market_data.get("price_change_percentage_24h"),
                    "price_change_7d": market_data.get("price_change_percentage_7d"),
                    "price_change_30d": market_data.get("price_change_percentage_30d"),
                    "high_24h": market_data.get("high_24h", {}).get("usd"),
                    "low_24h": market_data.get("low_24h", {}).get("usd"),
                    "ath": market_data.get("ath", {}).get("usd"),
                    "atl": market_data.get("atl", {}).get("usd")
                }
                
                logger.info(f"Fetched CoinGecko data for {symbol}")
                
                return str(result)
        
        except Exception as e:
            logger.error(f"CoinGecko tool error: {e}")
            return f"Error fetching data from CoinGecko: {str(e)}"
    
    def _run(self, symbol: str) -> str:
        raise NotImplementedError("Use async version")
