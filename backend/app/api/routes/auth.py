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
    """Register a new user and send confirmation email."""
    supabase_client = get_supabase()
    
    try:
        # First, try normal signup
        signup_result = supabase_client.auth.sign_up({
            "email": data.email,
            "password": data.password,
            "options": {
                "data": {
                    "full_name": data.full_name or "",
                    "age": data.age,
                    "gender": data.gender,
                }
            }
        })
        
        if signup_result.user is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to create user"
            )
        
        logger.info(f"User created: {signup_result.user.email}")
        
        # If we got a session, user is auto-confirmed (email confirmation disabled)
        if signup_result.session:
            logger.info(f"User auto-confirmed, returning session: {data.email}")
            return AuthResponse(
                access_token=signup_result.session.access_token,
                token_type="bearer",
                user={
                    "id": str(signup_result.user.id),
                    "email": signup_result.user.email,
                    "full_name": data.full_name,
                    "age": data.age,
                    "gender": data.gender,
                    "created_at": str(signup_result.user.created_at) if hasattr(signup_result.user, 'created_at') else "",
                }
            )
        
        # No session means email confirmation is required
        logger.info(f"Email confirmation required for: {data.email}")
        
        # Generate confirmation token
        token = secrets.token_urlsafe(32)
        token_hash = hashlib.sha256(token.encode()).hexdigest()
        
        # Store token with user info (expires in 24 hours)
        confirmation_tokens[token_hash] = {
            "user_id": str(signup_result.user.id),
            "email": data.email,
            "password": data.password,
            "full_name": data.full_name,
            "age": data.age,
            "gender": data.gender,
            "expires": datetime.now() + timedelta(hours=24)
        }
        
        # Generate confirmation URL
        confirmation_url = f"http://localhost:8000/api/v1/auth/confirm?token={token}"
        
        # Send confirmation email
        email_sent = send_confirmation_email(
            to_email=data.email,
            confirmation_url=confirmation_url,
            full_name=data.full_name
        )
        
        if email_sent:
            logger.info(f"Confirmation email sent to {data.email}")
            raise HTTPException(
                status_code=status.HTTP_201_CREATED,
                detail="Account created! Please check your email to confirm your account."
            )
        else:
            # Email not sent - SMTP not configured
            # Try to auto-confirm with service role
            logger.warning(f"Email not sent, attempting auto-confirmation: {data.email}")
            
            try:
                supabase_admin = get_supabase(use_service_role=True)
                
                # Update user to confirm email
                update_result = supabase_admin.auth.admin.update_user_by_id(
                    str(signup_result.user.id),
                    {"email_confirm": True}
                )
                
                logger.info(f"User email confirmed via service role: {data.email}")
                
                # Now try to sign in
                sign_in_result = supabase_client.auth.sign_in_with_password({
                    "email": data.email,
                    "password": data.password
                })
                
                if sign_in_result.session:
                    logger.info(f"User signed in successfully after auto-confirmation: {data.email}")
                    return AuthResponse(
                        access_token=sign_in_result.session.access_token,
                        token_type="bearer",
                        user={
                            "id": str(signup_result.user.id),
                            "email": signup_result.user.email,
                            "full_name": data.full_name,
                            "age": data.age,
                            "gender": data.gender,
                            "created_at": str(signup_result.user.created_at) if hasattr(signup_result.user, 'created_at') else "",
                        }
                    )
            except Exception as confirm_error:
                logger.error(f"Auto-confirmation failed: {confirm_error}")
            
            # If all else fails, user needs to sign in manually
            raise HTTPException(
                status_code=status.HTTP_201_CREATED,
                detail="Account created! SMTP not configured - please contact admin to confirm your email."
            )
        
    except HTTPException:
        raise
    except Exception as e:
        error_msg = str(e).lower()
        logger.error(f"Registration error: {e}")
        
        if "already" in error_msg or "duplicate" in error_msg or "exists" in error_msg:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered. Please use Sign In."
            )
        
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Registration failed: {str(e)}"
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
    supabase = get_supabase()
    
    try:
        response = supabase.auth.sign_in_with_password({
            "email": data.email,
            "password": data.password
        })
        
        if not response.session:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid credentials"
            )
        
        return AuthResponse(
            access_token=response.session.access_token,
            token_type="bearer",
            user={
                "id": response.user.id,
                "email": response.user.email,
                "created_at": str(response.user.created_at),
            }
        )
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
