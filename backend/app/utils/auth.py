"""Authentication utilities and dependencies."""
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt, JWTError
from app.config import settings
from app.utils.database import get_supabase
from typing import Optional, Dict
import logging

logger = logging.getLogger(__name__)

security = HTTPBearer(auto_error=False)  # Don't auto-raise errors


async def get_optional_token(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)
) -> Optional[Dict]:
    """Get token info if provided, otherwise return None."""
    if not credentials:
        return None
    
    token = credentials.credentials
    
    try:
        # Use Supabase to verify the token
        supabase = get_supabase()
        user_response = supabase.auth.get_user(token)
        
        if user_response and user_response.user:
            return {
                "user_id": user_response.user.id,
                "email": user_response.user.email,
                "role": user_response.user.role if hasattr(user_response.user, 'role') else "user",
                "user": user_response.user
            }
        
        return None
        
    except Exception as e:
        logger.warning(f"Invalid token: {e}")
        return None


async def verify_token(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> Dict:
    """
    Verify Supabase JWT token and extract user info.
    
    Returns:
        Dict with user_id and other claims
    """
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated"
        )
    
    token = credentials.credentials
    
    try:
        # Use Supabase to verify the token
        supabase = get_supabase()
        user_response = supabase.auth.get_user(token)
        
        if not user_response or not user_response.user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials"
            )
        
        return {
            "user_id": user_response.user.id,
            "email": user_response.user.email,
            "role": user_response.user.role if hasattr(user_response.user, 'role') else "user",
            "user": user_response.user
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"JWT verification failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials"
        )


async def get_current_user(
    auth_data: Dict = Depends(verify_token)
) -> Dict:
    """Get current authenticated user."""
    return auth_data


async def get_current_user_id(
    auth_data: Optional[Dict] = Depends(get_optional_token)
) -> str:
    """
    Get current user ID. For testing, returns a default user ID if not authenticated.
    """
    if auth_data and auth_data.get("user_id"):
        return auth_data["user_id"]
    
    # For development/testing - use a valid UUID format test user
    logger.warning("No authentication provided, using test user")
    return "00000000-0000-0000-0000-000000000000"


async def require_admin(
    auth_data: Dict = Depends(verify_token)
) -> Dict:
    """Require admin role."""
    if auth_data.get("role") != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    return auth_data


async def verify_supabase_jwt(token: str) -> Optional[Dict]:
    """
    Verify Supabase JWT using Supabase client.
    Alternative method using Supabase SDK.
    """
    try:
        supabase = get_supabase()
        user = supabase.auth.get_user(token)
        if user:
            return {
                "user_id": user.user.id,
                "email": user.user.email,
                "user": user.user
            }
        return None
    except Exception as e:
        logger.error(f"Supabase JWT verification failed: {e}")
        return None
