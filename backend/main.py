from fastapi import FastAPI, Depends, HTTPException, status, File, UploadFile, Form
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func
from jose import JWTError, jwt
from typing import List, Optional
import uuid
import os
from pydantic import BaseModel
from fastapi.staticfiles import StaticFiles
from datetime import datetime
from contextlib import asynccontextmanager

from . import models, schemas, security, inference
from .database import SessionLocal, engine

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Application starting up...")
    models.Base.metadata.create_all(bind=engine)
    print("Database tables checked/created.")
    yield
    print("Application shutting down...")

app = FastAPI(title="CivicReporter API", lifespan=lifespan)
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Dependencies ---
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_user(db: Session, email: str):
    return db.query(models.User).filter(models.User.email == email).first()

async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not validate credentials", headers={"WWW-Authenticate": "Bearer"})
    try:
        payload = jwt.decode(token, security.SECRET_KEY, algorithms=[security.ALGORITHM])
        email: str = payload.get("sub")
        if email is None: raise credentials_exception
        token_data = schemas.TokenData(email=email)
    except JWTError:
        raise credentials_exception
    user = get_user(db, email=token_data.email)
    if user is None: raise credentials_exception
    return user

async def get_current_active_user(current_user: schemas.User = Depends(get_current_user)):
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user

# --- Authentication Routes ---
@app.post("/register", response_model=schemas.User, tags=["Authentication"])
def register_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = get_user(db, email=user.email)
    if db_user: raise HTTPException(status_code=400, detail="Email already registered")
    hashed_password = security.get_password_hash(user.password)
    db_user = models.User(email=user.email, full_name=user.full_name, hashed_password=hashed_password, user_type=user.user_type, is_active=True)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

@app.post("/token", response_model=schemas.Token, tags=["Authentication"])
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = get_user(db, email=form_data.username)
    if not user or not security.verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect email or password", headers={"WWW-Authenticate": "Bearer"})
    if not user.is_active: raise HTTPException(status_code=400, detail="User not verified")
    access_token = security.create_access_token(data={"sub": user.email})
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/users/me", response_model=schemas.User, tags=["Authentication"])
async def read_users_me(current_user: schemas.User = Depends(get_current_active_user)):
    return current_user

# --- Public Route ---
class PublicDashboardData(BaseModel):
    analytics: schemas.AnalyticsData
    reports: List[schemas.Report]

@app.get("/api/public-dashboard", response_model=PublicDashboardData, tags=["Public"])
def get_public_dashboard_data(db: Session = Depends(get_db)):
    total = db.query(models.Report).count()
    pending = db.query(models.Report).filter(models.Report.status == "pending").count()
    in_progress = db.query(models.Report).filter(models.Report.status == "in_progress").count()
    pending_verification = db.query(models.Report).filter(models.Report.status == "pending_verification").count()
    resolved = db.query(models.Report).filter(models.Report.status == "resolved").count()
    detections = db.query(models.Detection.detected_class, func.count(models.Detection.id)).group_by(models.Detection.detected_class).all()
    by_type = {d[0]: d[1] for d in detections}
    analytics_data = { "total": total, "pending": pending, "in_progress": in_progress, "pending_verification": pending_verification, "resolved": resolved, "by_type": by_type }
    reports_for_map = db.query(models.Report).options(joinedload(models.Report.detections)).order_by(models.Report.submitted_at.desc()).limit(100).all()
    return {"analytics": analytics_data, "reports": reports_for_map}

# --- Reporting Routes ---
@app.post("/api/report", tags=["Reports"])
async def create_report(
    latitude: float = Form(...),
    longitude: float = Form(...),
    address: str = Form(...),
    image: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(get_current_active_user)
):
    uploads_dir = "uploads"; os.makedirs(uploads_dir, exist_ok=True)
    file_extension = os.path.splitext(image.filename)[1]
    unique_filename = f"{uuid.uuid4()}{file_extension}"
    file_path = os.path.join(uploads_dir, unique_filename)
    with open(file_path, "wb") as buffer: buffer.write(await image.read())
    detections = inference.analyze_image(file_path)
    if not detections: raise HTTPException(status_code=404, detail="AI models did not detect any issues.")

    bhopal_zones = ["Zone A", "Zone B", "Zone C", "Zone D"]
    report_zone = bhopal_zones[hash(unique_filename) % len(bhopal_zones)]
    initial_timeline_entry = [{"status": "pending", "timestamp": datetime.utcnow().isoformat(), "actor": "Citizen"}]
    new_report = models.Report(
        latitude=latitude, longitude=longitude, address_text=address,
        image_filename=unique_filename, submitter_id=current_user.id, zone=report_zone,
        timeline=initial_timeline_entry
    )
    db.add(new_report); db.commit(); db.refresh(new_report)
    for detection in detections:
        db.add(models.Detection(report_id=new_report.id, detected_class=detection["class"], confidence_score=detection["confidence"]))
    db.commit()
    return {"report_id": new_report.id, "detections": detections}

@app.get("/api/reports/my-reports", response_model=List[schemas.Report], tags=["Reports"])
async def get_my_reports(db: Session = Depends(get_db), current_user: schemas.User = Depends(get_current_active_user)):
    return db.query(models.Report).options(joinedload(models.Report.reviews)).filter(models.Report.submitter_id == current_user.id).order_by(models.Report.submitted_at.desc()).all()

