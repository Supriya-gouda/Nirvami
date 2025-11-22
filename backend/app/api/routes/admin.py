"""Admin dashboard routes."""
from fastapi import APIRouter, Depends
from app.utils.auth import require_admin
import logging

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/users")
async def get_all_users(
    admin: dict = Depends(require_admin)
):
    """Get all users (admin only)."""
    # Implementation here
    pass


@router.get("/analytics")
async def get_system_analytics(
    admin: dict = Depends(require_admin)
):
    """Get system-wide analytics."""
    # Implementation here
    pass
