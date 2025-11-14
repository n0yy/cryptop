from sqlalchemy import Column, BigInteger, String, Text, TIMESTAMP, JSON, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.models import Base


class CustomIndicator(Base):
    __tablename__ = "custom_indicators"
    
    id = Column(BigInteger, primary_key=True, index=True)
    user_id = Column(BigInteger, ForeignKey("users.id"), nullable=False, index=True)
    name = Column(String(100), nullable=False)
    formula = Column(Text, nullable=False)
    description = Column(Text, nullable=True)
    parameters = Column(JSON, default={})
    status = Column(String(20), default="ACTIVE")
    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())
    
    user = relationship("User", backref="custom_indicators")
    
    def __repr__(self):
        return f"<CustomIndicator(id={self.id}, name={self.name})>"
