"""
FACEGUARD V2 CORE DATA SERVICE - NOTIFICATION CONTACTS API
Rule 1: Incremental Completeness - Complete CRUD operations
Rule 2: Zero Placeholder Code - Real database operations
Rule 3: Error-First Development - Comprehensive error handling
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
import structlog

from storage.database import get_db_session
from services.notification_contact_service import NotificationContactService
from domain.schemas import (
    NotificationContactCreate,
    NotificationContactUpdate,
    NotificationContactResponse,
    NotificationContactListResponse,
    NotificationContactVerify,
    NotificationContactTestRequest,
    NotificationContactTestResponse,
    ErrorResponse
)

router = APIRouter(prefix="/notification-contacts", tags=["notification-contacts"])
logger = structlog.get_logger(__name__)

# Initialize service
contact_service = NotificationContactService()


@router.post("/", response_model=NotificationContactResponse, status_code=201)
async def create_notification_contact(
    contact_data: NotificationContactCreate,
    db: AsyncSession = Depends(get_db_session)
):
    """
    Create a new notification contact
    
    Contact types:
    - email: Email address for notifications
    - phone: Phone number for SMS notifications
    - webhook: URL for webhook notifications
    """
    try:
        contact = await contact_service.create_contact(db, contact_data)
        
        await logger.ainfo(
            "Notification contact created via API",
            contact_id=contact.id,
            contact_type=contact.contact_type,
            contact_value=contact.contact_value
        )
        
        return contact
        
    except ValueError as e:
        await logger.awarn("Invalid contact data", error=str(e))
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        await logger.aerror("Failed to create notification contact", error=str(e))
        raise HTTPException(
            status_code=500,
            detail={
                "error": "contact_creation_failed",
                "message": "Failed to create notification contact",
                "details": {"reason": str(e)}
            }
        )


@router.get("/", response_model=NotificationContactListResponse)
async def list_notification_contacts(
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(50, ge=1, le=100, description="Items per page"),
    contact_type: Optional[str] = Query(None, description="Filter by contact type"),
    is_active: Optional[bool] = Query(None, description="Filter by active status"),
    is_verified: Optional[bool] = Query(None, description="Filter by verification status"),
    person_id: Optional[str] = Query(None, description="Filter by linked person"),
    priority: Optional[str] = Query(None, description="Filter by priority"),
    db: AsyncSession = Depends(get_db_session)
):
    """
    List notification contacts with optional filtering
    
    Filters:
    - contact_type: email, phone, webhook
    - is_active: true/false
    - is_verified: true/false
    - person_id: UUID of linked person
    - priority: low, medium, high, critical
    """
    try:
        result = await contact_service.list_contacts(
            db,
            page=page,
            limit=limit,
            contact_type=contact_type,
            is_active=is_active,
            is_verified=is_verified,
            person_id=person_id,
            priority=priority
        )
        
        return NotificationContactListResponse(**result)
        
    except Exception as e:
        await logger.aerror("Failed to list notification contacts", error=str(e))
        raise HTTPException(
            status_code=500,
            detail={
                "error": "contact_list_failed",
                "message": "Failed to retrieve notification contacts",
                "details": {"reason": str(e)}
            }
        )


@router.get("/{contact_id}", response_model=NotificationContactResponse)
async def get_notification_contact(
    contact_id: str,
    db: AsyncSession = Depends(get_db_session)
):
    """Get a specific notification contact by ID"""
    try:
        contact = await contact_service.get_contact(db, contact_id)
        
        if not contact:
            raise HTTPException(
                status_code=404,
                detail={
                    "error": "contact_not_found",
                    "message": f"Notification contact {contact_id} not found"
                }
            )
        
        return contact
        
    except HTTPException:
        raise
    except Exception as e:
        await logger.aerror("Failed to get notification contact", error=str(e))
        raise HTTPException(
            status_code=500,
            detail={
                "error": "contact_retrieval_failed",
                "message": "Failed to retrieve notification contact",
                "details": {"reason": str(e)}
            }
        )


@router.put("/{contact_id}", response_model=NotificationContactResponse)
async def update_notification_contact(
    contact_id: str,
    update_data: NotificationContactUpdate,
    db: AsyncSession = Depends(get_db_session)
):
    """Update a notification contact"""
    try:
        contact = await contact_service.update_contact(db, contact_id, update_data)
        
        if not contact:
            raise HTTPException(
                status_code=404,
                detail={
                    "error": "contact_not_found",
                    "message": f"Notification contact {contact_id} not found"
                }
            )
        
        await logger.ainfo(
            "Notification contact updated via API",
            contact_id=contact_id,
            updated_fields=list(update_data.dict(exclude_unset=True).keys())
        )
        
        return contact
        
    except HTTPException:
        raise
    except Exception as e:
        await logger.aerror("Failed to update notification contact", error=str(e))
        raise HTTPException(
            status_code=500,
            detail={
                "error": "contact_update_failed",
                "message": "Failed to update notification contact",
                "details": {"reason": str(e)}
            }
        )


@router.delete("/{contact_id}", status_code=204)
async def delete_notification_contact(
    contact_id: str,
    db: AsyncSession = Depends(get_db_session)
):
    """Delete a notification contact"""
    try:
        deleted = await contact_service.delete_contact(db, contact_id)
        
        if not deleted:
            raise HTTPException(
                status_code=404,
                detail={
                    "error": "contact_not_found",
                    "message": f"Notification contact {contact_id} not found"
                }
            )
        
        await logger.ainfo(
            "Notification contact deleted via API",
            contact_id=contact_id
        )
        
        return None
        
    except HTTPException:
        raise
    except Exception as e:
        await logger.aerror("Failed to delete notification contact", error=str(e))
        raise HTTPException(
            status_code=500,
            detail={
                "error": "contact_deletion_failed",
                "message": "Failed to delete notification contact",
                "details": {"reason": str(e)}
            }
        )


@router.post("/{contact_id}/verify", response_model=NotificationContactResponse)
async def verify_notification_contact(
    contact_id: str,
    verification_data: NotificationContactVerify,
    db: AsyncSession = Depends(get_db_session)
):
    """
    Verify a notification contact with verification code
    
    Note: For testing, use verification code "1234"
    """
    try:
        contact = await contact_service.verify_contact(db, contact_id, verification_data)
        
        if not contact:
            raise HTTPException(
                status_code=404,
                detail={
                    "error": "contact_not_found",
                    "message": f"Notification contact {contact_id} not found"
                }
            )
        
        await logger.ainfo(
            "Notification contact verified via API",
            contact_id=contact_id
        )
        
        return contact
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        await logger.aerror("Failed to verify notification contact", error=str(e))
        raise HTTPException(
            status_code=500,
            detail={
                "error": "contact_verification_failed",
                "message": "Failed to verify notification contact",
                "details": {"reason": str(e)}
            }
        )


@router.post("/{contact_id}/test", response_model=NotificationContactTestResponse)
async def test_notification_contact(
    contact_id: str,
    test_data: NotificationContactTestRequest = NotificationContactTestRequest(),
    db: AsyncSession = Depends(get_db_session)
):
    """
    Test a notification contact by sending a test message
    
    This will send a real test notification to the contact
    """
    try:
        test_response = await contact_service.test_contact(db, contact_id, test_data)
        
        await logger.ainfo(
            "Notification contact tested via API",
            contact_id=contact_id,
            test_status=test_response.test_status
        )
        
        return test_response
        
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        await logger.aerror("Failed to test notification contact", error=str(e))
        raise HTTPException(
            status_code=500,
            detail={
                "error": "contact_test_failed",
                "message": "Failed to test notification contact",
                "details": {"reason": str(e)}
            }
        )


@router.get("/person/{person_id}", response_model=list[NotificationContactResponse])
async def get_person_notification_contacts(
    person_id: str,
    db: AsyncSession = Depends(get_db_session)
):
    """Get all notification contacts linked to a specific person"""
    try:
        contacts = await contact_service.get_contacts_for_person(db, person_id)
        
        await logger.ainfo(
            "Retrieved notification contacts for person",
            person_id=person_id,
            contact_count=len(contacts)
        )
        
        return contacts
        
    except Exception as e:
        await logger.aerror("Failed to get person notification contacts", error=str(e))
        raise HTTPException(
            status_code=500,
            detail={
                "error": "person_contacts_retrieval_failed",
                "message": "Failed to retrieve notification contacts for person",
                "details": {"reason": str(e)}
            }
        )