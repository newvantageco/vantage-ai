from fastapi import APIRouter
from app.db.session import engine
from sqlalchemy import text


router = APIRouter()


@router.get("/health")
async def health_check() -> dict:
    """Health check endpoint with database status."""
    try:
        # Test database connection
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        return {
            "status": "ok",
            "database": "connected",
            "api": "running",
            "version": "1.0.0"
        }
    except Exception as e:
        return {
            "status": "error",
            "database": "disconnected",
            "api": "running",
            "error": str(e),
            "version": "1.0.0"
        }


