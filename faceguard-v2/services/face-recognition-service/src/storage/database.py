"""
Database Connection for Face Recognition Service
LOCAL PostgreSQL (postgres:1234) - NEVER Docker
Preserves 157 embeddings from V1 system
"""

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
import asyncio
from typing import Optional, List, Dict

from config.settings import settings

# Base for model declarations
Base = declarative_base()

# Async engine for non-blocking operations
async_engine = create_async_engine(
    settings.database_url,
    echo=False,
    pool_pre_ping=True,
    pool_size=10,
    max_overflow=20
)

# Sync engine for certain operations
sync_engine = create_engine(
    settings.sync_database_url,
    echo=False,
    pool_pre_ping=True,
    pool_size=5
)

# Async session factory
AsyncSessionLocal = async_sessionmaker(
    bind=async_engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False
)

# Sync session factory
SyncSessionLocal = sessionmaker(
    bind=sync_engine,
    autocommit=False,
    autoflush=False
)


class DatabaseService:
    """
    Database service for face recognition
    Handles embedding retrieval and recognition event logging
    """
    
    def __init__(self):
        self.async_session = AsyncSessionLocal
        self.sync_session = SyncSessionLocal
    
    async def check_connection(self) -> bool:
        """Check database connectivity"""
        try:
            async with self.async_session() as session:
                result = await session.execute(text("SELECT 1"))
                return result.scalar() == 1
        except Exception as e:
            print(f"Database connection error: {e}")
            return False
    
    async def get_all_embeddings(self) -> List[Dict]:
        """
        Retrieve all 157 embeddings from V1 database
        Real data, no mocks
        """
        try:
            async with self.async_session() as session:
                # Query to get embeddings with person info
                query = text("""
                    SELECT 
                        e.embedding_id,
                        e.person_id,
                        e.vector_data,
                        e.confidence_score,
                        e.model_name,
                        e.status,
                        p.person_id as person_identifier,
                        p.first_name,
                        p.last_name
                    FROM embeddings e
                    JOIN persons p ON e.person_id = p.id
                    WHERE e.status = 'active' AND p.status = 'active'
                    ORDER BY e.created_at
                """)
                
                result = await session.execute(query)
                embeddings = []
                
                for row in result:
                    embeddings.append({
                        'embedding_id': row.embedding_id,
                        'person_id': row.person_identifier,  # Use person_id string
                        'person_uuid': str(row.person_id),  # Database UUID
                        'vector_data': list(row.vector_data) if row.vector_data else [],
                        'confidence_score': row.confidence_score,
                        'model_name': row.model_name,
                        'person_name': f"{row.first_name or ''} {row.last_name or ''}".strip()
                    })
                
                print(f"Retrieved {len(embeddings)} embeddings from database")
                return embeddings
                
        except Exception as e:
            print(f"Error retrieving embeddings: {e}")
            return []
    
    async def get_person_embeddings(self, person_id: str) -> List[Dict]:
        """
        Get ALL embeddings for a specific person
        Critical: Returns ALL embeddings (not LIMIT 1)
        """
        try:
            async with self.async_session() as session:
                query = text("""
                    SELECT 
                        e.embedding_id,
                        e.vector_data,
                        e.confidence_score,
                        e.quality_score,
                        e.is_primary
                    FROM embeddings e
                    JOIN persons p ON e.person_id = p.id
                    WHERE p.person_id = :person_id 
                    AND e.status = 'active'
                    ORDER BY e.is_primary DESC, e.confidence_score DESC
                """)
                
                result = await session.execute(query, {'person_id': person_id})
                embeddings = []
                
                for row in result:
                    embeddings.append({
                        'embedding_id': row.embedding_id,
                        'vector_data': list(row.vector_data) if row.vector_data else [],
                        'confidence_score': row.confidence_score,
                        'quality_score': row.quality_score,
                        'is_primary': row.is_primary
                    })
                
                return embeddings
                
        except Exception as e:
            print(f"Error getting person embeddings: {e}")
            return []
    
    async def log_recognition_event(
        self,
        person_id: str,
        confidence: float,
        processing_time_ms: int,
        gpu_used: bool = True,
        face_count: int = 1
    ) -> bool:
        """
        Log recognition event to database
        Real event logging, no placeholders
        """
        try:
            async with self.async_session() as session:
                # Get person UUID from person_id
                person_query = text("""
                    SELECT id FROM persons WHERE person_id = :person_id
                """)
                person_result = await session.execute(person_query, {'person_id': person_id})
                person_uuid = person_result.scalar()
                
                if not person_uuid:
                    print(f"Person not found: {person_id}")
                    return False
                
                # Generate event ID
                import uuid
                event_id = f"event_{uuid.uuid4().hex[:8]}"
                
                # Insert recognition event
                insert_query = text("""
                    INSERT INTO recognition_events (
                        id, event_id, person_id, confidence_score, 
                        similarity_score, processing_time_ms, gpu_used,
                        model_name, face_count
                    ) VALUES (
                        :id, :event_id, :person_id, :confidence,
                        :confidence, :processing_time, :gpu_used,
                        :model_name, :face_count
                    )
                """)
                
                await session.execute(insert_query, {
                    'id': str(uuid.uuid4()),
                    'event_id': event_id,
                    'person_id': str(person_uuid),
                    'confidence': confidence,
                    'processing_time': processing_time_ms,
                    'gpu_used': gpu_used,
                    'model_name': settings.model_name,
                    'face_count': face_count
                })
                
                # Update person's last_seen and recognition_count
                update_query = text("""
                    UPDATE persons 
                    SET last_seen = CURRENT_TIMESTAMP,
                        recognition_count = recognition_count + 1,
                        avg_confidence = CASE 
                            WHEN avg_confidence IS NULL THEN :confidence
                            ELSE (avg_confidence * recognition_count + :confidence) / (recognition_count + 1)
                        END
                    WHERE id = :person_id
                """)
                
                await session.execute(update_query, {
                    'person_id': str(person_uuid),
                    'confidence': confidence
                })
                
                await session.commit()
                return True
                
        except Exception as e:
            print(f"Error logging recognition event: {e}")
            return False
    
    async def get_database_stats(self) -> Dict:
        """Get database statistics"""
        try:
            async with self.async_session() as session:
                stats_query = text("""
                    SELECT 
                        (SELECT COUNT(*) FROM persons WHERE status = 'active') as active_persons,
                        (SELECT COUNT(*) FROM embeddings WHERE status = 'active') as active_embeddings,
                        (SELECT COUNT(*) FROM recognition_events) as total_events,
                        (SELECT COUNT(DISTINCT person_id) FROM embeddings) as persons_with_embeddings
                """)
                
                result = await session.execute(stats_query)
                row = result.fetchone()
                
                return {
                    'active_persons': row.active_persons,
                    'active_embeddings': row.active_embeddings,
                    'total_events': row.total_events,
                    'persons_with_embeddings': row.persons_with_embeddings
                }
                
        except Exception as e:
            print(f"Error getting database stats: {e}")
            return {
                'active_persons': 0,
                'active_embeddings': 0,
                'total_events': 0,
                'persons_with_embeddings': 0
            }


# Global database service instance
db_service = DatabaseService()