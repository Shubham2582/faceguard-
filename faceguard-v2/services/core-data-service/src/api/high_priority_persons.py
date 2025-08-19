"""
FACEGUARD V2 CORE DATA SERVICE - HIGH PRIORITY PERSONS API
Rule 1: Incremental Completeness - Complete CRUD API for managing high-alert persons
Rule 2: Zero Placeholder Code - Real endpoints for alert escalation management
Rule 3: Error-First Development - Comprehensive validation and error handling
"""

from fastapi import APIRouter, HTTPException, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
from uuid import UUID

from storage.database import get_db_session
from services.high_priority_person_service import HighPriorityPersonService
from domain.schemas import (
    HighPriorityPersonCreate,
    HighPriorityPersonUpdate,
    HighPriorityPersonRemove,
    HighPriorityPersonResponse,
    HighPriorityPersonListResponse,
    HighPriorityCheckResponse
)
import structlog

logger = structlog.get_logger(__name__)

router = APIRouter(prefix="/high-priority-persons", tags=["high-priority-persons"])


@router.post("/", response_model=HighPriorityPersonResponse, status_code=201)
async def add_high_priority_person(
    person_data: HighPriorityPersonCreate,
    session: AsyncSession = Depends(get_db_session)
):
    """
    Add a person to the high priority list
    When these persons are detected, alerts go to ALL channels (SMS + Email + Dashboard)
    """
    try:
        service = HighPriorityPersonService(session)
        high_priority_person = await service.add_high_priority_person(person_data)
        
        return high_priority_person
        
    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail={
                "error": "validation_error",
                "message": str(e)
            }
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={
                "error": "server_error",
                "message": "Failed to add person to high priority list",
                "details": {"reason": str(e)}
            }
        )


@router.get("/", response_model=HighPriorityPersonListResponse)
async def list_high_priority_persons(
    page: int = Query(1, ge=1, description="Page number starting from 1"),
    limit: int = Query(50, ge=1, le=100, description="Number of persons per page"),
    active_only: bool = Query(True, description="Filter to active high priority persons only"),
    priority_level: Optional[str] = Query(None, description="Filter by priority level: high, critical, wanted"),
    session: AsyncSession = Depends(get_db_session)
):
    """
    List all high priority persons with pagination and filtering
    """
    try:
        # Validate priority level if provided
        if priority_level:
            valid_levels = ["high", "critical", "wanted"]
            if priority_level not in valid_levels:
                raise HTTPException(
                    status_code=400,
                    detail={
                        "error": "validation_error",
                        "message": f"Invalid priority level. Must be one of: {valid_levels}"
                    }
                )
        
        service = HighPriorityPersonService(session)
        result = await service.list_high_priority_persons(
            page=page,
            limit=limit,
            active_only=active_only,
            priority_level=priority_level
        )
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={
                "error": "server_error",
                "message": "Failed to retrieve high priority persons",
                "details": {"reason": str(e)}
            }
        )


@router.get("/check/{person_id}", response_model=HighPriorityCheckResponse)
async def check_person_priority(
    person_id: UUID,
    session: AsyncSession = Depends(get_db_session)
):
    """
    Check if a person is high priority - used by alert evaluation
    PERFORMANCE CRITICAL: This is called for every person detection
    """
    try:
        service = HighPriorityPersonService(session)
        result = await service.check_person_priority(person_id)
        
        return result
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={
                "error": "server_error",
                "message": "Failed to check person priority status",
                "details": {"reason": str(e)}
            }
        )


@router.get("/{person_id}/notification-contacts")
async def get_person_notification_contacts(
    person_id: UUID,
    session: AsyncSession = Depends(get_db_session)
):
    """
    Get notification contacts linked to a high priority person
    Used by notification service for person-specific alert delivery
    """
    try:
        service = HighPriorityPersonService(session)
        contacts = await service.get_person_notification_contacts(person_id)
        
        return contacts
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={
                "error": "server_error",
                "message": "Failed to retrieve person notification contacts",
                "details": {"reason": str(e)}
            }
        )


