from typing import Optional
import logging

logger = logging.getLogger(__name__)


class PositionSizingCalculator:
    """
    Calculator for determining optimal position size based on risk management principles.
    Uses the Kelly Criterion variant or fixed risk percentage for position sizing.
    """

    RISK_PROFILE_MAPPING = {
        "LOW": 1.0,    # 1% risk per trade
        "MEDIUM": 2.0, # 2% risk per trade
        "HIGH": 3.0    # 3% risk per trade
    }

    @classmethod
    def get_risk_percent_from_profile(cls, risk_profile: str) -> float:
        """
        Get risk percentage based on user's risk profile.
        
        Args:
            risk_profile: User's risk profile (LOW, MEDIUM, HIGH)
        
        Returns:
            Risk percentage per trade
        """
        return cls.RISK_PROFILE_MAPPING.get(risk_profile.upper(), 2.0)

    @staticmethod
    def calculate_position_size(
        account_balance: float,
        risk_per_trade_percent: float,
        entry_price: float,
        stop_loss_price: float,
        asset_volatility: Optional[float] = None
    ) -> float:
        """
        Calculate the recommended quantity for a position.
        
        Formula: quantity = (account_balance * risk_percent / 100) / (entry_price - stop_loss_price)
        Adjusted for volatility if provided.
        
        Args:
            account_balance: Current account balance
            risk_per_trade_percent: Risk percentage per trade (e.g., 2.0)
            entry_price: Planned entry price
            stop_loss_price: Stop loss price level
            asset_volatility: Optional volatility factor (0-1, higher = smaller position)
        
        Returns:
            Recommended position quantity (rounded to 8 decimals)
        
        Raises:
            ValueError: If stop_loss_price >= entry_price or invalid inputs
        """
        if account_balance <= 0:
            raise ValueError("Account balance must be positive")
        if risk_per_trade_percent <= 0:
            raise ValueError("Risk per trade must be positive")
        if entry_price <= 0 or stop_loss_price <= 0:
            raise ValueError("Prices must be positive")
        if stop_loss_price >= entry_price:
            raise ValueError("Stop loss price must be below entry price for long positions")

        risk_amount = account_balance * (risk_per_trade_percent / 100.0)
        price_risk = entry_price - stop_loss_price

        # Adjust for volatility (reduce position size for higher volatility)
        if asset_volatility and 0 < asset_volatility <= 1:
            volatility_factor = 1 / (1 + asset_volatility)
            adjusted_risk_amount = risk_amount * volatility_factor
        else:
            adjusted_risk_amount = risk_amount

        quantity = adjusted_risk_amount / price_risk
        return round(quantity, 8)

