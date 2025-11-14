import pytest
from app.alerts.engine import AlertEngine
from app.models.alert import Alert


@pytest.mark.asyncio
async def test_alert_engine_initialization(test_db):
    engine = AlertEngine(test_db)
    assert engine is not None
    assert engine.db is not None


@pytest.mark.asyncio
async def test_check_alerts_empty(test_db):
    engine = AlertEngine(test_db)
    triggered_count = await engine.check_alerts()
    assert triggered_count == 0


@pytest.mark.asyncio
async def test_evaluate_alert_price_above(test_db):
    engine = AlertEngine(test_db)
    
    alert = Alert(
        user_id=1,
        symbol="BTC-USD",
        condition="PRICE_ABOVE",
        threshold=1000,
        status="ACTIVE",
        channels=["EMAIL"]
    )
    
    test_db.add(alert)
    await test_db.commit()
    
    result = await engine._evaluate_alert(alert)
    assert isinstance(result, bool)
