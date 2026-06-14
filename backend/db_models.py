"""
SQLAlchemy database models (tables).
Separate from Pydantic schemas which handle request/response structures.
"""
from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship

from database import Base

class Prediction(Base):
    __tablename__ = "predictions"

    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    brand = Column(String, nullable=False)
    year = Column(Integer, nullable=False)
    km_driven = Column(Integer, nullable=False)
    fuel = Column(String, nullable=False)
    seller_type = Column(String, nullable=False)
    transmission = Column(String, nullable=False)
    owner = Column(String, nullable=False)
    
    predicted_price = Column(Float, nullable=False)
    model_used = Column(String, nullable=False)
    model_r2_score = Column(Float, nullable=False)
    
    device_type = Column(String, nullable=True)  # "web", "mobile", "tablet", etc.
    
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    feedback = relationship("Feedback", back_populates="prediction", cascade="all, delete-orphan")


class Feedback(Base):
    __tablename__ = "feedback"

    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    prediction_id = Column(Integer, ForeignKey("predictions.id"), nullable=False, index=True)
    
    actual_price = Column(Float, nullable=True)
    rating = Column(Integer, nullable=True)  # 1-5 stars
    comment = Column(String, nullable=True)
    
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    prediction = relationship("Prediction", back_populates="feedback")
