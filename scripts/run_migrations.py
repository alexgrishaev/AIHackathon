"""
Script to run Alembic migrations on application startup.
This script is designed to be run before starting the application on Render.com.
"""

import os
import sys
import subprocess
import time
from pathlib import Path
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("db_migrations")

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


def test_db_connection():
    """Test if database is accessible."""
    try:
        from sqlalchemy import create_engine, text
        from app.database.connection import DATABASE_URL
        
        logger.info(f"Testing connection to database...")
        engine = create_engine(DATABASE_URL)
        with engine.connect() as connection:
            result = connection.execute(text("SELECT 1"))
            logger.info("Database connection successful!")
        return True
    except Exception as e:
        logger.error(f"Database connection test failed: {str(e)}")
        return False


def run_migrations(max_retries=5, retry_delay=5):
    """Run database migrations using Alembic."""
    # First test database connection with retries
    connected = False
    for attempt in range(max_retries):
        if test_db_connection():
            connected = True
            break
        logger.warning(f"Database not available yet. Retry {attempt+1}/{max_retries}...")
        time.sleep(retry_delay)
    
    if not connected:
        logger.error("Could not connect to database after multiple attempts")
        return False
        
    try:
        # Check if migrations directory exists, if not, set it up
        migrations_dir = project_root / "migrations"
        if not migrations_dir.exists():
            logger.info("Migrations directory not found. Setting up Alembic...")
            
            # Import and run the setup script
            from scripts.setup_alembic import setup_alembic
            setup_alembic()
            
            logger.info("Alembic setup complete. Creating initial migration...")
            
            # Create initial migration
            result = subprocess.run(
                ["alembic", "revision", "--autogenerate", "-m", "Initial database creation"],
                cwd=str(project_root),
                capture_output=True,
                text=True
            )
            
            if result.returncode != 0:
                logger.error(f"Failed to create initial migration:")
                logger.error(f"STDOUT: {result.stdout}")
                logger.error(f"STDERR: {result.stderr}")
                raise RuntimeError("Failed to create initial migration")
            
            logger.info("Initial migration created successfully")
        
        # Run migrations
        logger.info("Running database migrations...")
        result = subprocess.run(
            ["alembic", "upgrade", "head"],
            cwd=str(project_root),
            capture_output=True,
            text=True
        )
        
        if result.returncode != 0:
            logger.error(f"Migration failed:")
            logger.error(f"STDOUT: {result.stdout}")
            logger.error(f"STDERR: {result.stderr}")
            raise RuntimeError("Migration failed")
        
        logger.info("Database migrations completed successfully")
        return True
        
    except Exception as e:
        logger.error(f"Error running migrations: {str(e)}")
        return False


if __name__ == "__main__":
    success = run_migrations()
    if not success:
        logger.error("Migration process failed. Exiting...")
        sys.exit(1)
    
    logger.info("Migration process completed successfully")
