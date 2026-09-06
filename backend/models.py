"""
SQLAlchemy ORM models defining the relational database schema.

Tables:
- User: Stores credentials and account timestamps.
- ResearchRequest: Tracks individual research queries and execution status.
- Report: Stores the final generated Markdown report, critic score, and review.
"""

from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from database import Base


class User(Base):
    """Registered user accounts with hashed passwords."""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Deleting a user automatically removes all their research requests and reports
    research_requests = relationship(
        "ResearchRequest",
        back_populates="user",
        cascade="all, delete-orphan"
    )


class ResearchRequest(Base):
    """Tracks the lifecycle of each research job submitted by a user."""
    __tablename__ = "research_requests"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    topic = Column(String(500), nullable=False)
    status = Column(String(20), default="pending")  # States: pending | done | failed
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationship back to the owner and forward to the resulting report
    user = relationship("User", back_populates="research_requests")
    report = relationship(
        "Report",
        back_populates="request",
        uselist=False,
        cascade="all, delete-orphan"
    )


class Report(Base):
    """The synthesized research document and critic evaluation output."""
    __tablename__ = "reports"

    id = Column(Integer, primary_key=True, index=True)
    request_id = Column(Integer, ForeignKey("research_requests.id", ondelete="CASCADE"), nullable=False)
    content = Column(Text, nullable=False)
    critique_feedback = Column(Text, nullable=True)
    critique_score = Column(Integer, nullable=True)  # Numerical score (1-10)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    request = relationship("ResearchRequest", back_populates="report")
