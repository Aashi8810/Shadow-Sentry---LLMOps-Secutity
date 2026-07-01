from sqlalchemy import Column, Integer, String, Boolean, DateTime, JSON
from sqlalchemy.sql import func
from app.db.database import Base

class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
    user_id = Column(String, index=True)
    endpoint = Column(String)
    prompt = Column(String)
    response = Column(String)
    
    # Security tracking
    risk_score = Column(Integer)
    risk_level = Column(String)
    blocked = Column(Boolean, default=False)
    detection_reasons = Column(JSON)  # Stores the list of triggered rules