import pytest
import asyncio
from unittest.mock import AsyncMock, patch, MagicMock
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, insert, and_
from datetime import datetime, timedelta

import numpy as np

from app.services.risk_management_service import RiskManagementService
from app.services.alert_service import AlertService
from app.services.portfolio_service import PortfolioService
from app.models.user import User
from app.models.portfolio import Portfolio
from app.models.position import Position
from app.models.alert import Alert
from app.schemas.alert_schema import AlertCondition
from app.integrations.coingecko import CoinGeckoClient
from app.utils.database import get_db
from app.api.risk import router as risk_router


@pytest.mark.asyncio
class TestRiskManagementService:
    @pytest.fixture
def risk_service(self):
        return RiskManagementService()

    def test_calculate_position_size(self, risk_service):
        # Test LOW risk tolerance
        size = risk_service.calculate_position_size("LOW", 10000)
        assert size == 100.0  # 1% of 10k

        # Test MEDIUM
        size = risk_service.calculate_position_size("MEDIUM", 10000)
        assert size == 200.0  # 2%

        # Test HIGH
        size = risk_service.calculate_position_size("HIGH", 10000)
        assert size == 500.0  # 5%

        # Test invalid tolerance
        with pytest.raises(ValueError):
            risk_service.calculate_position_size("INVALID", 10000)

    def test_calculate_liquidation_price(self, risk_service):
        # Test long position liquidation (simplified: entry - (collateral / quantity))
        liq_price = risk_service.calculate_liquidation_price(50000, 0.1, 10, 500)
        assert liq_price == 45000.0  # 500 / 0.1 = 5000, 50000 - 5000 = 45000

        # Test zero quantity raises error
        with pytest.raises(ValueError):
            risk_service.calculate_liquidation_price(50000, 0, 10, 500)

    @patch.object(CoinGeckoClient, "get_price_history")
    async def test_perform_correlation_analysis(self, mock_get_history, risk_service):
        # Mock historical data for two symbols (correlated)
        mock_data_btc = [(1000, 100), (1010, 102), (1020, 104), (1030, 106)]
        mock_data_eth = [(1000, 1000), (1010, 1020), (1020, 1040), (1030, 1060)]
        mock_get_history.side_effect = [mock_data_btc, mock_data_eth]

        symbols = ["btc", "eth"]
        historical_data = {
            "btc": [100, 102, 104, 106],
            "eth": [1000, 1020, 1040, 1060]
        }
        analysis = risk_service.perform_correlation_analysis(symbols, historical_data)

        assert "correlation_matrix" in analysis
        assert "high_correlation_pairs" in analysis
        assert len(analysis["high_correlation_pairs"]) > 0  # Should detect correlation > 0.7

        # Test with insufficient data
        short_data = {"btc": [100]}
        analysis_short = risk_service.perform_correlation_analysis(["btc"], short_data)
        assert analysis_short["error"] == "Insufficient historical data for correlation analysis"


@pytest.mark.asyncio
class TestRiskAPIEndpoints:
    async def test_calculate_position_size_endpoint(self, client, test_db):
        response = await client.post("/api/risk/position-size", json={
            "riskTolerance": "MEDIUM",
            "portfolioValue": 10000
        })
        assert response.status_code == 200
        data = response.json()
        assert data["recommendedSize"] == 200.0

    async def test_calculate_liquidation_price_endpoint(self, client, test_db):
        response = await client.post("/api/risk/liquidation-price", json={
            "entryPrice": 50000,
            "quantity": 0.1,
            "leverage": 10,
            "collateral": 500
        })
        assert response.status_code == 200
        data = response.json()
        assert data["liquidationPrice"] == 45000.0

    async def test_update_position_risk(self, client, test_db):
        # Create test portfolio and position first
        user = User(id=1, username="test", email="test@example.com", created_at=datetime.utcnow())
        test_db.add(user)
        await test_db.commit()

        portfolio = Portfolio(
            id=1, user_id=1, name="Test", risk_profile="MEDIUM",
            target_allocations={}, created_at=datetime.utcnow(), updated_at=datetime.utcnow()
        )
        test_db.add(portfolio)
        await test_db.commit()

        position = Position(
            id=1, portfolio_id=1, symbol="BTC", quantity=0.1, entry_price=50000,
            entry_date=datetime.utcnow(), created_at=datetime.utcnow(), updated_at=datetime.utcnow()
        )
        test_db.add(position)
        await test_db.commit()

        # Update risk params
        response = await client.put("/api/risk/positions/1/risk", json={
            "stopLossPrice": 45000,
            "takeProfitPrice": 55000,
            "leverage": 5,
            "collateral": 1000
        })
        assert response.status_code == 200
        data = response.json()
        assert data["updatedFields"] == ["stopLossPrice", "takeProfitPrice", "leverage", "collateral"]

        # Verify in DB
        result = await test_db.execute(select(Position).where(Position.id == 1))
        updated_pos = result.scalar_one()
        assert updated_pos.stop_loss_price == 45000
        assert updated_pos.take_profit_price == 55000
        assert updated_pos.leverage == 5
        assert updated_pos.collateral == 1000


