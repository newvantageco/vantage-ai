#!/usr/bin/env python3
"""
Database wait and migration entrypoint for VANTAGE AI
Waits for database to be ready, then runs Alembic migrations
"""

import os
import sys
import time
import logging
from urllib.parse import urlparse
import psycopg
from alembic.config import Config
from alembic import command

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def wait_for_database(database_url: str, max_retries: int = 30, retry_delay: int = 2) -> bool:
    """Wait for database to be ready"""
    logger.info("Waiting for database to be ready...")
    
    parsed_url = urlparse(database_url)
    host = parsed_url.hostname
    port = parsed_url.port or 5432
    user = parsed_url.username
    password = parsed_url.password
    database = parsed_url.path[1:]  # Remove leading slash
    
    for attempt in range(max_retries):
        try:
            with psycopg.connect(
                host=host,
                port=port,
                user=user,
                password=password,
                dbname=database,
                connect_timeout=5
            ) as conn:
                with conn.cursor() as cur:
                    cur.execute("SELECT 1")
                    result = cur.fetchone()
                    if result:
                        logger.info("Database is ready!")
                        return True
        except Exception as e:
            logger.warning(f"Database not ready (attempt {attempt + 1}/{max_retries}): {e}")
            if attempt < max_retries - 1:
                time.sleep(retry_delay)
    
    logger.error("Database failed to become ready after maximum retries")
    return False

def run_migrations() -> bool:
    """Run Alembic migrations"""
    logger.info("Running database migrations...")
    
    try:
        # Get database URL from environment
        database_url = os.getenv("DATABASE_URL", "postgresql+psycopg://dev:dev@localhost:5432/vantage")
        logger.info(f"Using database URL: {database_url}")
        
        # Configure Alembic
        alembic_cfg = Config("alembic.ini")
        alembic_cfg.set_main_option("sqlalchemy.url", database_url)
        
        # Run migrations
        command.upgrade(alembic_cfg, "head")
        logger.info("Database migrations completed successfully!")
        return True
        
    except Exception as e:
        logger.error(f"Migration failed: {e}")
        return False

def main():
    """Main entrypoint"""
    logger.info("Starting VANTAGE AI database setup...")
    
    # Get configuration from environment
    database_url = os.getenv("DATABASE_URL", "postgresql+psycopg://dev:dev@localhost:5432/vantage")
    logger.info(f"Using database URL: {database_url}")
    
    # Wait for database
    if not wait_for_database(database_url):
        logger.error("Failed to connect to database")
        sys.exit(1)
    
    # Run migrations
    if not run_migrations():
        logger.error("Failed to run migrations")
        sys.exit(1)
    
    logger.info("Database setup completed successfully!")
    
    # If this is being called as a pre-start hook, exit successfully
    # If this is the main command, keep running
    if len(sys.argv) > 1 and sys.argv[1] == "wait-only":
        sys.exit(0)

if __name__ == "__main__":
    main()