@router.get("/{person_id}", response_model=HighPriorityPersonResponse)
async def get_high_priority_person(
    person_id: UUID,
    session: AsyncSession = Depends(get_db_session)
):
    """
    Get high priority person details by person ID
    """
    try:
        service = HighPriorityPersonService(session)
        result = await service.get_high_priority_person(person_id)
        
        if not result:
            raise HTTPException(
                status_code=404,
                detail={
                    "error": "not_found",
                    "message": f"High priority person with person_id {person_id} not found"
                }
            )
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={
                "error": "server_error",
                "message": "Failed to retrieve high priority person",
                "details": {"reason": str(e)}
            }
        )


@router.put("/{person_id}", response_model=HighPriorityPersonResponse)
async def update_high_priority_person(
    person_id: UUID,
    update_data: HighPriorityPersonUpdate,
    session: AsyncSession = Depends(get_db_session)
):
    """
    Update high priority person settings
    """
    try:
        service = HighPriorityPersonService(session)
        result = await service.update_high_priority_person(person_id, update_data)
        
        return result
        
    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail={
                "error": "validation_error",
                "message": str(e)
            }
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={
                "error": "server_error",
                "message": "Failed to update high priority person",
                "details": {"reason": str(e)}
            }
        )


@router.delete("/{person_id}", response_model=HighPriorityPersonResponse)
async def remove_high_priority_person(
    person_id: UUID,
    removal_data: HighPriorityPersonRemove,
    session: AsyncSession = Depends(get_db_session)
):
    """
    Remove person from high priority list (soft delete)
    """
    try:
        service = HighPriorityPersonService(session)
        result = await service.remove_high_priority_person(person_id, removal_data)
        
        return result
        
    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail={
                "error": "validation_error",
                "message": str(e)
            }
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={
                "error": "server_error",
                "message": "Failed to remove high priority person",
                "details": {"reason": str(e)}
            }
        )


@router.get("/statistics/summary")
async def get_high_priority_statistics(
    session: AsyncSession = Depends(get_db_session)
):
    """
    Get statistics about high priority persons
    """
    try:
        service = HighPriorityPersonService(session)
        statistics = await service.get_high_priority_statistics()
        
        return {
            "status": "success",
            "statistics": statistics,
            "timestamp": "2024-01-15T10:30:00Z"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={
                "error": "server_error",
                "message": "Failed to retrieve high priority statistics",
                "details": {"reason": str(e)}
            }
        )


# Bulk operations for administrative efficiency

@router.post("/bulk/add")
async def bulk_add_high_priority_persons(
    persons_data: list[HighPriorityPersonCreate],
    session: AsyncSession = Depends(get_db_session)
):
    """
    Add multiple persons to high priority list in bulk
    """
    if len(persons_data) > 50:
        raise HTTPException(
            status_code=400,
            detail={
                "error": "validation_error",
                "message": "Bulk operations limited to 50 persons at a time"
            }
        )
    
    try:
        service = HighPriorityPersonService(session)
        results = []
        errors = []
        
        for i, person_data in enumerate(persons_data):
            try:
                result = await service.add_high_priority_person(person_data)
                results.append(result)
            except Exception as e:
                errors.append({
                    "index": i,
                    "person_id": str(person_data.person_id),
                    "error": str(e)
                })
        
        return {
            "status": "completed",
            "successful": len(results),
            "failed": len(errors),
            "results": results,
            "errors": errors
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={
                "error": "server_error",
                "message": "Failed to bulk add high priority persons",
                "details": {"reason": str(e)}
            }
        )


@router.post("/bulk/remove")
async def bulk_remove_high_priority_persons(
    person_ids: list[UUID],
    removal_data: HighPriorityPersonRemove,
    session: AsyncSession = Depends(get_db_session)
):
    """
    Remove multiple persons from high priority list in bulk
    """
    if len(person_ids) > 50:
        raise HTTPException(
            status_code=400,
            detail={
                "error": "validation_error",
                "message": "Bulk operations limited to 50 persons at a time"
            }
        )
    
    try:
        service = HighPriorityPersonService(session)
        results = []
        errors = []
        
        for i, person_id in enumerate(person_ids):
            try:
                result = await service.remove_high_priority_person(person_id, removal_data)
                results.append(result)
            except Exception as e:
                errors.append({
                    "index": i,
                    "person_id": str(person_id),
                    "error": str(e)
                })
        
        return {
            "status": "completed",
            "successful": len(results),
            "failed": len(errors),
            "results": results,
            "errors": errors
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={
                "error": "server_error",
                "message": "Failed to bulk remove high priority persons",
                "details": {"reason": str(e)}
            }
        )