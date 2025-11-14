from langchain.tools import BaseTool
from typing import Optional
import httpx

from app.config import settings
from app.utils.logger import logger


class CoinMarketCapTool(BaseTool):
    name: str = "coinmarketcap_data"
    description: str = """
    Fetches cryptocurrency rankings and quotes from CoinMarketCap.
    Input should be a cryptocurrency symbol (e.g., 'BTC', 'ETH').
    Returns ranking, price, volume, and market metrics.
    """
    
    async def _arun(self, symbol: str) -> str:
        try:
            symbol = symbol.upper().replace("-USD", "").replace("USD", "")
            
            async with httpx.AsyncClient() as client:
                url = f"{settings.COINMARKETCAP_BASE_URL}/cryptocurrency/quotes/latest"
                headers = {
                    "X-CMC_PRO_API_KEY": settings.COINMARKETCAP_API_KEY,
                    "Accept": "application/json"
                }
                params = {
                    "symbol": symbol,
                    "convert": "USD"
                }
                
                response = await client.get(url, headers=headers, params=params, timeout=10.0)
                response.raise_for_status()
                
                data = response.json()
                crypto_data = data.get("data", {}).get(symbol, {})
                quote = crypto_data.get("quote", {}).get("USD", {})
                
                result = {
                    "symbol": symbol,
                    "name": crypto_data.get("name"),
                    "rank": crypto_data.get("cmc_rank"),
                    "price": quote.get("price"),
                    "volume_24h": quote.get("volume_24h"),
                    "volume_change_24h": quote.get("volume_change_24h"),
                    "percent_change_1h": quote.get("percent_change_1h"),
                    "percent_change_24h": quote.get("percent_change_24h"),
                    "percent_change_7d": quote.get("percent_change_7d"),
                    "percent_change_30d": quote.get("percent_change_30d"),
                    "market_cap": quote.get("market_cap"),
                    "market_cap_dominance": quote.get("market_cap_dominance"),
                    "fully_diluted_market_cap": quote.get("fully_diluted_market_cap")
                }
                
                logger.info(f"Fetched CoinMarketCap data for {symbol}")
                
                return str(result)
        
        except Exception as e:
            logger.error(f"CoinMarketCap tool error: {e}")
            return f"Error fetching data from CoinMarketCap: {str(e)}"
    
    def _run(self, symbol: str) -> str:
        raise NotImplementedError("Use async version")
