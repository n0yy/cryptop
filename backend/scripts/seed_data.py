import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from app.config import settings
from app.models.user import User
from app.utils.security import get_password_hash
from app.utils.logger import logger


async def seed_database():
    engine = create_async_engine(
        settings.DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://"),
        echo=True
    )
    
    async_session = sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )
    
    async with async_session() as session:
        try:
            demo_user = User(
                email="demo@cryptomonitoring.com",
                password_hash=get_password_hash("demo123"),
                preferences={
                    "notifications": {
                        "email": True,
                        "sms": False,
                        "discord": True
                    },
                    "default_currency": "USD",
                    "theme": "dark"
                }
            )
            
            session.add(demo_user)
            await session.commit()
            
            logger.info("Database seeded successfully")
            logger.info("Demo user created: demo@cryptomonitoring.com / demo123")
        
        except Exception as e:
            logger.error(f"Error seeding database: {e}")
            await session.rollback()
        
        finally:
            await engine.dispose()


if __name__ == "__main__":
    asyncio.run(seed_database())
