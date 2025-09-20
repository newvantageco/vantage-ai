from __future__ import annotations

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.config import get_settings


settings = get_settings()

engine = create_engine(
    settings.database_url, 
    pool_pre_ping=True, 
    future=True,
    pool_size=10,  # Reduced pool size to prevent connection exhaustion
    max_overflow=15,  # Reduced overflow to prevent resource exhaustion
    pool_recycle=1800,  # Recycle connections after 30 minutes (more frequent)
    pool_timeout=10,  # Reduced timeout to fail fast on connection issues
    echo=False  # Set to True for SQL query logging in development
)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)


def get_db():
	db = SessionLocal()
	try:
		yield db
	finally:
		db.close()



