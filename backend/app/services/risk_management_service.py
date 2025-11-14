from typing import List, Dict, Optional, Any
import numpy as np
from sqlalchemy.ext.asyncio import AsyncSession


class RiskManagementService:
    """Service for handling risk management calculations."""
    
    def __init__(self, db: Optional[AsyncSession] = None):
        self.db = db

    def calculate_position_size(self, risk_tolerance: str, portfolio_value: float) -> float:
        """Calculate recommended position size based on risk tolerance and portfolio value."""
        risk_tolerance = risk_tolerance.upper()
        if risk_tolerance == 'LOW':
            risk_factor = 0.01  # 1% of portfolio
        elif risk_tolerance == 'MEDIUM':
            risk_factor = 0.02  # 2% of portfolio
        elif risk_tolerance == 'HIGH':
            risk_factor = 0.05  # 5% of portfolio
        else:
            raise ValueError(f"Invalid risk tolerance: {risk_tolerance}. Must be LOW, MEDIUM, or HIGH.")
        return portfolio_value * risk_factor

    def calculate_liquidation_price(self, entry_price: float, quantity: float, leverage: float, collateral: float) -> float:
        """Calculate liquidation price for a leveraged position (assuming long position)."""
        # Simplified formula: liquidation occurs when loss equals collateral
        # Loss = quantity * (entry_price - current_price)
        # Set loss = collateral => current_price = entry_price - collateral / quantity
        # Leverage is provided for context but not directly used, as collateral determines the margin
        # In practice, collateral ≈ (quantity * entry_price) / leverage
        if quantity <= 0:
            raise ValueError("Quantity must be positive for long position.")
        return entry_price - (collateral / quantity)

    def perform_correlation_analysis(self, symbols: List[str], historical_data: Optional[Dict[str, List[float]]] = None) -> Dict[str, Any]:
        """Perform correlation risk analysis on asset symbols."""
        if historical_data is None or not historical_data:
            raise ValueError("Historical data must be provided for correlation analysis.")
        
        # Validate that all symbols have data
        for symbol in symbols:
            if symbol not in historical_data or len(historical_data[symbol]) < 2:
                raise ValueError(f"Insufficient historical data for symbol: {symbol}")
        
        # Compute daily returns for each symbol
        returns = {}
        for symbol in symbols:
            prices = np.array(historical_data[symbol])
            if len(prices) < 2:
                raise ValueError(f"Insufficient data points for {symbol}")
            daily_returns = np.diff(prices) / prices[:-1]
            returns[symbol] = daily_returns
        
        # Stack returns into a matrix (rows: time, columns: symbols)
        returns_matrix = np.column_stack([returns[symbol] for symbol in symbols])
        
        # Compute correlation matrix
        corr_matrix = np.corrcoef(returns_matrix)
        
        # Convert to dict for JSON serialization
        corr_dict = {}
        for i, sym1 in enumerate(symbols):
            corr_dict[sym1] = {}
            for j, sym2 in enumerate(symbols):
                corr_dict[sym1][sym2] = float(corr_matrix[i, j])
        
        # Identify highly correlated pairs (threshold > 0.7 or < -0.7)
        high_correlations = []
        threshold = 0.7
        for i, sym1 in enumerate(symbols):
            for j in range(i+1, len(symbols)):
                sym2 = symbols[j]
                corr = corr_matrix[i, j]
                if abs(corr) > threshold:
                    high_correlations.append({
                        'pair': (sym1, sym2),
                        'correlation': float(corr)
                    })
        
        return {
            'correlation_matrix': corr_dict,
            'high_correlations': high_correlations,
            'symbols': symbols,
            'threshold': threshold
        }
