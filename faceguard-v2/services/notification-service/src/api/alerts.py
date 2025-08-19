"""
FACEGUARD V2 NOTIFICATION SERVICE - ALERTS API (REDESIGNED)
CRITICAL: Uses Core Data Service API - NO direct database access
Rule 1: Incremental Completeness - 100% functional implementation
Rule 2: Zero Placeholder Code - Real alert rule management via Core Data Service
Rule 3: Error-First Development - Comprehensive validation and error handling
"""

from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional, Dict, Any
import structlog
from datetime import datetime
from uuid import UUID

from clients.core_data_client import get_core_data_client, CoreDataServiceError
from pydantic import BaseModel


# Alert rule creation schema for API requests
class SimpleAlertRuleCreate(BaseModel):
    rule_name: str
    description: str
    priority: str = "medium"  # low, medium, high
    trigger_conditions: Dict[str, Any]
    is_active: bool = True
    cooldown_minutes: int = 30
    escalation_minutes: Optional[int] = None
    auto_resolve_minutes: int = 240
    notification_channels: List[str] = []
    notification_template: Dict[str, Any] = {}
    created_by: str = "system"


router = APIRouter(prefix="/alerts", tags=["alerts"])
logger = structlog.get_logger(__name__)


@router.get("/rules")
async def list_alert_rules(
    page: int = Query(1, ge=1, description="Page number starting from 1"),
    limit: int = Query(50, ge=1, le=100, description="Number of rules per page"),
    active_only: Optional[bool] = Query(None, description="Filter by active status"),
    priority: Optional[str] = Query(None, description="Filter by priority level"),
    search: Optional[str] = Query(None, description="Search in rule name or description")
):
    """
    List alert rules - REDESIGNED to use Core Data Service API
    """
    try:
        # Get Core Data Service client
        client = await get_core_data_client()
        
        # Get alert rules from Core Data Service
        alert_rules = await client.get_alert_rules()
        
        await logger.ainfo(
            "Retrieved alert rules from Core Data Service",
            total_rules=len(alert_rules),
            page=page,
            limit=limit
        )
        
        # Apply filters
        filtered_rules = alert_rules
        
        if active_only is not None:
            filtered_rules = [rule for rule in filtered_rules if rule.get("is_active") == active_only]
        
        if priority:
            filtered_rules = [rule for rule in filtered_rules if rule.get("priority") == priority]
        
        if search:
            search_lower = search.lower()
            filtered_rules = [
                rule for rule in filtered_rules 
                if search_lower in rule.get("rule_name", "").lower() or 
                   search_lower in rule.get("description", "").lower()
            ]
        
        # Apply pagination
        total = len(filtered_rules)
        start_idx = (page - 1) * limit
        end_idx = start_idx + limit
        paginated_rules = filtered_rules[start_idx:end_idx]
        
        return {
            "rules": paginated_rules,
            "total": total,
            "page": page,
            "limit": limit,
            "pages": (total + limit - 1) // limit if total > 0 else 0
        }
        
    except CoreDataServiceError as e:
        await logger.aerror(
            "Core Data Service error while listing alert rules",
            error=str(e),
            status_code=e.status_code
        )
        raise HTTPException(
            status_code=e.status_code or 503,
            detail={
                "error": "core_data_service_error",
                "message": f"Failed to retrieve alert rules from Core Data Service: {e.message}",
                "details": e.details
            }
        )
    except Exception as e:
        await logger.aerror("Failed to list alert rules", error=str(e))
        raise HTTPException(
            status_code=500,
            detail={
                "error": "service_error",
                "message": "Failed to retrieve alert rules",
                "details": {"reason": str(e)}
            }
        )