@app.post("/api/reports/{report_id}/review", response_model=schemas.Review, tags=["Reports"])
def create_review(report_id: int, review: schemas.ReviewCreate, db: Session = Depends(get_db), current_user: schemas.User = Depends(get_current_active_user)):
    db_report = db.query(models.Report).filter(models.Report.id == report_id).first()
    if not db_report or db_report.submitter_id != current_user.id or db_report.status != "resolved":
        raise HTTPException(status_code=403, detail="Not allowed to review this report.")
    new_review = models.Review(**review.model_dump(), report_id=report_id, user_id=current_user.id)
    db.add(new_review); db.commit(); db.refresh(new_review)
    return new_review

# --- Official Routes ---
@app.get("/api/reports", response_model=List[schemas.Report], tags=["Official"])
async def get_all_reports(status: Optional[str] = None, zone: Optional[str] = None, issue_type: Optional[str] = None, db: Session = Depends(get_db), current_user: schemas.User = Depends(get_current_active_user)):
    if current_user.user_type not in ["municipal_official", "inspection_officer"]:
        raise HTTPException(status_code=403, detail="Not authorized")
    query = db.query(models.Report).options(joinedload(models.Report.detections), joinedload(models.Report.reviews))
    if status: query = query.filter(models.Report.status == status)
    if zone: query = query.filter(models.Report.zone == zone)
    if issue_type: query = query.join(models.Detection).filter(models.Detection.detected_class.ilike(f"%{issue_type}%"))
    return query.order_by(models.Report.submitted_at.desc()).all()

class ReportStatusUpdate(BaseModel): status: str
@app.patch("/api/reports/{report_id}/status", response_model=schemas.Report, tags=["Official"])
def update_report_status(report_id: int, status_update: ReportStatusUpdate, db: Session = Depends(get_db), current_user: schemas.User = Depends(get_current_active_user)):
    if current_user.user_type != "municipal_official": raise HTTPException(status_code=403, detail="Only municipal officials can update status")
    db_report = db.query(models.Report).filter(models.Report.id == report_id).first()
    if not db_report: raise HTTPException(status_code=404, detail="Report not found")
    valid_statuses = ["in_progress", "pending_verification"]
    if status_update.status in valid_statuses:
        db_report.status = status_update.status
        if status_update.status == "pending_verification": db_report.resolved_by_mcd_id = current_user.id
        timeline = (db_report.timeline or []) + [{"status": db_report.status, "timestamp": datetime.utcnow().isoformat(), "actor": f"MCD Official ({current_user.full_name})"}]
        db_report.timeline = timeline
        db.commit(); db.refresh(db_report)
        return db_report
    else:
        raise HTTPException(status_code=400, detail=f"Invalid status. Must be one of: {valid_statuses}")

class VerificationRequest(BaseModel): approve: bool; reason: Optional[str] = None
@app.post("/api/reports/{report_id}/verify", response_model=schemas.Report, tags=["Official"])
def verify_resolution(report_id: int, verification: VerificationRequest, db: Session = Depends(get_db), current_user: schemas.User = Depends(get_current_active_user)):
    if current_user.user_type != "inspection_officer": raise HTTPException(status_code=403, detail="Only inspection officers can verify reports")
    db_report = db.query(models.Report).filter(models.Report.id == report_id).first()
    if not db_report or db_report.status != "pending_verification": raise HTTPException(status_code=404, detail="Report not found or not pending verification")
    db_report.verified_by_io_id = current_user.id
    status_text = ""
    if verification.approve:
        db_report.status = "resolved"; db_report.rejection_reason = None; status_text = "Approved"
    else:
        db_report.status = "in_progress"; status_text = "Rejected"
        if not verification.reason: raise HTTPException(status_code=400, detail="A reason is required for rejection.")
        db_report.rejection_reason = verification.reason
    timeline = (db_report.timeline or []) + [{"status": status_text, "timestamp": datetime.utcnow().isoformat(), "actor": f"Inspector ({current_user.full_name})", "reason": db_report.rejection_reason}]
    db_report.timeline = timeline
    db.commit(); db.refresh(db_report)
    return db_report

@app.get("/api/mcd-performance", response_model=schemas.McdPerformanceReport, tags=["Analytics"])
def get_mcd_performance(db: Session = Depends(get_db), current_user: schemas.User = Depends(get_current_active_user)):
    if "supervisor" not in current_user.email: raise HTTPException(status_code=403, detail="Not authorized")
    verified_reports = db.query(models.Report).filter(models.Report.verified_by_io_id != None).options(joinedload(models.Report.detections)).all()
    approved_count = sum(1 for r in verified_reports if r.status == "resolved")
    rejected_count = len(verified_reports) - approved_count
    total_verified = len(verified_reports)
    rejection_details = [
        {"report_id": r.id, "reason": r.rejection_reason, "address": r.address_text,
         "mcd_id": r.resolved_by_mcd_id, "io_id": r.verified_by_io_id}
        for r in verified_reports if r.status != "resolved"
    ]
    return {
        "total_marked_resolved": total_verified, "approved_count": approved_count, "rejected_count": rejected_count,
        "approval_rate_percent": (approved_count / total_verified * 100) if total_verified > 0 else 100,
        "rejection_details": rejection_details
    }