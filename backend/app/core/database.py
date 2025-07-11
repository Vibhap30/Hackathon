"""
Database Configuration and Connection Management
PowerShare Energy Trading Platform
"""


from sqlalchemy.ext.declarative import declarative_base
from databases import Database
import logging

from app.core.config import settings


logger = logging.getLogger(__name__)

# [PROTOTYPE MODE]
# Define SQLAlchemy Base for model compatibility only (not used for DB operations in prototype)
Base = declarative_base()


# [PROTOTYPE MODE]
# SQLAlchemy engine/session/database setup is disabled for the prototype.
# Use local file-based storage (e.g., JSON/CSV) and dummy data for all data access.
# Example: load data from 'synthetic_datasets/user_profiles.csv' or similar files.
# For PostgreSQL, use asyncpg
database = Database(settings.DATABASE_URL)

# [PROTOTYPE MODE]
# The following database session functions are disabled for the prototype.
# Use dummy data and file-based storage for all data access.
def get_db():
    """
    [PROTOTYPE MODE]
    This function is disabled. For the prototype, use dummy data and file-based storage.
    """
    pass



# [PROTOTYPE MODE]
# Table creation is disabled for the prototype.
# Use local files for data persistence.
async def create_tables():
    """
    [PROTOTYPE MODE]
    Table creation is disabled. For the prototype, use local files for data persistence.
    """
    pass


async def close_database():
    """Close database connection"""
    try:
        await database.disconnect()
        logger.info("Database connection closed")
    except Exception as e:
        logger.error(f"Error closing database connection: {e}")


# Database health check
async def check_database_health() -> bool:
    """Check if database is healthy"""
    try:
        await database.execute("SELECT 1")
        return True
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        return False
