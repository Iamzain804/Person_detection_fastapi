from sqlalchemy import Column, Integer, Float, DateTime
from datetime import datetime
from ..core.database import Base

class DetectionRecord(Base):
    __tablename__ = "detections"

    id = Column(Integer, primary_key=True, index=True)
    person_count = Column(Integer)
    max_confidence = Column(Float)
    timestamp = Column(DateTime, default=datetime.utcnow)
