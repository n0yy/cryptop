from sqlalchemy import Column, BigInteger, String, Text, TIMESTAMP, JSON, ARRAY, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.models import Base


class Report(Base):
    __tablename__ = "reports"
    
    id = Column(BigInteger, primary_key=True, index=True)
    user_id = Column(BigInteger, ForeignKey("users.id"), nullable=False, index=True)
    report_type = Column(String(50), nullable=False)
    symbols = Column(ARRAY(String), default=[])
    content = Column(JSON, default={})
    file_url = Column(Text, nullable=True)
    generated_at = Column(TIMESTAMP, server_default=func.now())
    
    user = relationship("User", backref="reports")
    
    def __repr__(self):
        return f"<Report(id={self.id}, type={self.report_type})>"
