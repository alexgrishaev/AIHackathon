"""
Script to run Alembic migrations on application startup.
This script is designed to be run before starting the application on Render.com.
"""

import os
import sys
import subprocess
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


def run_migrations():
    """Run database migrations using Alembic."""
    try:
        # First check if migrations directory exists, if not, set it up
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
                logger.error(f"Failed to create initial migration: {result.stderr}")
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
            logger.error(f"Migration failed: {result.stderr}")
            raise RuntimeError(f"Migration failed: {result.stderr}")
        
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
