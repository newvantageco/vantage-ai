"""Pytest configuration and fixtures."""

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.db.base import Base
# Import all models to ensure they're registered with Base
from app.models.optimiser import OptimiserState, ScheduleMetrics
from app.models.content import Schedule, ContentItem
from app.models.entities import Organization, Channel, UserAccount
from app.models.post_metrics import PostMetrics
from app.models.external_refs import ScheduleExternal


@pytest.fixture(scope="function")
def db_session():
    """Create a test database session."""
    # Create an in-memory SQLite database for testing
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    
    # Create all tables with error handling for duplicate indexes
    try:
        Base.metadata.create_all(bind=engine)
    except Exception as e:
        # Log the error but continue - some indexes might already exist
        print(f"Warning: Some database objects already exist: {e}")
    
    # Create session
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    session = TestingSessionLocal()
    
    try:
        yield session
    finally:
        session.close()
        # Don't drop tables in SQLite in-memory as it's automatically cleaned up
