"""
Database setup using SQLAlchemy.

Defines engine, session, and Base for models.
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from .config import get_settings

settings = get_settings()

# SQLite needs check_same_thread False for multi-threaded environments like FastAPI dev
engine = create_engine(
    settings.DATABASE_URL,
    connect_args={"check_same_thread": False} if settings.DATABASE_URL.startswith("sqlite") else {},
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    """SQLAlchemy Base class for models."""
    pass


# PUBLIC_INTERFACE
def get_db():
    """Yield a database session and ensure proper cleanup."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
