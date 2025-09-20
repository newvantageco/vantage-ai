"""
Database Connection Pooling for VANTAGE AI
Optimizes database connections for better performance
"""

from sqlalchemy import create_engine
from sqlalchemy.pool import QueuePool, StaticPool
from sqlalchemy.engine import Engine
from typing import Optional
import logging

logger = logging.getLogger(__name__)

class DatabasePool:
    """Manages database connection pooling for optimal performance."""
    
    def __init__(self, database_url: str, pool_size: int = 20, max_overflow: int = 30):
        """
        Initialize database connection pool.
        
        Args:
            database_url: Database connection URL
            pool_size: Number of connections to maintain in the pool
            max_overflow: Maximum number of connections to create beyond pool_size
        """
        self.database_url = database_url
        self.pool_size = pool_size
        self.max_overflow = max_overflow
        self.engine: Optional[Engine] = None
    
    def create_engine(self) -> Engine:
        """Create optimized database engine with connection pooling."""
        if self.engine is None:
            self.engine = create_engine(
                self.database_url,
                poolclass=QueuePool,
                pool_size=self.pool_size,
                max_overflow=self.max_overflow,
                pool_pre_ping=True,  # Verify connections before use
                pool_recycle=3600,   # Recycle connections every hour
                pool_timeout=30,     # Timeout for getting connection from pool
                echo=False,          # Set to True for SQL debugging
                connect_args={
                    "connect_timeout": 10,
                    "application_name": "vantage_ai"
                }
            )
            
            logger.info(f"Database engine created with pool_size={self.pool_size}, max_overflow={self.max_overflow}")
        
        return self.engine
    
    def get_connection_info(self) -> dict:
        """Get information about the connection pool."""
        if self.engine is None:
            return {"status": "not_initialized"}
        
        pool = self.engine.pool
        return {
            "pool_size": pool.size(),
            "checked_in": pool.checkedin(),
            "checked_out": pool.checkedout(),
            "overflow": pool.overflow(),
            "invalid": pool.invalid()
        }
    
    def close(self):
        """Close all connections in the pool."""
        if self.engine:
            self.engine.dispose()
            logger.info("Database connection pool closed")

# Global database pool instance
db_pool: Optional[DatabasePool] = None

def get_db_pool() -> DatabasePool:
    """Get the global database pool instance."""
    global db_pool
    if db_pool is None:
        from app.core.config import get_settings
        settings = get_settings()
        db_pool = DatabasePool(settings.database_url)
    return db_pool

def get_engine() -> Engine:
    """Get the database engine from the pool."""
    return get_db_pool().create_engine()
