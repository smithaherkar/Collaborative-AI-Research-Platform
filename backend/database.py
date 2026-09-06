"""
Database configuration and session management using SQLAlchemy.

Supports PostgreSQL for production and falls back to a local SQLite database
for seamless local development and testing.
"""

import os
from pathlib import Path
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

# Load environment variables from the project root .env if present
env_root = Path(__file__).resolve().parent.parent / ".env"
if env_root.exists():
    load_dotenv(dotenv_path=env_root)
else:
    load_dotenv()

# Use DATABASE_URL from environment; default to SQLite for quick local runs
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL or not DATABASE_URL.strip():
    DATABASE_URL = "sqlite:///./research.db"

# SQLite requires 'check_same_thread: False' to allow FastAPI's multithreaded workers
connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}

# Initialize SQLAlchemy engine with connection health checks
engine = create_engine(
    DATABASE_URL,
    connect_args=connect_args,
    pool_pre_ping=True
)

# Factory for creating new database sessions per request
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for all ORM models
Base = declarative_base()


def get_db():
    """
    FastAPI dependency yielding a database session per request.
    Ensures the session is cleanly closed once the response is sent.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