@router.post("/rules", status_code=201)
async def create_alert_rule(rule_data: SimpleAlertRuleCreate):
    """
    Create alert rule - REDESIGNED to use Core Data Service API
    """
    try:
        # Rule 3: Error-First Development - Validate priority values
        valid_priorities = ["low", "medium", "high"]
        if rule_data.priority not in valid_priorities:
            raise HTTPException(
                status_code=400,
                detail={
                    "error": "validation_error",
                    "message": f"Priority must be one of: {', '.join(valid_priorities)}"
                }
            )
        
        # Validate trigger_conditions is not empty
        if not rule_data.trigger_conditions:
            raise HTTPException(
                status_code=400,
                detail={
                    "error": "validation_error",
                    "message": "trigger_conditions cannot be empty"
                }
            )
        
        # Get Core Data Service client
        client = await get_core_data_client()
        
        # Create alert rule via Core Data Service
        rule_dict = rule_data.model_dump()
        result = await client.create_alert_rule(rule_dict)
        
        await logger.ainfo(
            "Alert rule created via Core Data Service",
            rule_id=result.get("id"),
            rule_name=rule_data.rule_name,
            priority=rule_data.priority
        )
        
        return result
        
    except CoreDataServiceError as e:
        await logger.aerror(
            "Core Data Service error while creating alert rule",
            error=str(e),
            status_code=e.status_code,
            rule_name=rule_data.rule_name
        )
        
        # Handle specific error codes
        if e.status_code == 409:
            raise HTTPException(
                status_code=409,
                detail={
                    "error": "rule_name_exists",
                    "message": f"Alert rule '{rule_data.rule_name}' already exists"
                }
            )
        
        raise HTTPException(
            status_code=e.status_code or 503,
            detail={
                "error": "core_data_service_error",
                "message": f"Failed to create alert rule via Core Data Service: {e.message}",
                "details": e.details
            }
        )
    except HTTPException:
        raise
    except Exception as e:
        await logger.aerror("Failed to create alert rule", error=str(e))
        raise HTTPException(
            status_code=500,
            detail={
                "error": "creation_failed",
                "message": "Failed to create alert rule",
                "details": {"reason": str(e)}
            }
        )


@router.get("/rules/{rule_id}")
async def get_alert_rule(rule_id: str):
    """
    Get alert rule by ID - REDESIGNED to use Core Data Service API
    """
    try:
        # Rule 3: Error-First Development - Validate UUID format
        try:
            UUID(rule_id)  # This will raise ValueError if invalid UUID
        except (ValueError, TypeError):
            raise HTTPException(
                status_code=404,
                detail={
                    "error": "rule_not_found",
                    "message": f"Alert rule with ID {rule_id} not found"
                }
            )
        
        # Get Core Data Service client
        client = await get_core_data_client()
        
        # Get alert rule from Core Data Service
        result = await client.get_alert_rule(rule_id)
        
        await logger.ainfo(
            "Retrieved alert rule from Core Data Service",
            rule_id=rule_id,
            rule_name=result.get("rule_name")
        )
        
        return result
        
    except CoreDataServiceError as e:
        await logger.aerror(
            "Core Data Service error while getting alert rule",
            error=str(e),
            status_code=e.status_code,
            rule_id=rule_id
        )
        
        # Handle 404 specifically
        if e.status_code == 404:
            raise HTTPException(
                status_code=404,
                detail={
                    "error": "rule_not_found",
                    "message": f"Alert rule with ID {rule_id} not found"
                }
            )
        
        raise HTTPException(
            status_code=e.status_code or 503,
            detail={
                "error": "core_data_service_error",
                "message": f"Failed to retrieve alert rule from Core Data Service: {e.message}",
                "details": e.details
            }
        )
    except HTTPException:
        raise
    except Exception as e:
        await logger.aerror("Failed to get alert rule", rule_id=rule_id, error=str(e))
        raise HTTPException(
            status_code=500,
            detail={
                "error": "service_error",
                "message": "Failed to retrieve alert rule",
                "details": {"rule_id": rule_id, "reason": str(e)}
            }
        )


