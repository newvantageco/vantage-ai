from __future__ import annotations

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.config import get_settings


settings = get_settings()

engine = create_engine(
    settings.database_url, 
    pool_pre_ping=True, 
    future=True,
    pool_size=20,  # Number of connections to maintain in the pool
    max_overflow=30,  # Additional connections that can be created on demand
    pool_recycle=3600,  # Recycle connections after 1 hour
    pool_timeout=30,  # Timeout for getting connection from pool
    echo=False  # Set to True for SQL query logging in development
)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)


def get_db():
	db = SessionLocal()
	try:
		yield db
	finally:
		db.close()



