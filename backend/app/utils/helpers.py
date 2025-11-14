from datetime import datetime
from typing import Any, Dict
import time


def create_response(data: Any, status: str = "success") -> Dict:
    return {
        "status": status,
        "data": data,
        "timestamp": datetime.utcnow().isoformat()
    }


def create_error_response(code: str, message: str) -> Dict:
    return {
        "status": "error",
        "code": code,
        "message": message,
        "timestamp": datetime.utcnow().isoformat()
    }


def calculate_percentage_change(old_value: float, new_value: float) -> float:
    if old_value == 0:
        return 0.0
    return ((new_value - old_value) / old_value) * 100


def format_currency(amount: float, decimals: int = 2) -> str:
    return f"${amount:,.{decimals}f}"


def get_unix_timestamp() -> int:
    return int(time.time())


def parse_timeframe(timeframe: str) -> int:
    unit = timeframe[-1]
    value = int(timeframe[:-1])
    
    multipliers = {
        'm': 60,
        'h': 3600,
        'd': 86400,
        'w': 604800,
        'M': 2592000,
        'y': 31536000
    }
    
    return value * multipliers.get(unit, 3600)