@router.put("/rules/{rule_id}")
async def update_alert_rule(rule_id: str, rule_updates: Dict[str, Any]):
    """
    Update alert rule - REDESIGNED to use Core Data Service API
    """
    try:
        # Rule 3: Error-First Development - Validate priority if provided
        if "priority" in rule_updates:
            valid_priorities = ["low", "medium", "high"]
            if rule_updates["priority"] not in valid_priorities:
                raise HTTPException(
                    status_code=400,
                    detail={
                        "error": "validation_error",
                        "message": f"Priority must be one of: {', '.join(valid_priorities)}"
                    }
                )
        
        # Validate trigger_conditions if provided
        if "trigger_conditions" in rule_updates and not rule_updates["trigger_conditions"]:
            raise HTTPException(
                status_code=400,
                detail={
                    "error": "validation_error",
                    "message": "trigger_conditions cannot be empty"
                }
            )
        
        # Get Core Data Service client
        client = await get_core_data_client()
        
        # Update alert rule via Core Data Service
        result = await client.update_alert_rule(rule_id, rule_updates)
        
        await logger.ainfo(
            "Alert rule updated via Core Data Service",
            rule_id=rule_id,
            updated_fields=list(rule_updates.keys())
        )
        
        return result
        
    except CoreDataServiceError as e:
        await logger.aerror(
            "Core Data Service error while updating alert rule",
            error=str(e),
            status_code=e.status_code,
            rule_id=rule_id
        )
        
        # Handle 404 specifically
        if e.status_code == 404:
            raise HTTPException(
                status_code=404,
                detail={
                    "error": "rule_not_found",
                    "message": f"Alert rule with ID {rule_id} not found"
                }
            )
        
        raise HTTPException(
            status_code=e.status_code or 503,
            detail={
                "error": "core_data_service_error",
                "message": f"Failed to update alert rule via Core Data Service: {e.message}",
                "details": e.details
            }
        )
    except HTTPException:
        raise
    except Exception as e:
        await logger.aerror("Failed to update alert rule", rule_id=rule_id, error=str(e))
        raise HTTPException(
            status_code=500,
            detail={
                "error": "update_failed",
                "message": "Failed to update alert rule",
                "details": {"rule_id": rule_id, "reason": str(e)}
            }
        )


@router.delete("/rules/{rule_id}")
async def delete_alert_rule(
    rule_id: str,
    force: bool = Query(False, description="Force delete even if there are active instances")
):
    """
    Delete alert rule - REDESIGNED to use Core Data Service API
    """
    try:
        # Get Core Data Service client
        client = await get_core_data_client()
        
        # Delete alert rule via Core Data Service
        await client.delete_alert_rule(rule_id)
        
        await logger.ainfo(
            "Alert rule deleted via Core Data Service",
            rule_id=rule_id,
            force_delete=force
        )
        
        return {"message": "Alert rule deleted successfully", "rule_id": rule_id}
        
    except CoreDataServiceError as e:
        await logger.aerror(
            "Core Data Service error while deleting alert rule",
            error=str(e),
            status_code=e.status_code,
            rule_id=rule_id
        )
        
        # Handle specific error codes
        if e.status_code == 404:
            raise HTTPException(
                status_code=404,
                detail={
                    "error": "rule_not_found",
                    "message": f"Alert rule with ID {rule_id} not found"
                }
            )
        elif e.status_code == 409:
            raise HTTPException(
                status_code=409,
                detail={
                    "error": "rule_has_active_instances",
                    "message": "Cannot delete rule with active instances. Use force=true to override."
                }
            )
        
        raise HTTPException(
            status_code=e.status_code or 503,
            detail={
                "error": "core_data_service_error",
                "message": f"Failed to delete alert rule via Core Data Service: {e.message}",
                "details": e.details
            }
        )
    except Exception as e:
        await logger.aerror("Failed to delete alert rule", rule_id=rule_id, error=str(e))
        raise HTTPException(
            status_code=500,
            detail={
                "error": "deletion_failed",
                "message": "Failed to delete alert rule",
                "details": {"rule_id": rule_id, "reason": str(e)}
            }
        )


