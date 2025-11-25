"""Authentication routes."""
from fastapi import APIRouter, Depends, HTTPException, status
from app.utils.auth import verify_token, get_current_user
from app.utils.database import get_supabase
from app.utils.email import send_confirmation_email, send_welcome_email
from pydantic import BaseModel
from typing import Optional
import logging
import secrets
import hashlib
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

router = APIRouter()

# In-memory store for confirmation tokens (use Redis in production)
confirmation_tokens = {}


class RegisterRequest(BaseModel):
    email: str
    password: str
    full_name: Optional[str] = None
    age: Optional[int] = None
    gender: Optional[str] = None


class LoginRequest(BaseModel):
    email: str
    password: str


class AuthResponse(BaseModel):
    access_token: str
    token_type: str
    user: dict


class VerifyTokenResponse(BaseModel):
    valid: bool
    user_id: str
    email: str


@router.post("/register", response_model=AuthResponse)
async def register(data: RegisterRequest):
    """Register a new user with improved error handling."""
    logger.info(f"📝 Registration request received for: {data.email}")
    
    supabase_client = get_supabase()
    supabase_admin = get_supabase(use_service_role=True)
    
    try:
        # Check if user already exists first
        try:
            existing = supabase_admin.table("profiles").select("id").eq("email", data.email).execute()
            if existing.data and len(existing.data) > 0:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Email already registered. Please use Sign In."
                )
        except HTTPException:
            raise
        except Exception as check_error:
            logger.debug(f"Profile check error (expected if new): {check_error}")
        
        # Create user with admin API
        logger.info(f"Creating user via admin API: {data.email}")
        admin_user_result = supabase_admin.auth.admin.create_user({
            "email": data.email,
            "password": data.password,
            "email_confirm": True,  # Auto-confirm for now
            "user_metadata": {
                "full_name": data.full_name or "",
                "age": data.age,
                "gender": data.gender,
            }
        })
        
        if not admin_user_result or not admin_user_result.user:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create user account"
            )
        
        user_id = str(admin_user_result.user.id)
        logger.info(f"✅ User created: {data.email} (ID: {user_id})")
        
        # Create profile with retry logic
        profile_data = {
            "id": user_id,
            "email": data.email,
            "full_name": data.full_name or "",
            "created_at": datetime.utcnow().isoformat()
        }
        
        if data.age:
            profile_data["age"] = data.age
        if data.gender:
            profile_data["gender"] = data.gender
        
        max_retries = 3
        for attempt in range(max_retries):
            try:
                result = supabase_admin.table("profiles").insert(profile_data).execute()
                if result.data and len(result.data) > 0:
                    logger.info(f"✅ Profile created: {data.email}")
                    break
            except Exception as profile_error:
                if attempt == max_retries - 1:
                    logger.error(f"❌ Profile creation failed after {max_retries} attempts: {profile_error}")
                else:
                    logger.warning(f"Profile creation attempt {attempt + 1} failed, retrying...")
                    import time
                    time.sleep(0.5)
        
        # Sign in the user
        logger.info(f"Signing in user: {data.email}")
        try:
            sign_in_result = supabase_client.auth.sign_in_with_password({
                "email": data.email,
                "password": data.password
            })
            
            if not sign_in_result.session:
                raise HTTPException(
                    status_code=status.HTTP_201_CREATED,
                    detail="Account created successfully! Please sign in."
                )
            
            logger.info(f"✅ Registration complete: {data.email}")
            return AuthResponse(
                access_token=sign_in_result.session.access_token,
                token_type="bearer",
                user={
                    "id": user_id,
                    "email": data.email,
                    "full_name": data.full_name,
                    "created_at": str(admin_user_result.user.created_at) if hasattr(admin_user_result.user, 'created_at') else "",
                }
            )
        except HTTPException:
            raise
        except Exception as login_error:
            logger.error(f"Auto-login failed: {login_error}")
            raise HTTPException(
                status_code=status.HTTP_201_CREATED,
                detail="Account created successfully! Please sign in."
            )
            
    except HTTPException:
        raise
    except Exception as e:
        error_msg = str(e).lower()
        logger.error(f"❌ Registration error: {e}", exc_info=True)
        
        if "already" in error_msg or "duplicate" in error_msg or "exists" in error_msg or "unique" in error_msg:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered. Please use Sign In."
            )
        
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Registration failed. Please try again or contact support."
        )


