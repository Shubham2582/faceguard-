"""
FACEGUARD V2 CORE DATA SERVICE - DATABASE CONNECTION
Rule 2: Zero Placeholder Code - Real async database connection
Rule 3: Error-First Development - Proper connection error handling
"""

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.pool import NullPool
from sqlalchemy import text
from contextlib import asynccontextmanager
from typing import AsyncGenerator
import structlog
import asyncio

from config.settings import get_settings

logger = structlog.get_logger(__name__)
settings = get_settings()

# SQLAlchemy Base for ORM models
Base = declarative_base()

# Async engine with connection pooling
engine = create_async_engine(
    settings.database_url,
    echo=False,  # Set to True for SQL debugging
    poolclass=NullPool,  # Disable connection pooling for better error handling
    pool_pre_ping=True,  # Validate connections before use
    pool_recycle=3600,   # Recycle connections after 1 hour
)

# Async session factory
AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=True,
    autocommit=False,
)


class DatabaseManager:
    """Database connection and session management"""
    
    def __init__(self):
        self.engine = engine
        self.session_factory = AsyncSessionLocal
    
    @asynccontextmanager
    async def get_session(self) -> AsyncGenerator[AsyncSession, None]:
        """
        Get database session with automatic cleanup and error handling
        Rule 3: Error-First Development - Proper transaction management
        """
        async with self.session_factory() as session:
            try:
                yield session
                await session.commit()
            except Exception as e:
                await session.rollback()
                await logger.aerror("Database transaction failed", error=str(e))
                raise
            finally:
                await session.close()
    
    async def health_check(self) -> dict:
        """
        Check database connection health
        Rule 3: Error-First Development - Comprehensive health validation
        """
        try:
            start_time = asyncio.get_event_loop().time()
            
            async with self.get_session() as session:
                # Test basic connectivity
                result = await session.execute(text("SELECT 1 as health_check"))
                health_result = result.scalar()
                
                if health_result != 1:
                    raise Exception("Database health check failed - unexpected result")
                
                # Test database existence
                result = await session.execute(text("SELECT current_database()"))
                current_db = result.scalar()
                
                # Test tables accessibility (if they exist)
                try:
                    result = await session.execute(text("SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = 'public'"))
                    table_count = result.scalar()
                except Exception as e:
                    table_count = 0
                    await logger.awarn("Could not count tables", error=str(e))
                
                end_time = asyncio.get_event_loop().time()
                response_time_ms = round((end_time - start_time) * 1000, 2)
                
                return {
                    "status": "healthy",
                    "database": current_db,
                    "response_time_ms": response_time_ms,
                    "tables_count": table_count,
                    "connection_pool": {
                        "status": "active",
                        "engine": str(self.engine.url).replace(settings.database_password, "***")
                    }
                }
                
        except Exception as e:
            await logger.aerror("Database health check failed", error=str(e))
            return {
                "status": "unhealthy", 
                "error": str(e),
                "database_url": str(self.engine.url).replace(settings.database_password, "***")
            }
    
    async def initialize_database(self):
        """
        Initialize database schema and tables
        Rule 2: Zero Placeholder Code - Real schema creation
        """
        try:
            async with engine.begin() as conn:
                await conn.run_sync(Base.metadata.create_all)
            await logger.ainfo("Database schema initialized successfully")
        except Exception as e:
            await logger.aerror("Database initialization failed", error=str(e))
            raise
    
    async def close(self):
        """Close database connections properly"""
        await engine.dispose()
        await logger.ainfo("Database connections closed")


# Global database manager instance
db_manager = DatabaseManager()


async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    """Dependency injection for FastAPI endpoints"""
    async with db_manager.get_session() as session:
        yield session


async def get_database_manager() -> DatabaseManager:
    """Get database manager instance for dependency injection"""
    return db_manager