@router.get("/history")
async def get_alert_history(
    page: int = Query(1, ge=1, description="Page number starting from 1"),
    limit: int = Query(50, ge=1, le=100, description="Number of items per page"),
    status: Optional[str] = Query(None, description="Filter by alert status"),
    priority: Optional[str] = Query(None, description="Filter by priority level"),
    rule_id: Optional[str] = Query(None, description="Filter by alert rule ID"),
    person_id: Optional[str] = Query(None, description="Filter by person ID"),
    from_date: Optional[datetime] = Query(None, description="Filter alerts from this date"),
    to_date: Optional[datetime] = Query(None, description="Filter alerts until this date")
):
    """
    Get alert history - REDESIGNED to use Core Data Service API
    """
    try:
        # Get Core Data Service client
        client = await get_core_data_client()
        
        # Build filters for Core Data Service
        filters = {}
        if status:
            filters["status"] = status
        if priority:
            filters["priority"] = priority
        if rule_id:
            filters["rule_id"] = rule_id
        if person_id:
            filters["person_id"] = person_id
        if from_date:
            filters["from_date"] = from_date.isoformat()
        if to_date:
            filters["to_date"] = to_date.isoformat()
        
        # Get alert history from Core Data Service
        result = await client.get_alert_history(page=page, limit=limit, **filters)
        
        await logger.ainfo(
            "Retrieved alert history from Core Data Service",
            page=page,
            limit=limit,
            total=result.get("total", 0),
            filters=filters
        )
        
        return result
        
    except CoreDataServiceError as e:
        await logger.aerror(
            "Core Data Service error while getting alert history",
            error=str(e),
            status_code=e.status_code
        )
        raise HTTPException(
            status_code=e.status_code or 503,
            detail={
                "error": "core_data_service_error",
                "message": f"Failed to retrieve alert history from Core Data Service: {e.message}",
                "details": e.details
            }
        )
    except Exception as e:
        await logger.aerror("Failed to get alert history", error=str(e))
        raise HTTPException(
            status_code=500,
            detail={
                "error": "service_error",
                "message": "Failed to retrieve alert history",
                "details": {"reason": str(e)}
            }
        )


@router.post("/acknowledge/{alert_id}")
async def acknowledge_alert(alert_id: str):
    """
    Acknowledge alert - REDESIGNED to use Core Data Service API
    """
    try:
        # Rule 3: Error-First Development - Validate UUID format
        try:
            UUID(alert_id)  # This will raise ValueError if invalid UUID
        except (ValueError, TypeError):
            raise HTTPException(
                status_code=404,
                detail={
                    "error": "alert_not_found",
                    "message": f"Alert with ID {alert_id} not found"
                }
            )
        
        # Get Core Data Service client
        client = await get_core_data_client()
        
        # Acknowledge alert via Core Data Service
        result = await client.acknowledge_alert(alert_id)
        
        await logger.ainfo(
            "Alert acknowledged via Core Data Service",
            alert_id=alert_id
        )
        
        return result
        
    except CoreDataServiceError as e:
        await logger.aerror(
            "Core Data Service error while acknowledging alert",
            error=str(e),
            status_code=e.status_code,
            alert_id=alert_id
        )
        
        # Handle 404 specifically
        if e.status_code == 404:
            raise HTTPException(
                status_code=404,
                detail={
                    "error": "alert_not_found",
                    "message": f"Alert with ID {alert_id} not found"
                }
            )
        
        raise HTTPException(
            status_code=e.status_code or 503,
            detail={
                "error": "core_data_service_error",
                "message": f"Failed to acknowledge alert via Core Data Service: {e.message}",
                "details": e.details
            }
        )
    except HTTPException:
        raise
    except Exception as e:
        await logger.aerror("Failed to acknowledge alert", alert_id=alert_id, error=str(e))
        raise HTTPException(
            status_code=500,
            detail={
                "error": "acknowledgment_failed",
                "message": "Failed to acknowledge alert",
                "details": {"alert_id": alert_id, "reason": str(e)}
            }
        )