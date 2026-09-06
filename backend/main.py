"""
FastAPI REST API for the Collaborative AI Research Platform.

Handles user authentication, background database operations,
multi-agent pipeline invocation, and report retrieval.
"""

import re
from typing import List, Optional

from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from database import Base, engine, get_db
from models import User, ResearchRequest, Report
from schemas import (
    UserCreate,
    UserResponse,
    LoginRequest,
    Token,
    ResearchCreate,
    ReportResponse,
    ResearchRequestResponse,
)
from auth import (
    get_current_user,
    hash_password,
    verify_password,
    create_access_token,
)
from pipeline import run_research_pipeline

# Ensure all database tables exist on application startup
Base.metadata.create_all(bind=engine)

# Initialize FastAPI application
app = FastAPI(
    title="Collaborative AI Research Platform API",
    description="Decoupled REST API for multi-agent autonomous research and report synthesis.",
    version="1.0.0",
)

# Enable CORS to allow the frontend client to communicate with the API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def extract_critic_score(feedback: Optional[str]) -> Optional[int]:
    """
    Parses the numerical score out of the critic feedback (e.g., 'Score: 8/10' -> 8).
    Returns None if the score pattern is not found.
    """
    if not feedback:
        return None
    match = re.search(r"Score:\s*(\d+)", feedback, re.IGNORECASE)
    if match:
        try:
            return int(match.group(1))
        except ValueError:
            return None
    return None


# ---------------------------------------------------------------------------
# Health & Status Endpoint
# ---------------------------------------------------------------------------
@app.get("/", tags=["Health"])
def health_check():
    """Returns the operational status of the API."""
    return {
        "status": "ok",
        "message": "Collaborative AI Research Platform API is running",
    }


# ---------------------------------------------------------------------------
# Authentication Endpoints
# ---------------------------------------------------------------------------
@app.post("/signup", response_model=UserResponse, status_code=status.HTTP_201_CREATED, tags=["Auth"])
def signup(user_in: UserCreate, db: Session = Depends(get_db)):
    """
    Registers a new user account.
    Checks for email uniqueness and hashes the password before persisting.
    """
    existing_user = db.query(User).filter(User.email == user_in.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="An account with this email address already exists.",
        )

    new_user = User(
        email=user_in.email,
        hashed_password=hash_password(user_in.password),
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


@app.post("/login", response_model=Token, tags=["Auth"])
def login(credentials: LoginRequest, db: Session = Depends(get_db)):
    """
    Authenticates user credentials and issues a signed JWT Bearer access token.
    """
    user = db.query(User).filter(User.email == credentials.email).first()
    if not user or not verify_password(credentials.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = create_access_token(data={"sub": user.email})
    return {"access_token": access_token, "token_type": "bearer"}


# ---------------------------------------------------------------------------
# Research & Reports Endpoints
# ---------------------------------------------------------------------------
@app.post("/research", response_model=ReportResponse, tags=["Research"])
def execute_research(
    payload: ResearchCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Runs the full multi-agent research pipeline for the requested topic.
    Persists the request lifecycle and resulting report in the database.
    """
    # 1. Record the initial research request in 'pending' status
    research_req = ResearchRequest(
        user_id=current_user.id,
        topic=payload.topic,
        status="pending",
    )
    db.add(research_req)
    db.commit()
    db.refresh(research_req)

    # 2. Invoke the 4-stage agent pipeline
    try:
        results = run_research_pipeline(payload.topic)
        report_content = results.get("report", "")
        critic_feedback = results.get("feedback", "")
        score = extract_critic_score(critic_feedback)

        # 3. Save the generated report and critique evaluation
        report = Report(
            request_id=research_req.id,
            content=report_content,
            critique_feedback=critic_feedback,
            critique_score=score,
        )
        db.add(report)

        # 4. Mark the request as completed and commit transaction
        research_req.status = "done"
        db.commit()
        db.refresh(report)
        return report

    except Exception as e:
        # If external API or synthesis fails, update status and rollback cleanly
        db.rollback()
        research_req.status = "failed"
        db.commit()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Research pipeline execution failed: {str(e)}",
        )


@app.get("/reports/{report_id}", response_model=ReportResponse, tags=["Reports"])
def get_report(
    report_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Fetches a specific research report by ID.
    Enforces ownership isolation so users can only view their own reports.
    """
    report = db.query(Report).filter(Report.id == report_id).first()
    if not report:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Report not found.",
        )

    # Ownership verification
    if report.request.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Report not found.",
        )

    return report


@app.get("/my-reports", response_model=List[ResearchRequestResponse], tags=["Reports"])
def list_my_reports(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Retrieves the complete history of research requests and reports for the logged-in user.
    """
    requests = (
        db.query(ResearchRequest)
        .filter(ResearchRequest.user_id == current_user.id)
        .order_by(ResearchRequest.created_at.desc())
        .all()
    )
    return requests
