import pytest
import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from httpx import AsyncClient

from app.main import app
from app.utils.database import Base, get_db
from app.config import settings


TEST_DATABASE_URL = "postgresql+asyncpg://test_user:test_pass@localhost:5432/test_crypto_db"


@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
async def test_engine():
    engine = create_async_engine(TEST_DATABASE_URL, echo=True)
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    yield engine
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    
    await engine.dispose()


@pytest.fixture
async def test_db(test_engine):
    async_session = sessionmaker(
        test_engine, class_=AsyncSession, expire_on_commit=False
    )
    
    async with async_session() as session:
        yield session


@pytest.fixture
async def client(test_db):
    async def override_get_db():
        yield test_db
    
    app.dependency_overrides[get_db] = override_get_db
    
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac
    
    app.dependency_overrides.clear()


@pytest.fixture
def sample_alert_data():
    return {
        "userId": 1,
        "symbol": "BTC-USD",
        "condition": "PRICE_ABOVE",
        "threshold": 50000,
        "channels": ["EMAIL"]
    }


@pytest.fixture
def sample_portfolio_data():
    return {
        "userId": 1,
        "name": "Test Portfolio",
        "riskProfile": "MEDIUM",
        "targetAllocations": {
            "BTC-USD": 0.5,
            "ETH-USD": 0.5
        }
    }
