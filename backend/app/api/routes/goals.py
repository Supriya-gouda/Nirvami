"""Goals routes."""
import logging
from fastapi import APIRouter, Depends, HTTPException
from datetime import date, datetime
from typing import List, Optional
from pydantic import BaseModel
from app.utils.auth import get_current_user_id
from app.utils.database import get_supabase

logger = logging.getLogger(__name__)

router = APIRouter()
# Prefix set in main.py: /api/v1/goals


# Schemas
class GoalCreate(BaseModel):
    """Schema for creating a goal."""
    title: str
    description: Optional[str] = None
    target_date: Optional[str] = None  # ISO date format


class GoalUpdate(BaseModel):
    """Schema for updating a goal."""
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None  # 'active', 'completed', 'archived'
    completion_percent: Optional[int] = None
    target_date: Optional[str] = None
    is_completed: Optional[bool] = None


class GoalResponse(BaseModel):
    """Schema for goal response."""
    id: str
    user_id: str
    title: str
    description: Optional[str]
    status: str
    completion_percent: int
    target_date: Optional[str]
    is_completed: bool
    created_at: str
    completed_at: Optional[str]


@router.post("", response_model=GoalResponse)
async def create_goal(
    goal: GoalCreate,
    current_user_id: str = Depends(get_current_user_id),
):
    """Create a new goal."""
    supabase = get_supabase()
    
    try:
        # Validate target_date if provided
        target_date_value = None
        if goal.target_date:
            try:
                target_date_value = date.fromisoformat(goal.target_date).isoformat()
            except ValueError:
                raise HTTPException(status_code=400, detail="Invalid target_date format. Use YYYY-MM-DD")
        
        # Create goal
        result = supabase.table("goals").insert({
            "user_id": current_user_id,
            "title": goal.title,
            "description": goal.description,
            "target_date": target_date_value,
            "status": "active",
            "completion_percent": 0,
            "is_completed": False,
        }).execute()
        
        if not result.data:
            raise HTTPException(status_code=500, detail="Failed to create goal")
        
        logger.info(f"Goal created for user {current_user_id}: {goal.title}")
        return result.data[0]
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating goal: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("", response_model=List[GoalResponse])
async def get_goals(
    current_user_id: str = Depends(get_current_user_id),
    status: Optional[str] = None,
):
    """Get goals for the current user."""
    supabase = get_supabase()
    
    try:
        query = supabase.table("goals").select("*").eq("user_id", current_user_id)
        
        # Filter by status if provided
        if status:
            if status not in ['active', 'completed', 'archived']:
                raise HTTPException(status_code=400, detail="Invalid status. Use: active, completed, or archived")
            query = query.eq("status", status)
        
        result = query.order("created_at", desc=True).execute()
        
        return result.data if result.data else []
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching goals: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{goal_id}", response_model=GoalResponse)
async def get_goal(
    goal_id: str,
    current_user_id: str = Depends(get_current_user_id),
):
    """Get a specific goal."""
    supabase = get_supabase()
    
    try:
        result = (
            supabase.table("goals")
            .select("*")
            .eq("id", goal_id)
            .eq("user_id", current_user_id)
            .execute()
        )
        
        if not result.data or len(result.data) == 0:
            raise HTTPException(status_code=404, detail="Goal not found")
        
        return result.data[0]
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching goal: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/{goal_id}", response_model=GoalResponse)
async def update_goal(
    goal_id: str,
    goal_update: GoalUpdate,
    current_user_id: str = Depends(get_current_user_id),
):
    """Update a goal."""
    supabase = get_supabase()
    
    try:
        # Verify goal exists and belongs to user
        existing = (
            supabase.table("goals")
            .select("*")
            .eq("id", goal_id)
            .eq("user_id", current_user_id)
            .execute()
        )
        
        if not existing.data or len(existing.data) == 0:
            raise HTTPException(status_code=404, detail="Goal not found")
        
        # Prepare update data
        update_data = {}
        if goal_update.title is not None:
            update_data["title"] = goal_update.title
        if goal_update.description is not None:
            update_data["description"] = goal_update.description
        if goal_update.status is not None:
            if goal_update.status not in ['active', 'completed', 'archived']:
                raise HTTPException(status_code=400, detail="Invalid status")
            update_data["status"] = goal_update.status
            
            # Auto-set completion fields if status is completed
            if goal_update.status == 'completed':
                update_data["is_completed"] = True
                update_data["completion_percent"] = 100
                update_data["completed_at"] = datetime.now().isoformat()
        
        if goal_update.completion_percent is not None:
            if not (0 <= goal_update.completion_percent <= 100):
                raise HTTPException(status_code=400, detail="Completion percent must be between 0 and 100")
            update_data["completion_percent"] = goal_update.completion_percent
            
            # Auto-complete if 100%
            if goal_update.completion_percent == 100:
                update_data["is_completed"] = True
                update_data["status"] = "completed"
                update_data["completed_at"] = datetime.now().isoformat()
        
        if goal_update.target_date is not None:
            try:
                update_data["target_date"] = date.fromisoformat(goal_update.target_date).isoformat()
            except ValueError:
                raise HTTPException(status_code=400, detail="Invalid target_date format")
        
        if goal_update.is_completed is not None:
            update_data["is_completed"] = goal_update.is_completed
            if goal_update.is_completed:
                update_data["status"] = "completed"
                update_data["completion_percent"] = 100
                update_data["completed_at"] = datetime.now().isoformat()
        
        if not update_data:
            raise HTTPException(status_code=400, detail="No fields to update")
        
        # Update goal
        result = (
            supabase.table("goals")
            .update(update_data)
            .eq("id", goal_id)
            .eq("user_id", current_user_id)
            .execute()
        )
        
        if not result.data:
            raise HTTPException(status_code=500, detail="Failed to update goal")
        
        logger.info(f"Goal {goal_id} updated by user {current_user_id}")
        return result.data[0]
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating goal: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{goal_id}")
async def delete_goal(
    goal_id: str,
    current_user_id: str = Depends(get_current_user_id),
):
    """Delete a goal."""
    supabase = get_supabase()
    
    try:
        # Verify goal exists and belongs to user
        existing = (
            supabase.table("goals")
            .select("id")
            .eq("id", goal_id)
            .eq("user_id", current_user_id)
            .execute()
        )
        
        if not existing.data or len(existing.data) == 0:
            raise HTTPException(status_code=404, detail="Goal not found")
        
        # Delete goal
        supabase.table("goals").delete().eq("id", goal_id).eq("user_id", current_user_id).execute()
        
        logger.info(f"Goal {goal_id} deleted by user {current_user_id}")
        return {"message": "Goal deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting goal: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{goal_id}/complete", response_model=GoalResponse)
async def complete_goal(
    goal_id: str,
    current_user_id: str = Depends(get_current_user_id),
):
    """Mark a goal as completed."""
    supabase = get_supabase()
    
    try:
        # Verify goal exists
        existing = (
            supabase.table("goals")
            .select("*")
            .eq("id", goal_id)
            .eq("user_id", current_user_id)
            .execute()
        )
        
        if not existing.data or len(existing.data) == 0:
            raise HTTPException(status_code=404, detail="Goal not found")
        
        # Update to completed
        result = (
            supabase.table("goals")
            .update({
                "status": "completed",
                "is_completed": True,
                "completion_percent": 100,
                "completed_at": datetime.now().isoformat(),
            })
            .eq("id", goal_id)
            .eq("user_id", current_user_id)
            .execute()
        )
        
        if not result.data:
            raise HTTPException(status_code=500, detail="Failed to complete goal")
        
        logger.info(f"Goal {goal_id} marked as completed by user {current_user_id}")
        return result.data[0]
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error completing goal: {e}")
        raise HTTPException(status_code=500, detail=str(e))
