import httpx
from typing import Optional, Dict

from app.config import settings
from app.utils.logger import logger


class CoinMarketCapClient:
    def __init__(self):
        self.base_url = settings.COINMARKETCAP_BASE_URL
        self.api_key = settings.COINMARKETCAP_API_KEY
    
    async def get_quote(self, symbol: str) -> Dict:
        try:
            symbol = symbol.upper().replace("-USD", "").replace("USD", "")
            
            async with httpx.AsyncClient() as client:
                url = f"{self.base_url}/cryptocurrency/quotes/latest"
                headers = {
                    "X-CMC_PRO_API_KEY": self.api_key,
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
                
                return {
                    "price": quote.get("price"),
                    "market_cap": quote.get("market_cap"),
                    "volume_24h": quote.get("volume_24h"),
                    "percent_change_24h": quote.get("percent_change_24h")
                }
        
        except Exception as e:
            logger.error(f"Error fetching quote from CoinMarketCap: {e}")
            return {}