@router.get("/confirm")
async def confirm_email(token: str):
    """Confirm user email via token."""
    try:
        # Hash the token
        token_hash = hashlib.sha256(token.encode()).hexdigest()
        
        # Check if token exists
        if token_hash not in confirmation_tokens:
            return {
                "success": False,
                "message": "Invalid or expired confirmation link. Please sign up again."
            }
        
        # Get user data
        user_data = confirmation_tokens[token_hash]
        
        # Check if token expired
        if datetime.now() > user_data["expires"]:
            del confirmation_tokens[token_hash]
            return {
                "success": False,
                "message": "Confirmation link has expired. Please sign up again."
            }
        
        # Confirm user using service role
        supabase_admin = get_supabase(use_service_role=True)
        
        try:
            # Update user to confirm email
            update_result = supabase_admin.auth.admin.update_user_by_id(
                user_data["user_id"],
                {"email_confirm": True}
            )
            
            logger.info(f"User email confirmed via link: {user_data['email']}")
            
            # Send welcome email
            send_welcome_email(
                to_email=user_data["email"],
                full_name=user_data.get("full_name")
            )
            
            # Clean up token
            del confirmation_tokens[token_hash]
            
            # Return HTML page with redirect
            html_content = """
            <!DOCTYPE html>
            <html>
            <head>
                <title>Email Confirmed - Nirvami</title>
                <style>
                    body {
                        font-family: Arial, sans-serif;
                        display: flex;
                        justify-content: center;
                        align-items: center;
                        min-height: 100vh;
                        margin: 0;
                        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    }
                    .container {
                        background: white;
                        padding: 40px;
                        border-radius: 10px;
                        box-shadow: 0 10px 40px rgba(0,0,0,0.2);
                        text-align: center;
                        max-width: 500px;
                    }
                    h1 {
                        color: #667eea;
                        margin-bottom: 20px;
                    }
                    p {
                        color: #666;
                        line-height: 1.6;
                        margin-bottom: 30px;
                    }
                    .checkmark {
                        font-size: 80px;
                        color: #4CAF50;
                        margin-bottom: 20px;
                    }
                    .button {
                        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                        color: white;
                        padding: 15px 40px;
                        text-decoration: none;
                        border-radius: 5px;
                        font-size: 16px;
                        display: inline-block;
                        margin-top: 20px;
                    }
                </style>
                <script>
                    setTimeout(() => {
                        window.location.href = 'http://localhost:3000/login';
                    }, 3000);
                </script>
            </head>
            <body>
                <div class="container">
                    <div class="checkmark">✓</div>
                    <h1>Email Confirmed!</h1>
                    <p>Your account has been successfully verified. You can now sign in to Nirvami.</p>
                    <p style="font-size: 14px; color: #999;">Redirecting to login page in 3 seconds...</p>
                    <a href="http://localhost:3000/login" class="button">Go to Sign In</a>
                </div>
            </body>
            </html>
            """
            
            from fastapi.responses import HTMLResponse
            return HTMLResponse(content=html_content)
            
        except Exception as confirm_error:
            logger.error(f"Failed to confirm user: {confirm_error}")
            return {
                "success": False,
                "message": "Failed to confirm email. Please try again or contact support."
            }
        
    except Exception as e:
        logger.error(f"Confirmation error: {e}")
        return {
            "success": False,
            "message": "An error occurred. Please try again."
        }


@router.post("/login", response_model=AuthResponse)
async def login(data: LoginRequest):
    """Login user."""
    import time
    start_time = time.time()
    
    supabase = get_supabase()
    
    try:
        response = supabase.auth.sign_in_with_password({
            "email": data.email,
            "password": data.password
        })
        
        auth_time = time.time() - start_time
        logger.info(f"⏱️ Login auth took {auth_time:.2f}s")
        
        if not response.session:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid credentials"
            )
        
        # Fetch profile in parallel (don't block response)
        profile_start = time.time()
        try:
            profile_result = supabase.table("profiles").select("full_name").eq("id", response.user.id).single().execute()
            full_name = profile_result.data.get("full_name") if profile_result.data else None
            profile_time = time.time() - profile_start
            logger.info(f"⏱️ Profile fetch took {profile_time:.2f}s")
        except Exception as profile_error:
            logger.warning(f"Could not fetch profile: {profile_error}")
            full_name = None
        
        total_time = time.time() - start_time
        logger.info(f"⏱️ Total login time: {total_time:.2f}s")
        
        return AuthResponse(
            access_token=response.session.access_token,
            token_type="bearer",
            user={
                "id": response.user.id,
                "email": response.user.email,
                "full_name": full_name,
                "created_at": str(response.user.created_at),
            }
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Login error: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )


@router.post("/verify", response_model=VerifyTokenResponse)
async def verify_jwt_token(current_user: dict = Depends(get_current_user)):
    """Verify Supabase JWT token."""
    return VerifyTokenResponse(
        valid=True,
        user_id=current_user["user_id"],
        email=current_user.get("email", "")
    )


@router.get("/me")
async def get_current_user_info(current_user: dict = Depends(get_current_user)):
    """Get current user information."""
    supabase = get_supabase(use_service_role=True)
    
    try:
        result = supabase.table("profiles").select("*").eq("id", current_user["user_id"]).single().execute()
        return result.data
    except Exception as e:
        logger.error(f"Error fetching user profile: {e}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User profile not found"
        )


@router.get("/user")
async def get_user(current_user: dict = Depends(get_current_user)):
    """Get current user information (alias for /me)."""
    return await get_current_user_info(current_user)
