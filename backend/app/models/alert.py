from sqlalchemy import Column, BigInteger, String, DECIMAL, TIMESTAMP, ARRAY, ForeignKey, JSON
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.models import Base


class Alert(Base):
    __tablename__ = "alerts"
    
    id = Column(BigInteger, primary_key=True, index=True)
    user_id = Column(BigInteger, ForeignKey("users.id"), nullable=False, index=True)
    symbol = Column(String(20), nullable=False, index=True)
    condition = Column(String(50), nullable=False)
    threshold = Column(DECIMAL(20, 8), nullable=False)
    status = Column(String(20), default="ACTIVE", index=True)
    channels = Column(ARRAY(String), default=[])
    metadata = Column(JSON, default={})
    triggered_at = Column(TIMESTAMP, nullable=True)
    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())
    
    user = relationship("User", backref="alerts")
    
    def __repr__(self):
        return f"<Alert(id={self.id}, symbol={self.symbol}, condition={self.condition})>"
