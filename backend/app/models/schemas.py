"""Pydantic models for request/response schemas."""
from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List, Dict, Any
from datetime import datetime, date
from enum import Enum


# ============================================
# ENUMS
# ============================================

class DoshaType(str, Enum):
    VATA = "vata"
    PITTA = "pitta"
    KAPHA = "kapha"
    VATA_PITTA = "vata-pitta"
    PITTA_KAPHA = "pitta-kapha"
    VATA_KAPHA = "vata-kapha"
    TRIDOSHA = "tridosha"


class MessageRole(str, Enum):
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"


class MealType(str, Enum):
    BREAKFAST = "breakfast"
    LUNCH = "lunch"
    DINNER = "dinner"
    SNACK = "snack"


class AlertType(str, Enum):
    CRISIS = "crisis"
    WELLNESS_LOW = "wellness_low"
    REMINDER = "reminder"
    ACHIEVEMENT = "achievement"


class AlertSeverity(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


# ============================================
# USER & PROFILE
# ============================================

class UserProfile(BaseModel):
    id: str
    email: str
    full_name: Optional[str] = None
    avatar_url: Optional[str] = None
    dosha_type: Optional[DoshaType] = None
    role: str = "user"
    consent_data_collection: bool = False
    consent_ai_processing: bool = False
    consent_notifications: bool = True
    created_at: datetime
    updated_at: datetime


class UpdateProfileRequest(BaseModel):
    full_name: Optional[str] = None
    avatar_url: Optional[str] = None
    dosha_type: Optional[DoshaType] = None
    consent_data_collection: Optional[bool] = None
    consent_ai_processing: Optional[bool] = None
    consent_notifications: Optional[bool] = None


class UserPreferences(BaseModel):
    notification_email: bool = True
    notification_sms: bool = False
    notification_push: bool = True
    crisis_alerts_enabled: bool = True
    data_retention_days: int = 365
    preferences: Dict[str, Any] = {}


# ============================================
# CHAT & MESSAGES
# ============================================

class SendMessageRequest(BaseModel):
    session_id: Optional[str] = None
    content: str = Field(..., min_length=1)
    include_context: bool = True


class Message(BaseModel):
    id: str
    session_id: str
    user_id: str
    role: MessageRole
    content: str
    emotion_detected: Optional[str] = None
    emotion_scores: Optional[Dict[str, float]] = None
    crisis_flag: bool = False
    created_at: datetime


class ChatSession(BaseModel):
    id: str
    user_id: str
    title: Optional[str] = None
    started_at: datetime
    last_message_at: datetime
    messages: Optional[List[Message]] = None


class ChatResponse(BaseModel):
    """Response from chat endpoint."""
    message: Message
    response: str
    session_id: str
    crisis_detected: bool
    emotion_detected: str


# ============================================
# EMOTIONS
# ============================================

class EmotionDetectionResponse(BaseModel):
    dominant_emotion: str
    confidence: float
    all_scores: Dict[str, float]


class EmotionLog(BaseModel):
    id: str
    user_id: str
    emotion_type: str
    confidence: float
    all_scores: Dict[str, float]
    source: str = "text"
    created_at: datetime


class EmotionAggregate(BaseModel):
    date: date
    dominant_emotion: str
    emotion_distribution: Dict[str, float]
    average_valence: Optional[float] = None
    total_entries: int


# ============================================
# AURA
# ============================================

class AuraEntry(BaseModel):
    id: str
    user_id: str
    date: date
    color_code: str
    intensity: float
    glow_level: Optional[float] = None
    aura_type: Optional[str] = None
    emotion_basis: Dict[str, float]
    created_at: datetime


class AuraInsight(BaseModel):
    date: date
    aura: AuraEntry
    insight: str
    recommendations: List[str]


# ============================================
# WELLNESS
# ============================================

class WellnessScore(BaseModel):
    id: str
    user_id: str
    date: date
    overall_score: float
    emotion_score: Optional[float] = None
    wearable_score: Optional[float] = None
    engagement_score: Optional[float] = None
    score_components: Dict[str, Any]
    insights: List[str]
    recommendations: List[str]
    created_at: datetime


# ============================================
# DOSHA
# ============================================

class DoshaQuizRequest(BaseModel):
    quiz_responses: Dict[str, Any]


class DoshaAssessment(BaseModel):
    id: str
    user_id: str
    vata_score: float
    pitta_score: float
    kapha_score: float
    primary_dosha: str
    secondary_dosha: Optional[str] = None
    assessment_date: datetime


class DoshaRecommendation(BaseModel):
    category: str
    title: str
    description: str
    priority: str


# ============================================
# MEALS
# ============================================

class CreateMealRequest(BaseModel):
    meal_time: datetime
    meal_type: MealType
    meal_text: str
    ingredients: Optional[List[str]] = None
    calories: Optional[int] = None


class Meal(BaseModel):
    id: str
    user_id: str
    meal_time: datetime
    meal_type: MealType
    meal_text: str
    ingredients: Optional[List[str]] = None
    dosha_impact_tags: Optional[Dict[str, str]] = None
    calories: Optional[int] = None
    created_at: datetime


class MealEmotionCorrelation(BaseModel):
    meal_id: str
    meal: Meal
    emotions: List[EmotionLog]
    correlation_score: float
    time_delta_hours: float
    insight: str


# ============================================
# WEARABLE
# ============================================

class WearableDataRequest(BaseModel):
    recorded_at: Optional[datetime] = None
    device_type: str = "apple_watch"
    heart_rate: Optional[int] = None
    hrv: Optional[float] = None
    eda: Optional[float] = None
    sleep_hours: Optional[float] = None
    sleep_quality: Optional[str] = None
    steps: Optional[int] = None
    active_calories: Optional[int] = None
    stress_level: Optional[str] = None
    raw_data: Optional[Dict[str, Any]] = None


class WearableSnapshot(BaseModel):
    id: str
    user_id: str
    recorded_at: datetime
    device_type: str
    heart_rate: Optional[int] = None
    hrv: Optional[float] = None
    eda: Optional[float] = None
    sleep_hours: Optional[float] = None
    sleep_quality: Optional[str] = None
    steps: Optional[int] = None
    active_calories: Optional[int] = None
    stress_level: Optional[str] = None
    created_at: datetime


# ============================================
# ANALYTICS
# ============================================

class AnalyticsPeriod(str, Enum):
    WEEK = "week"
    MONTH = "month"
    QUARTER = "quarter"
    YEAR = "year"


class EmotionTrendData(BaseModel):
    date: str
    emotion_scores: Dict[str, float]


class AnalyticsResponse(BaseModel):
    period: AnalyticsPeriod
    start_date: date
    end_date: date
    emotion_trends: List[EmotionTrendData]
    wellness_trend: List[Dict[str, Any]]
    insights: List[str]


# ============================================
# ALERTS
# ============================================

class Alert(BaseModel):
    id: str
    user_id: str
    alert_type: AlertType
    severity: AlertSeverity
    title: str
    message: str
    triggered_by: Optional[str] = None
    status: str = "active"
    notified_channels: List[str]
    created_at: datetime


class CreateAlertRequest(BaseModel):
    alert_type: AlertType
    severity: AlertSeverity
    title: str
    message: str
    triggered_by: Optional[str] = None


class Notification(BaseModel):
    id: str
    user_id: str
    title: str
    body: str
    type: str
    read: bool = False
    action_url: Optional[str] = None
    created_at: datetime
