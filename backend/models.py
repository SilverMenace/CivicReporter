from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Boolean, Text, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
from .database import Base

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    full_name = Column(String(255), nullable=False)
    hashed_password = Column(String(255), nullable=False)
    user_type = Column(String(50), default="citizen") # 'citizen', 'municipal_official', 'inspection_officer'
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

class Report(Base):
    __tablename__ = "reports"
    id = Column(Integer, primary_key=True, index=True)
    submitter_id = Column(Integer, ForeignKey("users.id"))
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    address_text = Column(String(512))
    image_filename = Column(String(255), unique=True)
    status = Column(String(50), default="pending", index=True) 
    zone = Column(String(100), index=True) 
    submitted_at = Column(DateTime, default=datetime.utcnow)
    
    # New columns for advanced tracking
    timeline = Column(JSON, default=[]) 
    rejection_reason = Column(Text, nullable=True)
    resolved_by_mcd_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    verified_by_io_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    
    detections = relationship("Detection", back_populates="report")
    reviews = relationship("Review", back_populates="report")

class Detection(Base):
    __tablename__ = "detections"
    id = Column(Integer, primary_key=True, index=True)
    report_id = Column(Integer, ForeignKey("reports.id"))
    detected_class = Column(String(100), index=True)
    confidence_score = Column(Float)
    report = relationship("Report", back_populates="detections")

class Review(Base):
    __tablename__ = "reviews"
    id = Column(Integer, primary_key=True, index=True)
    report_id = Column(Integer, ForeignKey("reports.id"))
    user_id = Column(Integer, ForeignKey("users.id"))
    rating = Column(Integer)
    comment = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    report = relationship("Report", back_populates="reviews")