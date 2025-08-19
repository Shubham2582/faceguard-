"""
FACEGUARD V2 CORE DATA SERVICE - HIGH PRIORITY PERSON SERVICE
Rule 1: Incremental Completeness - Complete CRUD operations for high priority persons
Rule 2: Zero Placeholder Code - Real database operations for alert escalation management
"""

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, func
from sqlalchemy.orm import selectinload
from typing import List, Optional, Dict, Any
from uuid import UUID
from datetime import datetime

from domain.models import HighPriorityPersonModel, PersonModel, NotificationContactModel
from domain.schemas import (
    HighPriorityPersonCreate,
    HighPriorityPersonUpdate,
    HighPriorityPersonRemove,
    HighPriorityPersonResponse,
    HighPriorityPersonListResponse,
    HighPriorityCheckResponse
)


class HighPriorityPersonService:
    """Service for managing high priority persons and alert escalation"""
    
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def add_high_priority_person(
        self, 
        person_data: HighPriorityPersonCreate
    ) -> HighPriorityPersonResponse:
        """
        Add a person to the high priority list
        Rule 3: Error-First Development - Validate person exists
        """
        # Validate person exists
        person_query = select(PersonModel).where(PersonModel.id == person_data.person_id)
        result = await self.session.execute(person_query)
        person = result.scalars().first()
        
        if not person:
            raise ValueError(f"Person with ID {person_data.person_id} not found")
        
        # Check if already in high priority list
        existing_query = select(HighPriorityPersonModel).where(
            and_(
                HighPriorityPersonModel.person_id == person_data.person_id,
                HighPriorityPersonModel.is_active == True
            )
        )
        result = await self.session.execute(existing_query)
        existing = result.scalars().first()
        
        if existing:
            raise ValueError(f"Person {person_data.person_id} is already in high priority list")
        
        # Validate priority level
        valid_levels = ["high", "critical", "wanted"]
        if person_data.priority_level not in valid_levels:
            raise ValueError(f"Invalid priority level. Must be one of: {valid_levels}")
        
        # Validate notification frequency
        valid_frequencies = ["immediate", "daily", "weekly"]
        if person_data.notification_frequency not in valid_frequencies:
            raise ValueError(f"Invalid notification frequency. Must be one of: {valid_frequencies}")
        
        # Create high priority person record
        high_priority_person = HighPriorityPersonModel(
            person_id=person_data.person_id,
            priority_level=person_data.priority_level,
            alert_reason=person_data.alert_reason,
            added_by=person_data.added_by,
            escalation_channels=person_data.escalation_channels,
            notification_frequency=person_data.notification_frequency,
            is_active=True
        )
        
        self.session.add(high_priority_person)
        await self.session.commit()
        await self.session.refresh(high_priority_person)
        
        # Return response with person details
        response = HighPriorityPersonResponse.model_validate(high_priority_person)
        response.person_first_name = person.first_name
        response.person_last_name = person.last_name
        response.person_person_id = person.person_id
        
        return response
    
    async def list_high_priority_persons(
        self,
        page: int = 1,
        limit: int = 50,
        active_only: bool = True,
        priority_level: Optional[str] = None
    ) -> HighPriorityPersonListResponse:
        """
        List all high priority persons with pagination and filtering
        """
        # Build query with filters
        query = select(HighPriorityPersonModel).join(PersonModel)
        
        if active_only:
            query = query.where(HighPriorityPersonModel.is_active == True)
        
        if priority_level:
            query = query.where(HighPriorityPersonModel.priority_level == priority_level)
        
        # Get total count
        count_query = select(func.count(HighPriorityPersonModel.id))
        if active_only:
            count_query = count_query.where(HighPriorityPersonModel.is_active == True)
        if priority_level:
            count_query = count_query.where(HighPriorityPersonModel.priority_level == priority_level)
        
        total_result = await self.session.execute(count_query)
        total = total_result.scalar()
        
        # Apply pagination and ordering
        query = query.order_by(HighPriorityPersonModel.added_at.desc())
        query = query.offset((page - 1) * limit).limit(limit)
        
        # Execute query with person details
        result = await self.session.execute(query)
        high_priority_persons = result.scalars().all()
        
        # Build response list with person details
        responses = []
        for hpp in high_priority_persons:
            # Get person details
            person_query = select(PersonModel).where(PersonModel.id == hpp.person_id)
            person_result = await self.session.execute(person_query)
            person = person_result.scalars().first()
            
            response = HighPriorityPersonResponse.model_validate(hpp)
            if person:
                response.person_first_name = person.first_name
                response.person_last_name = person.last_name
                response.person_person_id = person.person_id
            
            responses.append(response)
        
        # Calculate pagination info
        pages = (total + limit - 1) // limit if total > 0 else 0
        
        return HighPriorityPersonListResponse(
            high_priority_persons=responses,
            total=total,
            page=page,
            limit=limit,
            pages=pages
        )
    
    async def get_high_priority_person(self, person_id: UUID) -> Optional[HighPriorityPersonResponse]:
        """
        Get high priority person details by person ID
        """
        query = select(HighPriorityPersonModel).where(
            and_(
                HighPriorityPersonModel.person_id == person_id,
                HighPriorityPersonModel.is_active == True
            )
        )
        
        result = await self.session.execute(query)
        hpp = result.scalars().first()
        
        if not hpp:
            return None
        
        # Get person details
        person_query = select(PersonModel).where(PersonModel.id == person_id)
        person_result = await self.session.execute(person_query)
        person = person_result.scalars().first()
        
        response = HighPriorityPersonResponse.model_validate(hpp)
        if person:
            response.person_first_name = person.first_name
            response.person_last_name = person.last_name
            response.person_person_id = person.person_id
        
        return response
    
    async def update_high_priority_person(
        self,
        person_id: UUID,
        update_data: HighPriorityPersonUpdate
    ) -> HighPriorityPersonResponse:
        """
        Update high priority person settings
        """
        query = select(HighPriorityPersonModel).where(
            and_(
                HighPriorityPersonModel.person_id == person_id,
                HighPriorityPersonModel.is_active == True
            )
        )
        
        result = await self.session.execute(query)
        hpp = result.scalars().first()
        
        if not hpp:
            raise ValueError(f"High priority person with person_id {person_id} not found")
        
        # Validate updates
        if update_data.priority_level:
            valid_levels = ["high", "critical", "wanted"]
            if update_data.priority_level not in valid_levels:
                raise ValueError(f"Invalid priority level. Must be one of: {valid_levels}")
            hpp.priority_level = update_data.priority_level
        
        if update_data.notification_frequency:
            valid_frequencies = ["immediate", "daily", "weekly"]
            if update_data.notification_frequency not in valid_frequencies:
                raise ValueError(f"Invalid notification frequency. Must be one of: {valid_frequencies}")
            hpp.notification_frequency = update_data.notification_frequency
        
        # Apply updates
        if update_data.alert_reason is not None:
            hpp.alert_reason = update_data.alert_reason
        
        if update_data.escalation_channels:
            hpp.escalation_channels = update_data.escalation_channels
        
        if update_data.is_active is not None:
            hpp.is_active = update_data.is_active
            if not update_data.is_active:
                hpp.removed_at = datetime.utcnow()
        
        hpp.last_updated = datetime.utcnow()
        
        await self.session.commit()
        await self.session.refresh(hpp)
        
        # Get person details for response
        person_query = select(PersonModel).where(PersonModel.id == person_id)
        person_result = await self.session.execute(person_query)
        person = person_result.scalars().first()
        
        response = HighPriorityPersonResponse.model_validate(hpp)
        if person:
            response.person_first_name = person.first_name
            response.person_last_name = person.last_name
            response.person_person_id = person.person_id
        
        return response
    
    async def remove_high_priority_person(
        self,
        person_id: UUID,
        removal_data: HighPriorityPersonRemove
    ) -> HighPriorityPersonResponse:
        """
        Remove person from high priority list (soft delete)
        """
        query = select(HighPriorityPersonModel).where(
            and_(
                HighPriorityPersonModel.person_id == person_id,
                HighPriorityPersonModel.is_active == True
            )
        )
        
        result = await self.session.execute(query)
        hpp = result.scalars().first()
        
        if not hpp:
            raise ValueError(f"High priority person with person_id {person_id} not found")
        
        # Soft delete - mark as inactive
        hpp.is_active = False
        hpp.removed_at = datetime.utcnow()
        hpp.removed_by = removal_data.removed_by
        hpp.removal_reason = removal_data.removal_reason
        hpp.last_updated = datetime.utcnow()
        
        await self.session.commit()
        await self.session.refresh(hpp)
        
        # Get person details for response
        person_query = select(PersonModel).where(PersonModel.id == person_id)
        person_result = await self.session.execute(person_query)
        person = person_result.scalars().first()
        
        response = HighPriorityPersonResponse.model_validate(hpp)
        if person:
            response.person_first_name = person.first_name
            response.person_last_name = person.last_name
            response.person_person_id = person.person_id
        
        return response
    
    async def check_person_priority(self, person_id: UUID) -> HighPriorityCheckResponse:
        """
        Check if a person is high priority - used by alert evaluation
        PERFORMANCE CRITICAL: This is called for every person detection
        """
        query = select(HighPriorityPersonModel).where(
            and_(
                HighPriorityPersonModel.person_id == person_id,
                HighPriorityPersonModel.is_active == True
            )
        )
        
        result = await self.session.execute(query)
        hpp = result.scalars().first()
        
        if hpp:
            return HighPriorityCheckResponse(
                person_id=person_id,
                is_high_priority=True,
                priority_level=hpp.priority_level,
                alert_reason=hpp.alert_reason,
                escalation_channels=hpp.escalation_channels,
                notification_frequency=hpp.notification_frequency,
                added_by=hpp.added_by,
                added_at=hpp.added_at
            )
        else:
            return HighPriorityCheckResponse(
                person_id=person_id,
                is_high_priority=False
            )
    
    async def get_high_priority_statistics(self) -> Dict[str, Any]:
        """
        Get statistics about high priority persons
        """
        # Total active high priority persons
        total_query = select(func.count(HighPriorityPersonModel.id)).where(
            HighPriorityPersonModel.is_active == True
        )
        total_result = await self.session.execute(total_query)
        total_active = total_result.scalar()
        
        # Count by priority level
        levels_query = select(
            HighPriorityPersonModel.priority_level,
            func.count(HighPriorityPersonModel.id)
        ).where(
            HighPriorityPersonModel.is_active == True
        ).group_by(HighPriorityPersonModel.priority_level)
        
        levels_result = await self.session.execute(levels_query)
        levels_counts = dict(levels_result.all())
        
        # Recent additions (last 7 days)
        from datetime import timedelta
        recent_cutoff = datetime.utcnow() - timedelta(days=7)
        recent_query = select(func.count(HighPriorityPersonModel.id)).where(
            and_(
                HighPriorityPersonModel.is_active == True,
                HighPriorityPersonModel.added_at >= recent_cutoff
            )
        )
        recent_result = await self.session.execute(recent_query)
        recent_additions = recent_result.scalar()
        
        return {
            "total_active": total_active,
            "by_priority_level": levels_counts,
            "recent_additions_7_days": recent_additions,
            "escalation_enabled": total_active > 0
        }
    
    async def get_person_notification_contacts(self, person_id: UUID) -> List[Dict[str, Any]]:
        """
        Get notification contacts linked to a high priority person via the linking table
        Returns contacts with escalation delays and custom templates for person-specific alerts
        """
        try:
            # First check if this person is actually high priority
            hp_query = select(HighPriorityPersonModel).where(
                and_(
                    HighPriorityPersonModel.person_id == person_id,
                    HighPriorityPersonModel.is_active == True
                )
            )
            hp_result = await self.session.execute(hp_query)
            hp_person = hp_result.scalars().first()
            
            if not hp_person:
                return []  # Person is not high priority, no specific contacts
            
            # Query the linking table using raw SQL since we don't have an ORM model for it yet
            from sqlalchemy import text
            
            query = text("""
                SELECT 
                    nc.id as contact_id,
                    nc.contact_name,
                    nc.contact_type,
                    nc.contact_value,
                    nc.priority as contact_priority,
                    hpc.escalation_delay_minutes,
                    hpc.priority_override,
                    hpc.custom_message_template,
                    hpc.is_active as link_active
                FROM high_priority_person_contacts hpc
                JOIN notification_contacts nc ON hpc.notification_contact_id = nc.id
                WHERE hpc.high_priority_person_id = :hp_person_id
                  AND hpc.is_active = true
                  AND nc.is_active = true
                ORDER BY hpc.escalation_delay_minutes ASC, nc.priority DESC
            """)
            
            result = await self.session.execute(query, {"hp_person_id": hp_person.id})
            rows = result.fetchall()
            
            contacts = []
            for row in rows:
                contact_data = {
                    "id": str(row.contact_id),
                    "contact_name": row.contact_name,
                    "contact_type": row.contact_type,
                    "contact_value": row.contact_value,
                    "contact_priority": row.contact_priority,
                    "escalation_delay_minutes": row.escalation_delay_minutes,
                    "priority_override": row.priority_override or row.contact_priority,
                    "custom_message_template": row.custom_message_template,
                    "link_active": row.link_active
                }
                contacts.append(contact_data)
            
            return contacts
            
        except Exception as e:
            # Log error but don't fail the alert process
            import structlog
            logger = structlog.get_logger(__name__)
            await logger.aerror(
                "Failed to get person notification contacts",
                person_id=str(person_id),
                error=str(e)
            )
            return []