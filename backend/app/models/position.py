from sqlalchemy import Column, BigInteger, String, DECIMAL, TIMESTAMP, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.models.base import Base


class Position(Base):
    __tablename__ = "positions"
    
    id = Column(BigInteger, primary_key=True, index=True)
    portfolio_id = Column(BigInteger, ForeignKey("portfolios.id"), nullable=False, index=True)
    symbol = Column(String(20), nullable=False, index=True)
    quantity = Column(DECIMAL(20, 8), nullable=False)
    entry_price = Column(DECIMAL(20, 8), nullable=False)
    entry_date = Column(TIMESTAMP, nullable=False)
    stop_loss_price = Column(DECIMAL(20, 8), nullable=True)
    take_profit_price = Column(DECIMAL(20, 8), nullable=True)
    leverage = Column(DECIMAL(20, 8), nullable=True)
    collateral = Column(DECIMAL(20, 8), nullable=True)
    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())
    
    portfolio = relationship("Portfolio", back_populates="positions")
    
    def __repr__(self):
        return f"<Position(id={self.id}, symbol={self.symbol}, quantity={self.quantity}, stop_loss_price={self.stop_loss_price}, take_profit_price={self.take_profit_price})>"

