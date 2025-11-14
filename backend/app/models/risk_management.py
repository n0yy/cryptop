from sqlalchemy import Column, BigInteger, String, Float, TIMESTAMP, ForeignKey, Enum
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from enum import Enum as PyEnum
from app.models import Base


class OrderType(PyEnum):
    STOP_LOSS = "STOP_LOSS"
    TAKE_PROFIT = "TAKE_PROFIT"


class OrderStatus(PyEnum):
    PENDING = "PENDING"
    ACTIVE = "ACTIVE"
    TRIGGERED = "TRIGGERED"
    CANCELLED = "CANCELLED"


class StopLossTakeProfitOrder(Base):
    __tablename__ = "stop_loss_take_profit_orders"
    
    id = Column(BigInteger, primary_key=True, index=True)
    portfolio_id = Column(BigInteger, ForeignKey("portfolios.id"), nullable=False, index=True)
    symbol = Column(String(20), nullable=False, index=True)
    order_type = Column(Enum(OrderType), nullable=False)
    trigger_price = Column(Float, nullable=False)
    quantity = Column(Float, nullable=False)
    leverage = Column(Float, nullable=True)
    status = Column(Enum(OrderStatus), nullable=False, default=OrderStatus.PENDING)
    created_at = Column(TIMESTAMP, server_default=func.now())
    triggered_at = Column(TIMESTAMP, nullable=True)
    executed_price = Column(Float, nullable=True)
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())
    
    portfolio = relationship("Portfolio", backref="stop_loss_take_profit_orders")
    
    def __repr__(self):
        return f"<StopLossTakeProfitOrder(id={self.id}, symbol={self.symbol}, type={self.order_type.value})>"
