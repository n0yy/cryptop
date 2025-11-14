from typing import Dict, List
import pandas as pd
import numpy as np
from datetime import datetime
import uuid

from app.integrations.coingecko import CoinGeckoClient
from app.utils.logger import logger


class BacktestEngine:
    def __init__(self):
        self.coingecko = CoinGeckoClient()
    
    async def run_backtest(
        self,
        strategy_name: str,
        symbol: str,
        period: str,
        parameters: Dict,
        initial_capital: float
    ) -> Dict:
        try:
            backtest_id = f"BT-{datetime.now().strftime('%Y%m%d')}-{uuid.uuid4().hex[:6].upper()}"
            
            price_data = await self._fetch_historical_data(symbol, period)
            
            if price_data.empty:
                raise ValueError("No historical data available")
            
            trades = self._execute_strategy(price_data, strategy_name, parameters)
            
            results = self._calculate_metrics(trades, initial_capital)
            
            equity_curve_url = await self._generate_equity_curve(backtest_id, trades)
            
            return {
                "backtestId": backtest_id,
                "strategyName": strategy_name,
                "results": results,
                "equityCurveUrl": equity_curve_url,
                "completedAt": datetime.utcnow().isoformat()
            }
        
        except Exception as e:
            logger.error(f"Backtest error: {e}")
            raise
    
    async def _fetch_historical_data(self, symbol: str, period: str) -> pd.DataFrame:
        days = period.replace("y", "").replace("d", "")
        if "y" in period:
            days = str(int(days) * 365)
        
        price_history = await self.coingecko.get_price_history(symbol, days)
        
        df = pd.DataFrame(price_history, columns=["timestamp", "price"])
        df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms")
        df.set_index("timestamp", inplace=True)
        
        return df
    
    def _execute_strategy(self, price_data: pd.DataFrame, strategy_name: str, parameters: Dict) -> List[Dict]:
        trades = []
        
        if strategy_name == "RSI Mean Reversion":
            rsi_period = parameters.get("rsiPeriod", 14)
            buy_threshold = parameters.get("buyThreshold", 30)
            sell_threshold = parameters.get("sellThreshold", 70)
            
            delta = price_data["price"].diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=rsi_period).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=rsi_period).mean()
            rs = gain / loss
            rsi = 100 - (100 / (1 + rs))
            
            position = None
            
            for i in range(len(price_data)):
                if i < rsi_period:
                    continue
                
                current_rsi = rsi.iloc[i]
                current_price = price_data["price"].iloc[i]
                
                if position is None and current_rsi < buy_threshold:
                    position = {
                        "entry_price": current_price,
                        "entry_time": price_data.index[i]
                    }
                
                elif position is not None and current_rsi > sell_threshold:
                    trades.append({
                        "entry_price": position["entry_price"],
                        "exit_price": current_price,
                        "entry_time": position["entry_time"],
                        "exit_time": price_data.index[i],
                        "pnl": current_price - position["entry_price"]
                    })
                    position = None
        
        return trades
    
    def _calculate_metrics(self, trades: List[Dict], initial_capital: float) -> Dict:
        if not trades:
            return {
                "totalReturn": 0.0,
                "sharpeRatio": 0.0,
                "maxDrawdown": 0.0,
                "winRate": 0.0,
                "totalTrades": 0,
                "profitFactor": 0.0
            }
        
        total_pnl = sum(trade["pnl"] for trade in trades)
        total_return = total_pnl / initial_capital
        
        winning_trades = [t for t in trades if t["pnl"] > 0]
        win_rate = len(winning_trades) / len(trades) if trades else 0
        
        gross_profit = sum(t["pnl"] for t in winning_trades)
        gross_loss = abs(sum(t["pnl"] for t in trades if t["pnl"] < 0))
        profit_factor = gross_profit / gross_loss if gross_loss > 0 else 0
        
        returns = [t["pnl"] / initial_capital for t in trades]
        sharpe_ratio = (np.mean(returns) / np.std(returns)) * np.sqrt(252) if returns else 0
        
        equity_curve = np.cumsum([t["pnl"] for t in trades])
        running_max = np.maximum.accumulate(equity_curve)
        drawdown = (equity_curve - running_max) / running_max
        max_drawdown = np.min(drawdown) if len(drawdown) > 0 else 0
        
        return {
            "totalReturn": round(total_return, 2),
            "sharpeRatio": round(sharpe_ratio, 2),
            "maxDrawdown": round(max_drawdown, 2),
            "winRate": round(win_rate, 2),
            "totalTrades": len(trades),
            "profitFactor": round(profit_factor, 2)
        }
    
    async def _generate_equity_curve(self, backtest_id: str, trades: List[Dict]) -> str:
        return f"https://cdn.example.com/backtest/{backtest_id}.png"
