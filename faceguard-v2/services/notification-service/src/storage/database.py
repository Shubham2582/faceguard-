"""
FACEGUARD V2 NOTIFICATION SERVICE - DATABASE CONNECTION
Rule 2: Zero Placeholder Code - Real async database operations
Rule 3: Error-First Development - Comprehensive connection error handling

Shared Database Access:
- Uses same PostgreSQL database as core-data-service
- Accesses notification_channels, alert_rules, alert_instances, notification_logs tables
- Async connection pool with proper error handling
"""

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.pool import NullPool, QueuePool
from sqlalchemy import text, MetaData
from contextlib import asynccontextmanager
import structlog
from typing import Dict, Any, Optional
import asyncio
from datetime import datetime

from config.settings import get_settings

logger = structlog.get_logger(__name__)
settings = get_settings()


class NotificationDatabaseManager:
    """
    Database manager for notification service
    Rule 2: Zero Placeholder Code - Real database connection management
    Rule 3: Error-First Development - Proper connection error handling
    """
    
    def __init__(self):
        self._engine = None
        self._session_maker = None
        self._connection_pool_info = {}
    
    async def initialize(self):
        """Initialize database connection pool"""
        try:
            await logger.ainfo("Initializing notification service database connection")
            
            # Create async engine with connection pooling
            connect_args = {
                "server_settings": {
                    "application_name": f"faceguard_notification_service_{settings.service_version}",
                }
            }
            
            self._engine = create_async_engine(
                settings.database_url,
                echo=settings.debug_mode,
                pool_size=settings.db_pool_size,
                max_overflow=settings.db_max_overflow,
                pool_timeout=settings.db_pool_timeout,
                pool_recycle=settings.db_pool_recycle,
                poolclass=QueuePool,
                connect_args=connect_args
            )
            
            # Create session factory
            self._session_maker = async_sessionmaker(
                bind=self._engine,
                class_=AsyncSession,
                expire_on_commit=False
            )
            
            # Test connection
            await self._test_connection()
            
            await logger.ainfo("Database connection initialized successfully",
                               pool_size=settings.db_pool_size,
                               max_overflow=settings.db_max_overflow)
            
        except Exception as e:
            await logger.aerror("Database initialization failed", error=str(e))
            raise
    
    async def _test_connection(self):
        """Test database connection and validate schema"""
        try:
            async with self._session_maker() as session:
                # Test basic connectivity
                result = await session.execute(text("SELECT 1 as test"))
                test_value = result.scalar()
                
                if test_value != 1:
                    raise Exception("Database connectivity test failed")
                
                # Validate notification tables exist
                tables_query = text("""
                    SELECT table_name 
                    FROM information_schema.tables 
                    WHERE table_schema = 'public' 
                    AND table_name IN ('notification_channels', 'alert_rules', 'alert_instances', 'notification_logs')
                """)
                
                tables_result = await session.execute(tables_query)
                existing_tables = [row[0] for row in tables_result]
                
                required_tables = ['notification_channels', 'alert_rules', 'alert_instances', 'notification_logs']
                missing_tables = [table for table in required_tables if table not in existing_tables]
                
                if missing_tables:
                    await logger.awarn("Some notification tables are missing", 
                                       missing_tables=missing_tables)
                else:
                    await logger.ainfo("All notification tables validated successfully")
                
        except Exception as e:
            await logger.aerror("Database connection test failed", error=str(e))
            raise
    
    @asynccontextmanager
    async def get_session(self):
        """Get database session with proper error handling"""
        if not self._session_maker:
            raise Exception("Database not initialized. Call initialize() first.")
        
        session = None
        try:
            session = self._session_maker()
            yield session
        except Exception as e:
            if session:
                await session.rollback()
            await logger.aerror("Database session error", error=str(e))
            raise
        finally:
            if session:
                await session.close()
    
    async def health_check(self) -> Dict[str, Any]:
        """
        Database health check
        Returns detailed health information for monitoring
        """
        try:
            start_time = datetime.utcnow()
            
            if not self._engine:
                return {
                    "status": "unhealthy",
                    "error": "Database not initialized",
                    "timestamp": start_time.isoformat()
                }
            
            async with self.get_session() as session:
                # Test query
                result = await session.execute(text("SELECT 1"))
                result.scalar()
                
                # Get connection pool status
                pool = self._engine.pool
                pool_info = {
                    "size": pool.size() if hasattr(pool, 'size') else "unknown",
                    "checked_in": pool.checkedin() if hasattr(pool, 'checkedin') else "unknown",
                    "checked_out": pool.checkedout() if hasattr(pool, 'checkedout') else "unknown",
                    "overflow": pool.overflow() if hasattr(pool, 'overflow') else "unknown"
                }
                
                # Test notification tables
                tables_query = text("""
                    SELECT 
                        'notification_channels' as table_name,
                        COUNT(*) as record_count
                    FROM notification_channels
                    WHERE is_active = true
                    UNION ALL
                    SELECT 
                        'alert_rules' as table_name,
                        COUNT(*) as record_count
                    FROM alert_rules
                    WHERE is_active = true
                    UNION ALL
                    SELECT 
                        'alert_instances' as table_name,
                        COUNT(*) as record_count
                    FROM alert_instances
                    WHERE triggered_at >= NOW() - INTERVAL '24 hours'
                """)
                
                tables_result = await session.execute(tables_query)
                table_stats = {row[0]: row[1] for row in tables_result}
                
                end_time = datetime.utcnow()
                response_time = (end_time - start_time).total_seconds() * 1000
                
                return {
                    "status": "healthy",
                    "database": "postgresql",
                    "connection_pool": pool_info,
                    "notification_tables": table_stats,
                    "response_time_ms": round(response_time, 2),
                    "timestamp": end_time.isoformat()
                }
                
        except Exception as e:
            await logger.aerror("Database health check failed", error=str(e))
            return {
                "status": "unhealthy",
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }
    
    async def get_connection_stats(self) -> Dict[str, Any]:
        """Get detailed connection statistics"""
        try:
            if not self._engine:
                return {"error": "Database not initialized"}
            
            pool = self._engine.pool
            
            return {
                "pool_size": pool.size() if hasattr(pool, 'size') else 0,
                "checked_in_connections": pool.checkedin() if hasattr(pool, 'checkedin') else 0,
                "checked_out_connections": pool.checkedout() if hasattr(pool, 'checkedout') else 0,
                "overflow_connections": pool.overflow() if hasattr(pool, 'overflow') else 0,
                "invalid_connections": pool.invalid() if hasattr(pool, 'invalid') else 0,
            }
        except Exception as e:
            await logger.aerror("Failed to get connection stats", error=str(e))
            return {"error": str(e)}
    
    async def close(self):
        """Close database connections"""
        try:
            if self._engine:
                await self._engine.dispose()
                self._engine = None
                self._session_maker = None
                await logger.ainfo("Database connections closed successfully")
        except Exception as e:
            await logger.aerror("Error closing database connections", error=str(e))


# Global database manager instance
_db_manager = None


async def get_database_manager() -> NotificationDatabaseManager:
    """Get global database manager instance (singleton pattern)"""
    global _db_manager
    if _db_manager is None:
        _db_manager = NotificationDatabaseManager()
        await _db_manager.initialize()
    return _db_manager


async def get_db_session():
    """Dependency function for FastAPI endpoints"""
    db_manager = await get_database_manager()
    async with db_manager.get_session() as session:
        yield session


# Database connection decorator for service methods
def with_db_session(func):
    """Decorator to inject database session into service methods"""
    async def wrapper(*args, **kwargs):
        db_manager = await get_database_manager()
        async with db_manager.get_session() as session:
            return await func(session, *args, **kwargs)
    return wrapper


# Transaction management helper
@asynccontextmanager
async def database_transaction():
    """Context manager for database transactions"""
    db_manager = await get_database_manager()
    async with db_manager.get_session() as session:
        try:
            await session.begin()
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise