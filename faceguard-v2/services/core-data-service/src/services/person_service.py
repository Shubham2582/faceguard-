"""
FACEGUARD V2 CORE DATA SERVICE - PERSON SERVICE
Rule 2: Zero Placeholder Code - Real CRUD operations implementation
Rule 3: Error-First Development - Comprehensive error handling
Critical: NO 501 "Not Implemented" errors anywhere
"""

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from typing import List, Optional, Dict, Any
import structlog
import uuid
from datetime import datetime

from domain.models import PersonModel, EmbeddingModel
from domain.schemas import (
    PersonCreate, PersonUpdate, PersonResponse, PersonListResponse,
    ErrorResponse
)

logger = structlog.get_logger(__name__)


class PersonService:
    """
    Person service with REAL CRUD operations
    Rule 2: Zero Placeholder Code - Complete implementations only
    Rule 3: Error-First Development - Proper exception handling
    """
    
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def create_person(self, person_data: PersonCreate) -> PersonResponse:
        """
        Create new person with validation and duplicate checking
        Rule 3: Error-First Development - Comprehensive validation
        
        Returns:
            PersonResponse: Created person data
            
        Raises:
            ValueError: Validation errors
            IntegrityError: Duplicate person_id
        """
        try:
            # Generate person_id if not provided
            if not person_data.person_id:
                person_id = f"person_{uuid.uuid4().hex[:8]}"
            else:
                person_id = person_data.person_id
            
            # Check for duplicate person_id
            existing = await self._get_person_by_person_id(person_id)
            if existing:
                raise ValueError(f"Person with person_id '{person_id}' already exists")
            
            # Create person model
            person = PersonModel(
                person_id=person_id,
                first_name=person_data.first_name.strip(),
                last_name=person_data.last_name.strip(),
                email=person_data.email,
                phone=person_data.phone,
                department=person_data.department,
                position=person_data.position,
                access_level=person_data.access_level,
                is_vip=person_data.is_vip,
                is_watchlist=person_data.is_watchlist,
                status="active",
                is_verified=False,
                face_count=0,
                embedding_count=0,
                recognition_count=0
            )
            
            self.session.add(person)
            await self.session.commit()
            await self.session.refresh(person)
            
            await logger.ainfo("Person created successfully", 
                               person_id=person.person_id,
                               name=f"{person.first_name} {person.last_name}")
            
            return PersonResponse.model_validate(person)
            
        except IntegrityError as e:
            await self.session.rollback()
            await logger.aerror("Person creation failed - integrity error", error=str(e))
            raise ValueError(f"Person creation failed: {str(e)}")
        except SQLAlchemyError as e:
            await self.session.rollback()
            await logger.aerror("Person creation failed - database error", error=str(e))
            raise Exception(f"Database error during person creation: {str(e)}")
        except Exception as e:
            await self.session.rollback()
            await logger.aerror("Person creation failed - unexpected error", error=str(e))
            raise
    
    async def get_person_by_id(self, person_id: str) -> Optional[PersonResponse]:
        """
        Get person by UUID or person_id
        Rule 3: Error-First Development - Proper not found handling
        
        Args:
            person_id: UUID or person_id string
            
        Returns:
            PersonResponse or None if not found
        """
        try:
            # Try UUID first, then person_id
            if self._is_uuid(person_id):
                query = select(PersonModel).where(PersonModel.id == person_id)
            else:
                query = select(PersonModel).where(PersonModel.person_id == person_id)
            
            result = await self.session.execute(query)
            person = result.scalars().first()
            
            if not person:
                await logger.ainfo("Person not found", person_id=person_id)
                return None
            
            return PersonResponse.model_validate(person)
            
        except SQLAlchemyError as e:
            await logger.aerror("Database error retrieving person", person_id=person_id, error=str(e))
            raise Exception(f"Database error: {str(e)}")
        except Exception as e:
            await logger.aerror("Unexpected error retrieving person", person_id=person_id, error=str(e))
            raise
    
    async def update_person(self, person_id: str, person_data: PersonUpdate) -> Optional[PersonResponse]:
        """
        Update person with partial data
        Rule 3: Error-First Development - Validation and existence checking
        
        Args:
            person_id: UUID or person_id string
            person_data: Partial update data
            
        Returns:
            PersonResponse or None if not found
            
        Raises:
            ValueError: Validation errors
        """
        try:
            # Find existing person
            if self._is_uuid(person_id):
                query = select(PersonModel).where(PersonModel.id == person_id)
            else:
                query = select(PersonModel).where(PersonModel.person_id == person_id)
            
            result = await self.session.execute(query)
            person = result.scalars().first()
            
            if not person:
                await logger.ainfo("Person not found for update", person_id=person_id)
                return None
            
            # Update fields (only non-None values)
            update_data = person_data.model_dump(exclude_unset=True)
            
            for field, value in update_data.items():
                if hasattr(person, field):
                    setattr(person, field, value)
            
            # Update timestamp
            person.updated_at = datetime.utcnow()
            
            await self.session.commit()
            await self.session.refresh(person)
            
            await logger.ainfo("Person updated successfully", 
                               person_id=person.person_id,
                               updated_fields=list(update_data.keys()))
            
            return PersonResponse.model_validate(person)
            
        except IntegrityError as e:
            await self.session.rollback()
            await logger.aerror("Person update failed - integrity error", person_id=person_id, error=str(e))
            raise ValueError(f"Person update failed: {str(e)}")
        except SQLAlchemyError as e:
            await self.session.rollback()
            await logger.aerror("Person update failed - database error", person_id=person_id, error=str(e))
            raise Exception(f"Database error: {str(e)}")
        except Exception as e:
            await self.session.rollback()
            await logger.aerror("Person update failed - unexpected error", person_id=person_id, error=str(e))
            raise
    
    async def delete_person(self, person_id: str) -> bool:
        """
        Delete person and associated embeddings
        Rule 3: Error-First Development - Cascade deletion with proper cleanup
        
        Args:
            person_id: UUID or person_id string
            
        Returns:
            bool: True if deleted, False if not found
        """
        try:
            # Find existing person
            if self._is_uuid(person_id):
                query = select(PersonModel).where(PersonModel.id == person_id)
            else:
                query = select(PersonModel).where(PersonModel.person_id == person_id)
            
            result = await self.session.execute(query)
            person = result.scalars().first()
            
            if not person:
                await logger.ainfo("Person not found for deletion", person_id=person_id)
                return False
            
            # Delete associated embeddings first
            embedding_query = select(EmbeddingModel).where(EmbeddingModel.person_id == person.id)
            embedding_result = await self.session.execute(embedding_query)
            embeddings = embedding_result.scalars().all()
            
            for embedding in embeddings:
                await self.session.delete(embedding)
            
            # Delete person
            await self.session.delete(person)
            await self.session.commit()
            
            await logger.ainfo("Person deleted successfully", 
                               person_id=person.person_id,
                               name=f"{person.first_name} {person.last_name}",
                               embeddings_deleted=len(embeddings))
            
            return True
            
        except SQLAlchemyError as e:
            await self.session.rollback()
            await logger.aerror("Person deletion failed - database error", person_id=person_id, error=str(e))
            raise Exception(f"Database error: {str(e)}")
        except Exception as e:
            await self.session.rollback()
            await logger.aerror("Person deletion failed - unexpected error", person_id=person_id, error=str(e))
            raise
    
    async def list_persons(self, page: int = 1, limit: int = 20, 
                          search: Optional[str] = None,
                          status: Optional[str] = None) -> PersonListResponse:
        """
        List persons with pagination and filtering
        Rule 2: Zero Placeholder Code - Real pagination implementation
        
        Args:
            page: Page number (1-based)
            limit: Items per page (1-100)
            search: Search term for name/email
            status: Filter by status
            
        Returns:
            PersonListResponse: Paginated person list
        """
        try:
            # Validate pagination parameters
            if page < 1:
                page = 1
            if not (1 <= limit <= 100):
                limit = 20
            
            offset = (page - 1) * limit
            
            # Build query
            query = select(PersonModel)
            
            # Apply filters
            conditions = []
            
            if search:
                search_term = f"%{search.strip()}%"
                conditions.append(
                    or_(
                        PersonModel.first_name.ilike(search_term),
                        PersonModel.last_name.ilike(search_term),
                        PersonModel.email.ilike(search_term),
                        PersonModel.person_id.ilike(search_term)
                    )
                )
            
            if status:
                conditions.append(PersonModel.status == status)
            
            if conditions:
                query = query.where(and_(*conditions))
            
            # Get total count
            count_query = select(func.count(PersonModel.id))
            if conditions:
                count_query = count_query.where(and_(*conditions))
            
            total_result = await self.session.execute(count_query)
            total = total_result.scalar()
            
            # Apply pagination and ordering
            query = query.order_by(PersonModel.created_at.desc()).offset(offset).limit(limit)
            
            # Execute query
            result = await self.session.execute(query)
            persons = result.scalars().all()
            
            # Convert to response models
            person_responses = [PersonResponse.model_validate(person) for person in persons]
            
            await logger.ainfo("Persons listed successfully", 
                               page=page, limit=limit, total=total, returned=len(person_responses))
            
            return PersonListResponse(
                total=total,
                page=page,
                limit=limit,
                persons=person_responses
            )
            
        except SQLAlchemyError as e:
            await logger.aerror("Person listing failed - database error", error=str(e))
            raise Exception(f"Database error: {str(e)}")
        except Exception as e:
            await logger.aerror("Person listing failed - unexpected error", error=str(e))
            raise
    
    async def _get_person_by_person_id(self, person_id: str) -> Optional[PersonModel]:
        """Internal helper to check person existence by person_id"""
        query = select(PersonModel).where(PersonModel.person_id == person_id)
        result = await self.session.execute(query)
        return result.scalars().first()
    
    def _is_uuid(self, value: str) -> bool:
        """Check if string is a valid UUID"""
        try:
            uuid.UUID(value)
            return True
        except (ValueError, TypeError):
            return False


async def get_person_service(session: AsyncSession) -> PersonService:
    """Dependency injection for PersonService"""
    return PersonService(session)