@pytest.mark.asyncio
class TestRiskAlertChecking:
    async def test_alert_triggering_and_position_closure(self, test_db):
        # Setup test data
        user = User(id=1, username="test", email="test@example.com", created_at=datetime.utcnow())
        test_db.add(user)
        await test_db.commit()

        portfolio = Portfolio(
            id=1, user_id=1, name="Test", risk_profile="MEDIUM",
            target_allocations={}, created_at=datetime.utcnow(), updated_at=datetime.utcnow()
        )
        test_db.add(portfolio)
        await test_db.commit()

        # Create open position
        position = Position(
            id=1, portfolio_id=1, symbol="BTC", quantity=0.1, entry_price=50000,
            entry_date=datetime.utcnow(), stop_loss_price=45000, created_at=datetime.utcnow(), updated_at=datetime.utcnow()
        )
        test_db.add(position)
        await test_db.commit()

        # Create STOP_LOSS alert
        alert = Alert(
            id=1, user_id=1, symbol="BTC", condition=AlertCondition.STOP_LOSS,
            threshold=45000, status="ACTIVE", channels=["EMAIL"],
            created_at=datetime.utcnow(), metadata=None
        )
        test_db.add(alert)
        await test_db.commit()

        # Mock CoinGecko to return price below threshold
        with patch("app.integrations.coingecko.CoinGeckoClient.get_current_price", new_callable=AsyncMock) as mock_price:
            mock_price.return_value = 44000  # Below stop loss

            # Mock PortfolioService for drawdown (not used here)
            with patch("app.services.alert_service.PortfolioService") as mock_portfolio:
                mock_portfolio_instance = AsyncMock()
                mock_portfolio.return_value = mock_portfolio_instance
                mock_portfolio_instance.get_user_portfolios.return_value = [{"portfolioId": 1}]
                mock_portfolio_instance.get_portfolio.return_value = {"positions": [{"quantity": 0.1, "entryPrice": 50000}]}
                mock_portfolio_instance.get_portfolio_analysis.return_value = {"totalValue": 4400}

                # Create AlertService and call check
                alert_service = AlertService(test_db)
                triggered = await alert_service.check_and_trigger_all_risk_alerts()

                assert triggered == 1

                # Verify alert triggered
                result = await test_db.execute(select(Alert).where(Alert.id == 1))
                updated_alert = result.scalar_one()
                assert updated_alert.status == "TRIGGERED"
                assert updated_alert.triggered_at is not None

                # Verify position closed (quantity = 0)
                pos_result = await test_db.execute(select(Position).where(Position.id == 1))
                updated_pos = pos_result.scalar_one()
                assert updated_pos.quantity == 0

                # Verify metadata has execution details
                import json
                details = json.loads(updated_alert.metadata)
                assert "execution_details" in details
                assert details["execution_details"]["action"] == "STOP_LOSS"
                assert len(details["execution_details"]["closed_positions"]) == 1
                assert details["execution_details"]["closed_positions"][0]["position_id"] == 1

    async def test_drawdown_alert(self, test_db):
        # Setup user, portfolio, position with entry value 5000 (0.1 BTC * 50000)
        user = User(id=1, username="test", email="test@example.com", created_at=datetime.utcnow())
        test_db.add(user)
        await test_db.commit()

        portfolio = Portfolio(
            id=1, user_id=1, name="Test", risk_profile="MEDIUM",
            target_allocations={}, created_at=datetime.utcnow(), updated_at=datetime.utcnow()
        )
        test_db.add(portfolio)
        await test_db.commit()

        position = Position(
            id=1, portfolio_id=1, symbol="BTC", quantity=0.1, entry_price=50000,
            entry_date=datetime.utcnow(), created_at=datetime.utcnow(), updated_at=datetime.utcnow()
        )
        test_db.add(position)
        await test_db.commit()

        # Create DRAWDOWN_THRESHOLD alert at 15% (threshold=15)
        alert = Alert(
            id=2, user_id=1, symbol=None, condition=AlertCondition.DRAWDOWN_THRESHOLD,
            threshold=15, status="ACTIVE", channels=["EMAIL"],
            created_at=datetime.utcnow(), metadata=None
        )
        test_db.add(alert)
        await test_db.commit()

        # Mock PortfolioService to return current value 4000 (20% drawdown)
        with patch("app.services.alert_service.PortfolioService") as mock_portfolio:
            mock_portfolio_instance = AsyncMock()
            mock_portfolio.return_value = mock_portfolio_instance
            mock_portfolio_instance.get_user_portfolios.return_value = [{"portfolioId": 1}]
            mock_portfolio_instance.get_portfolio.return_value = {"positions": [{"quantity": 0.1, "entryPrice": 50000}]}
            mock_portfolio_instance.get_portfolio_analysis.return_value = {"totalValue": 4000}  # 20% drawdown

            alert_service = AlertService(test_db)
            triggered = await alert_service.check_and_trigger_all_risk_alerts()

            assert triggered == 1

            # Verify alert triggered
            result = await test_db.execute(select(Alert).where(Alert.id == 2))
            updated_alert = result.scalar_one()
            assert updated_alert.status == "TRIGGERED"
            assert updated_alert.triggered_at is not None

            # Position should NOT be closed for drawdown
            pos_result = await test_db.execute(select(Position).where(Position.id == 1))
            updated_pos = pos_result.scalar_one()
            assert updated_pos.quantity == 0.1  # Unchanged

            # Verify metadata has drawdown details
            import json
            details = json.loads(updated_alert.metadata)
            assert "execution_details" in details
            assert details["execution_details"]["action"] == "DRAWDOWN_ALERT"
            assert details["execution_details"]["drawdown_percent"] == -20.0

    @patch("app.integrations.coingecko.CoinGeckoClient.get_current_price")
    async def test_no_trigger_if_condition_not_met(self, mock_price, test_db):
        mock_price.return_value = 50000  # Above threshold, no trigger

        # Setup similar to SL test
        user = User(id=1, username="test", email="test@example.com", created_at=datetime.utcnow())
        test_db.add(user)
        await test_db.commit()

        portfolio = Portfolio(
            id=1, user_id=1, name="Test", risk_profile="MEDIUM",
            target_allocations={}, created_at=datetime.utcnow(), updated_at=datetime.utcnow()
        )
        test_db.add(portfolio)
        await test_db.commit()

        position = Position(
            id=1, portfolio_id=1, symbol="BTC", quantity=0.1, entry_price=50000,
            entry_date=datetime.utcnow(), stop_loss_price=45000, created_at=datetime.utcnow(), updated_at=datetime.utcnow()
        )
        test_db.add(position)
        await test_db.commit()

        alert = Alert(
            id=1, user_id=1, symbol="BTC", condition=AlertCondition.STOP_LOSS,
            threshold=45000, status="ACTIVE", channels=["EMAIL"],
            created_at=datetime.utcnow(), metadata=None
        )
        test_db.add(alert)
        await test_db.commit()

        with patch("app.services.alert_service.PortfolioService") as mock_portfolio:
            mock_portfolio_instance = AsyncMock()
            mock_portfolio.return_value = mock_portfolio_instance
            mock_portfolio_instance.get_user_portfolios.return_value = [{"portfolioId": 1}]
            mock_portfolio_instance.get_portfolio.return_value = {"positions": [{"quantity": 0.1, "entryPrice": 50000}]}
            mock_portfolio_instance.get_portfolio_analysis.return_value = {"totalValue": 5000}

            alert_service = AlertService(test_db)
            triggered = await alert_service.check_and_trigger_all_risk_alerts()
            assert triggered == 0

            # Alert status remains ACTIVE
            result = await test_db.execute(select(Alert).where(Alert.id == 1))
            updated_alert = result.scalar_one()
            assert updated_alert.status == "ACTIVE"

            # Position unchanged
            pos_result = await test_db.execute(select(Position).where(Position.id == 1))
            updated_pos = pos_result.scalar_one()
            assert updated_pos.quantity == 0.1
EOF'