"""Main FastAPI application for Nirvami backend."""
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import logging
import os

from app.config import settings
from app.api.routes import (
    auth,
    chat,
    emotions,
    aura,
    wellness,
    dosha,
    meals,
    wearable,
    watch,
    analytics,
    alerts,
    admin,
    profile,
    yoga,
    routines,
    journal,
    goals,
    dinacharya,
    recommendations  # New unified recommendation routes
)
from app.api.routes import wearable_v2  # New simplified wearable routes
from app.ml.model_manager import ModelManager
from app.services.gemini_chatbot import get_chatbot

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifespan events."""
    # Startup
    logger.info("Starting Nirvami Backend...")
    
    # Debug: Print DB Config
    try:
        db_host = settings.DATABASE_URL.split('@')[-1].split('/')[0]
        logger.info(f"🔌 DB URL host: {db_host}")
        logger.info(f"🧪 USE_MOCK_DATA: {settings.USE_MOCK_DATA}")
    except Exception as e:
        logger.error(f"Could not parse DATABASE_URL: {e}")
    
    # Initialize Gemini chatbot
    try:
        chatbot = get_chatbot()
        if chatbot.is_available():
            logger.info("✅ Gemini chatbot ready")
        else:
            logger.warning("⚠️  Gemini chatbot not available")
    except Exception as e:
        logger.error(f"❌ Error initializing chatbot: {e}")
    
    try:
        # Initialize ML models if enabled
        enable_ml = settings.ENABLE_ML_MODELS
        
        if enable_ml:
            logger.info("🔄 Loading ML models...")
            model_manager = ModelManager()
            await model_manager.load_models()
            app.state.model_manager = model_manager
            logger.info("✅ ML models loaded successfully")
        else:
            logger.info("⚠️  ML models disabled - using rule-based fallbacks")
            app.state.model_manager = None
    except Exception as e:
        logger.error(f"❌ Error loading ML models: {e}", exc_info=True)
        app.state.model_manager = None
        logger.warning("⚠️  Continuing without ML models - using fallback responses")
    
    yield
    
    # Shutdown
    logger.info("Shutting down Nirvami Backend...")


# Create FastAPI app
app = FastAPI(
    title="Nirvami API",
    description="AI-powered mental wellness platform with Ayurvedic intelligence",
    version="1.0.0",
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins in development (includes null origin for file://)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Handle unexpected exceptions."""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error occurred"}
    )

# Health check
@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "version": "1.0.0",
        "environment": settings.ENVIRONMENT
    }

# Include routers
app.include_router(auth.router, prefix=f"/api/{settings.API_VERSION}/auth", tags=["Authentication"])
app.include_router(profile.router, prefix=f"/api/{settings.API_VERSION}/profile", tags=["Profile"])
app.include_router(chat.router, prefix=f"/api/{settings.API_VERSION}/chat", tags=["Chat"])
app.include_router(emotions.router, prefix=f"/api/{settings.API_VERSION}/emotions", tags=["Emotions"])
app.include_router(aura.router, prefix=f"/api/{settings.API_VERSION}/aura", tags=["Aura"])
app.include_router(wellness.router, prefix=f"/api/{settings.API_VERSION}/wellness", tags=["Wellness"])
app.include_router(journal.router, prefix=f"/api/{settings.API_VERSION}/journal", tags=["Journal"])
app.include_router(goals.router, prefix=f"/api/{settings.API_VERSION}/goals", tags=["Goals"])
app.include_router(dosha.router, prefix=f"/api/{settings.API_VERSION}/dosha", tags=["Dosha"])
app.include_router(yoga.router, prefix=f"/api/{settings.API_VERSION}/yoga", tags=["Yoga & Sound Therapy"])
app.include_router(recommendations.router, prefix=f"/api/{settings.API_VERSION}/recommendations", tags=["Recommendations"])  # New unified recommendations
app.include_router(meals.router, prefix=f"/api/{settings.API_VERSION}/meals", tags=["Meals"])
app.include_router(routines.router, prefix=f"/api/{settings.API_VERSION}/routines", tags=["Daily Routines"])
app.include_router(dinacharya.router, prefix=f"/api/{settings.API_VERSION}", tags=["Dinacharya"])
app.include_router(wearable.router, prefix=f"/api/{settings.API_VERSION}/wearable", tags=["Wearable"])
app.include_router(wearable_v2.router, prefix=f"/api/{settings.API_VERSION}/wearable-v2", tags=["Wearable V2"])  # New clean routes
app.include_router(watch.router, prefix=f"/api/{settings.API_VERSION}/watch", tags=["Watch"])
app.include_router(analytics.router, prefix=f"/api/{settings.API_VERSION}/analytics", tags=["Analytics"])
app.include_router(alerts.router, prefix=f"/api/{settings.API_VERSION}/alerts", tags=["Alerts"])
app.include_router(admin.router, prefix=f"/api/{settings.API_VERSION}/admin", tags=["Admin"])

# Temporary Debug Endpoint
from fastapi import Depends
from app.utils.auth import get_current_user_id
from app.utils.database import get_supabase
import uuid
from datetime import datetime

@app.post("/debug/db-test")
async def db_test(
    current_user_id: str = Depends(get_current_user_id),
    supabase = Depends(get_supabase)
):
    """Test database write capability."""
    try:
        logger.info(f"Attempting DB write for user: {current_user_id}")
        
        # Create a test audit log
        test_data = {
            "id": str(uuid.uuid4()),
            "user_id": current_user_id if current_user_id != "00000000-0000-0000-0000-000000000000" else None,
            "action": "debug_db_test",
            "entity_type": "debug",
            "entity_id": str(uuid.uuid4()),
            "old_values": {},
            "new_values": {"message": "Hello from backend DB test"},
            "ip_address": "127.0.0.1",
            "user_agent": "DebugClient",
            "created_at": datetime.now().isoformat()
        }
        
        # Write to audit_logs table
        result = supabase.table("audit_logs").insert(test_data).execute()
        
        logger.info(f"✅ DB Write Success: {result.data}")
        return {"ok": True, "data": result.data}
        
    except Exception as e:
        logger.error(f"❌ DB Write Failed: {e}")
        return {"ok": False, "error": str(e)}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.ENVIRONMENT == "development"
    )
