from pydantic import BaseModel, ConfigDict
from typing import List, Optional, Any
from datetime import datetime

# --- Child Schemas (for nesting in other schemas) ---
class Detection(BaseModel):
    detected_class: str
    confidence_score: float
    model_config = ConfigDict(from_attributes=True)

class Review(BaseModel):
    rating: int
    comment: Optional[str] = None
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)
    
# --- Main Data Schemas ---
class Report(BaseModel):
    id: int
    latitude: float
    longitude: float
    address_text: str
    image_filename: str
    status: str
    zone: Optional[str] = None
    submitted_at: datetime
    timeline: Optional[List[Any]] = []
    rejection_reason: Optional[str] = None
    detections: List[Detection] = []
    reviews: List[Review] = []
    model_config = ConfigDict(from_attributes=True)
    
class ReviewCreate(BaseModel):
    rating: int
    comment: Optional[str] = None

# --- Analytics Schemas ---
class AnalyticsData(BaseModel):
    total: int
    pending: int
    in_progress: int
    pending_verification: int
    resolved: int
    by_type: dict

class McdPerformanceReport(BaseModel):
    total_marked_resolved: int
    approved_count: int
    rejected_count: int
    approval_rate_percent: float
    rejection_details: List[dict]

# --- User & Token Schemas ---
class UserCreate(BaseModel):
    email: str
    full_name: str
    password: str
    user_type: str = "citizen"

class User(BaseModel):
    id: int
    email: str
    full_name: str
    user_type: str
    is_active: bool
    model_config = ConfigDict(from_attributes=True)
    
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: Optional[str] = None