from typing import Dict
import random

from app.utils.logger import logger


class SentimentAnalyzer:
    def __init__(self):
        pass
    
    async def analyze(self, symbol: str) -> Dict:
        try:
            sentiment_score = random.uniform(0.3, 0.9)
            fear_greed_index = random.randint(20, 80)
            social_volume = random.randint(50000, 200000)
            
            return {
                "score": round(sentiment_score, 2),
                "fearGreedIndex": fear_greed_index,
                "socialVolume": social_volume
            }
        except Exception as e:
            logger.error(f"Error analyzing sentiment: {e}")
            return {
                "score": 0.5,
                "fearGreedIndex": 50,
                "socialVolume": 0
            }
