"""
Pydantic schemas for request validation and response formatting.
"""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr, Field, ConfigDict


# ---------------------------------------------------------------------------
# User Authentication Schemas
# ---------------------------------------------------------------------------
class UserCreate(BaseModel):
    """Payload for user registration."""
    email: EmailStr
    password: str = Field(..., min_length=6, description="Minimum 6 characters for security")


class UserResponse(BaseModel):
    """Safe user profile representation (excluding password hash)."""
    id: int
    email: str
    created_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class LoginRequest(BaseModel):
    """Credentials required for logging in."""
    email: EmailStr
    password: str


class Token(BaseModel):
    """JWT response model returned after successful authentication."""
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    """Decoded JWT claims payload."""
    email: Optional[str] = None


# ---------------------------------------------------------------------------
# Research & Report Schemas
# ---------------------------------------------------------------------------
class ResearchCreate(BaseModel):
    """Payload to trigger a new multi-agent research run."""
    topic: str = Field(..., min_length=3, max_length=500, description="Topic to investigate")


class ReportResponse(BaseModel):
    """Serialized report details including content and peer review score."""
    id: int
    request_id: int
    content: str
    critique_feedback: Optional[str] = None
    critique_score: Optional[int] = None
    created_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class ResearchRequestResponse(BaseModel):
    """Summary of a research request and its associated report for history listing."""
    id: int
    user_id: int
    topic: str
    status: str
    created_at: Optional[datetime] = None
    report: Optional[ReportResponse] = None

    model_config = ConfigDict(from_attributes=True)
