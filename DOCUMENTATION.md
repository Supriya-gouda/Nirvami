# Nirvami - Complete Documentation

**Last Updated**: December 8, 2024  
**Version**: 1.0.0

---

## Table of Contents

1. [Platform Overview](#platform-overview)
2. [Complete Features](#complete-features)
3. [Technology Stack](#technology-stack)
4. [Project Structure](#project-structure)
5. [API Reference](#api-reference)
6. [Database Schema](#database-schema)
7. [Installation Guide](#installation-guide)
8. [Testing](#testing)
9. [Security](#security)
10. [Implementation Status](#implementation-status)

---

## Platform Overview

**Nirvami** is an intelligent mental health companion that bridges ancient Ayurvedic wisdom with modern AI technology to provide personalized mental wellness support. The platform combines emotion detection, dosha-based recommendations, wellness tracking, holistic health analytics, AI chatbot with automatic recommendation extraction, and SMS notifications for health alerts.

### Why Nirvami?

<table>
<tr>
<td width="50%">

**🎯 Personalized Wellness**
- Dosha-based Ayurvedic recommendations
- AI-driven emotion analysis
- Custom wellness scoring
- Adaptive guidance

**🤖 AI-Powered Intelligence**
- Google Gemini chatbot
- Automatic recommendation extraction
- Emotion detection from text
- Predictive health insights

</td>
<td width="50%">

**📱 Comprehensive Tracking**
- Wearable device integration
- Meal-mood correlation
- Daily routine monitoring
- Real-time health alerts

**🔔 Smart Notifications**
- SMS alerts via Twilio
- In-app health warnings
- Anomaly detection
- Proactive wellness reminders

</td>
</tr>
</table>

---

## Complete Features

### 🧠 AI-Powered Emotion Intelligence
- **Multi-Modal Emotion Detection**: Analyze emotions from text, voice, and user interactions
- **Real-Time Sentiment Analysis**: Advanced ML models (Flan-T5, MiniLM) for accurate emotion classification
- **Emotion Timeline**: Track emotional patterns over time with detailed analytics
- **15 Mental States Supported**: Balanced, Energized, Stressed, Focused, Tired, Joyful, Sad, Angry, Peaceful, Confused, Motivated, Overwhelmed, Creative, Restless, Grateful
- **Confidence Scores**: ML model provides confidence percentages for each emotion classification
- **Historical Analysis**: View emotion trends over days, weeks, and months
- **Contextual Detection**: Analyzes not just explicit emotions but implied emotional states

### 🎨 Aura Visualization System
- **Dynamic Aura Colors**: 9 distinct aura colors mapped to emotional and mental states
  - Grey (Neutral/No Data)
  - Gold (Balanced/Enlightened)
  - Blue (Peaceful/Calm)
  - Red (Energized/Passionate)
  - Green (Creative/Growing)
  - Purple (Focused/Spiritual)
  - Orange (Joyful/Enthusiastic)
  - Dark Grey (Stressed/Heavy)
  - Pale Blue (Sad/Melancholic)
- **Real-Time Updates**: Aura changes based on latest mood logs
- **Chakra & Element Mapping**: Each aura associated with specific chakras and natural elements
- **Visual Representation**: 3D spinning sphere with gradient effects showing current emotional energy
- **24-Hour Reset**: Aura returns to neutral grey if no mood logged in 24 hours
- **Historical Timeline**: View aura changes over past 30 days

### 🧘 Ayurvedic Dosha Integration
- **Personalized Dosha Assessment**: Interactive quiz with 15+ questions covering:
  - Physical characteristics (body type, skin, hair)
  - Mental traits (stress response, learning style)
  - Lifestyle preferences (sleep patterns, activity levels)
- **Three Dosha Types**:
  - **Vata**: Air + Ether element, creative, energetic, prone to anxiety
  - **Pitta**: Fire + Water element, ambitious, focused, prone to anger
  - **Kapha**: Earth + Water element, stable, calm, prone to lethargy
- **Dosha-Based Recommendations**: Customized suggestions for:
  - Diet (specific foods to favor and avoid)
  - Yoga poses (targeted sequences for balance)
  - Daily routines (optimal wake/sleep times)
  - Lifestyle adjustments (seasonal changes)
- **Balance Tracking**: Monitor dosha balance changes over time
- **Ayurvedic Resources**: Curated content on herbs, practices, and lifestyle adjustments

### 💪 Wellness Scoring & Analytics
- **Comprehensive Wellness Score**: Multi-dimensional scoring (0-100) based on:
  - **Emotional state (40% weight)**:
    - Positive emotions: +20 points
    - Negative emotions: -20 points
    - Neutral: 0 points
  - **Physical health metrics (30% weight)**:
    - Sleep: Optimal 7-9 hrs = +15 points
    - Heart rate: 60-100 bpm = +10 points
    - Activity: >8000 steps = +5 points
  - **Lifestyle factors (30% weight)**:
    - Meal logging consistency: +10 points
    - Routine tracking: +10 points
    - Yoga practice: +10 points
- **Historical Trends**: Track wellness improvements over days, weeks, and months
- **Predictive Insights**: AI-powered alerts for potential health risks
- **Granular Breakdown**: See individual component contributions to overall score
- **Goal Setting**: Set and track custom wellness targets

### 📊 Wearable Data Integration
- **Manual Health Entry**: Log the following metrics:
  - Sleep duration (hours)
  - Heart rate (bpm)
  - Daily steps count
  - Stress level (1-10 scale)
  - Calories burned
- **Apple Watch XML Upload**: 
  - Bulk import historical health data from Apple Health exports
  - Supports standard Apple Health XML format
  - Automatically parses all health records
  - Averages data across multiple days for consolidated entry
- **Real-Time Health Analysis**: Automated detection of 6+ health anomalies:
  - **High heart rate**: >100 bpm resting
  - **Low heart rate**: <60 bpm (bradycardia)
  - **Severe stress**: Stress level >8
  - **Sleep deprivation**: <6 hours sleep
  - **Sedentary behavior**: <5000 steps per day
  - **Combined risk factors**: 
    - Sleep + stress combination
    - Activity + stress combination
    - Triple threat (sleep + activity + stress)
- **Smart Notifications**: 
  - In-app alerts with color-coded severity (yellow, orange, red)
  - Detailed health concern descriptions
  - Actionable recommendations for each anomaly
  - SMS support for critical health events
- **SMS Notifications**: 
  - Automatic SMS alerts sent via Twilio
  - Triggered when wearable data analysis is complete
  - Includes summary of detected concerns
  - Configurable phone number per user profile
- **30-Day Health History**: View trends and patterns in health metrics

### 🍽️ Meal & Diet Tracking
- **Meal Logging**: Record meals with:
  - Timestamp (automatic or manual)
  - Meal description (free text)
  - Optional meal type (breakfast, lunch, dinner, snack)
  - Optional portion size
- **Meal-Emotion Correlation**: 
  - AI analyzes relationships between specific foods and mood changes
  - Identifies trigger foods that negatively impact emotions
  - Highlights mood-boosting meals
  - Statistical correlation analysis over time
- **Ayurvedic Diet Recommendations**: 
  - Dosha-specific food suggestions
  - Seasonal dietary guidance
  - Food combination rules (compatible/incompatible foods)
- **Nutrition Insights**: 
  - Track dietary patterns
  - Identify emotional eating triggers
  - Monitor diet consistency

### 🧘‍♀️ Yoga & Sound Therapy
- **Yoga Pose Library**: 
  - 50+ yoga poses (asanas)
  - Detailed instructions for each pose
  - Sanskrit and English names
  - Difficulty levels (beginner, intermediate, advanced)
  - Benefits and contraindications
  - High-quality images demonstrating proper form
- **Dosha-Specific Sequences**: 
  - Personalized yoga routines based on constitution
  - Vata: Grounding, slow poses (Tree, Warrior)
  - Pitta: Cooling, moderate poses (Forward Fold, Moon Salutation)
  - Kapha: Energizing, dynamic poses (Sun Salutation, Backbends)
- **Sound Healing**: 
  - Curated sound therapy sessions
  - Chakra-specific frequencies
  - Binaural beats for different mental states
  - Guided audio meditations
- **Progress Tracking**: 
  - Monitor yoga practice consistency
  - Track favorite poses
  - Log session duration and frequency

### 📅 Daily Routines (Dinacharya)
- **Ayurvedic Routine Tracking**: Log daily activities aligned with Ayurvedic principles:
  - Morning rituals (waking time, tongue scraping, oil pulling)
  - Midday practices (meal times, work breaks)
  - Evening routines (dinner, relaxation, sleep preparation)
- **Multiple Entries Per Day**: Track different activities throughout the day
- **Routine Analytics**: 
  - Identify patterns and correlations with wellness
  - Optimize daily schedule for better health
  - Track consistency over weeks/months
- **Custom Activities**: Flexible logging for personalized wellness activities
- **Suggested Routines**: Pre-built routine templates based on dosha type

### 💬 AI Chatbot Companion
- **Conversational AI**: 
  - Powered by Google Gemini (gemini-flash-latest) for natural, empathetic interactions
  - Context window remembers conversation history
  - Personality tuned for mental health support
- **Context-Aware Responses**: 
  - Chatbot understands user's emotional state and history
  - Accesses user profile data (dosha, wellness score, recent activities)
  - Provides personalized advice based on complete health picture
- **Real-Time Emotion Detection**: 
  - Analyzes conversation sentiment to update mood logs
  - Detects emotional shifts during conversation
  - Automatically logs emotions without explicit user input
- **Personalized Guidance**: 
  - Recommendations based on user's dosha, wellness score, and current state
  - Adapts advice to user's experience level and preferences
  - Provides Ayurvedic context for suggestions
- **Smart Recommendation Extraction**: 
  - Automatically extracts and saves actionable wellness recommendations
  - Categories: Yoga poses, breathing techniques, meditation practices, lifestyle tips
  - Saves to dedicated recommendations page for easy access
  - Avoids duplicate recommendations
- **Mental Health Focus**: 
  - Specialized in yoga, Ayurveda, meditation, breathing exercises
  - Holistic wellness approach (physical + mental + spiritual)
  - Crisis detection: Identifies concerning language and provides resources
  - Emergency support: Displays crisis hotline numbers when needed

### 📈 Dashboard & Analytics
- **Unified Health Dashboard**: 
  - Real-time overview of all wellness metrics
  - Today's wellness score with trend indicator
  - Current aura visualization
  - Latest emotion status
  - Recent wearable data snapshot
- **Streak Tracking**: 
  - Monitor daily login consistency
  - Gamification to encourage engagement
  - Longest streak record
- **Recent Activity Feed**: 
  - Latest emotions logged
  - Recent meals added
  - Latest health entries
  - Chronological timeline of activities
- **Visual Data Representation**: 
  - Charts for wellness trends
  - Graphs for emotion distribution
  - Color-coded health indicators
  - Progress bars for daily goals
- **Quick Actions**: 
  - Log mood button
  - Add meal button
  - Enter health data button
  - Start chat with AI
  - One-click navigation to all features

---

## Technology Stack

### Frontend Architecture

| Technology | Version | Purpose |
|-----------|---------|----------|
| **React** | 18 | Component-based UI library |
| **TypeScript** | 5.0 | Static type checking and safety |
| **TailwindCSS** | Latest | Utility-first CSS framework |
| **Framer Motion** | Latest | Animation library for smooth transitions |
| **React Hooks** | - | State management (useState, useEffect, useContext) |
| **Context API** | - | Global state (AuthContext, NotificationContext) |
| **Axios** | Latest | HTTP client for API calls (60s timeout) |
| **Vite** | Latest | Fast build tool and dev server |
| **React Router** | 6 | Client-side routing |

**Frontend Dependencies**:
```json
{
  "react": "^18.2.0",
  "react-dom": "^18.2.0",
  "react-router-dom": "^6.22.0",
  "typescript": "^5.0.0",
  "tailwindcss": "^3.4.0",
  "framer-motion": "^11.0.0",
  "axios": "^1.6.0",
  "@supabase/supabase-js": "^2.39.0",
  "lucide-react": "^0.344.0"
}
```

### Backend Architecture

| Technology | Version | Purpose |
|-----------|---------|----------|
| **FastAPI** | 0.104+ | High-performance async Python web framework |
| **Python** | 3.10+ | Programming language |
| **Supabase** | Latest | PostgreSQL database and authentication |
| **JWT** | - | Token-based authentication (PyJWT) |
| **Google Flan-T5-Base** | - | Text emotion analysis (transformers library) |
| **Sentence Transformers** | - | Semantic embeddings for RAG (all-MiniLM-L6-v2) |
| **Google Gemini** | gemini-flash-latest | Conversational AI chatbot |
| **Twilio** | Latest | SMS notification service |
| **Redis** | Latest | Background job queue (RQ library) |
| **Pydantic** | 2.0+ | Data validation and serialization |

**Backend Dependencies**:
```txt
fastapi==0.104.1
uvicorn[standard]==0.24.0
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4
python-multipart==0.0.6
supabase==2.0.0
transformers==4.35.0
torch==2.1.0
sentence-transformers==2.2.2
google-generativeai==0.3.0
twilio==8.10.0
redis==5.0.0
rq==1.15.0
pydantic==2.5.0
python-dotenv==1.0.0
```

### Machine Learning Models

| Model | Size | Purpose | Download Time |
|-------|------|---------|---------------|
| **google/flan-t5-base** | ~1GB | Emotion classification from text | 3-5 minutes |
| **sentence-transformers/all-MiniLM-L6-v2** | ~90MB | Semantic embeddings for RAG system | 1-2 minutes |

**Note**: Models auto-download to `backend/models_cache/` on first run.

### Database

- **PostgreSQL** (via Supabase)
- **Version**: 15+
- **Connection**: PostgREST API via Supabase client
- **Features**: Row-Level Security (RLS), triggers, indexes

---

## Project Structure

### Complete Directory Tree

```
Nirvami/
├── frontend/                     # React + TypeScript frontend
│   ├── src/
│   │   ├── components/           # React components
│   │   │   ├── ui/              # Reusable UI components (shadcn/ui)
│   │   │   │   ├── Button.tsx
│   │   │   │   ├── Card.tsx
│   │   │   │   ├── Input.tsx
│   │   │   │   └── ...
│   │   │   ├── Dashboard.tsx    # Main dashboard
│   │   │   ├── ChatbotPage.tsx  # AI chatbot interface
│   │   │   ├── AuraVisualizationPage.tsx  # Aura 3D display
│   │   │   ├── EmotionHistoryPage.tsx     # Emotion timeline
│   │   │   ├── DoshaQuizPage.tsx          # Ayurvedic assessment
│   │   │   ├── DailyRoutinesPage.tsx      # Routine tracking
│   │   │   ├── DevicePage.tsx             # Wearable data entry
│   │   │   ├── DietMoodPage.tsx           # Meal logging
│   │   │   ├── YogaLifestylePage.tsx      # Yoga & sound therapy
│   │   │   ├── WatchDataUpload.tsx        # Apple Health XML upload
│   │   │   ├── NotificationCenter.tsx     # In-app notifications
│   │   │   ├── CriticalAlertDialog.tsx    # Health alert popup
│   │   │   └── ...
│   │   ├── services/
│   │   │   └── api.ts            # API client (40+ endpoints)
│   │   ├── contexts/
│   │   │   ├── AuthContext.tsx   # Authentication state
│   │   │   └── NotificationContext.tsx  # Notification state
│   │   ├── types/
│   │   │   └── api.types.ts      # TypeScript definitions
│   │   ├── styles/
│   │   │   └── globals.css       # Global CSS styles
│   │   ├── assets/               # Images, icons, SVGs
│   │   ├── App.tsx               # Main app component
│   │   └── main.tsx              # Entry point
│   ├── public/                   # Static assets
│   ├── index.html                # HTML template
│   ├── package.json              # Frontend dependencies
│   ├── tsconfig.json             # TypeScript config
│   ├── vite.config.ts            # Vite build config
│   ├── tailwind.config.js        # TailwindCSS config
│   ├── postcss.config.js         # PostCSS config
│   ├── .env.example              # Environment variable template
│   └── README.md                 # Frontend documentation
│
├── backend/                      # FastAPI Python backend
│   ├── app/
│   │   ├── api/
│   │   │   ├── __init__.py
│   │   │   └── routes/           # API route handlers
│   │   │       ├── __init__.py
│   │   │       ├── auth.py       # Authentication endpoints
│   │   │       ├── profile.py    # User profile endpoints
│   │   │       ├── aura.py       # Aura generation & history
│   │   │       ├── chat.py       # Chatbot with emotion detection
│   │   │       ├── emotions.py   # Emotion logging & analytics
│   │   │       ├── wellness.py   # Wellness score calculation
│   │   │       ├── dosha.py      # Dosha assessment & recommendations
│   │   │       ├── meals.py      # Meal logging & correlations
│   │   │       ├── wearable.py   # Health data & alerts (v1)
│   │   │       ├── wearable_v2.py # Enhanced wearable with XML upload
│   │   │       ├── yoga.py       # Yoga content & routines
│   │   │       ├── routines.py   # Daily routine tracking
│   │   │       ├── alerts.py     # Health alert management
│   │   │       └── recommendations.py  # AI-extracted recommendations
│   │   ├── services/             # Business logic layer
│   │   │   ├── __init__.py
│   │   │   ├── aura_service.py   # Aura computation from emotions
│   │   │   ├── emotion_service.py # ML-based emotion detection
│   │   │   ├── wearable_service.py # Health analytics & anomalies
│   │   │   ├── wearable_service_v2.py # Enhanced wearable service
│   │   │   ├── apple_health_xml_parser.py  # XML parsing logic
│   │   │   ├── gemini_chatbot.py  # Gemini API integration
│   │   │   ├── recommendation_service.py  # Recommendation extraction
│   │   │   ├── sms_service.py     # Twilio SMS integration
│   │   │   ├── notification_service.py  # In-app notifications
│   │   │   ├── alert_service.py   # Health alert generation
│   │   │   ├── meal_service.py    # Meal correlation analysis
│   │   │   └── ...
│   │   ├── models/
│   │   │   ├── __init__.py
│   │   │   └── schemas.py        # Pydantic data models
│   │   ├── utils/
│   │   │   ├── __init__.py
│   │   │   ├── auth.py           # JWT authentication
│   │   │   └── database.py       # Supabase client
│   │   ├── workers/
│   │   │   ├── __init__.py
│   │   │   └── jobs.py           # Background tasks (RQ jobs)
│   │   ├── config.py             # Application configuration
│   │   └── main.py               # FastAPI app initialization
│   ├── database/
│   │   ├── schema.sql            # Complete database schema (30+ tables)
│   │   ├── meal_schema.sql       # Meal-specific schema updates
│   │   ├── notifications_schema.sql  # Notification system schema
│   │   └── cleanup_emotion_logs.sql  # Data cleanup scripts
│   ├── scripts/                  # Setup & seeding scripts
│   │   ├── apply_schema.py       # Apply database schema
│   │   ├── seed_dosha_recommendations.py
│   │   ├── seed_yoga_content.py
│   │   ├── seed_ayurveda_resources.py
│   │   ├── update_wellness_schema.py
│   │   └── ...
│   ├── models_cache/             # ML models (auto-downloaded)
│   │   ├── models--google--flan-t5-base/
│   │   └── models--sentence-transformers--all-MiniLM-L6-v2/
│   ├── requirements.txt          # Python dependencies
│   ├── run_dev.py                # Development server script
│   ├── start-dev.ps1             # PowerShell start script (Windows)
│   ├── .env.example              # Environment variable template
│   └── README.md                 # Backend documentation
│
├── .git/                         # Git repository
├── .gitignore                    # Git ignore rules
├── .vscode/                      # VS Code settings
├── README.md                     # Project overview (this file)
├── DOCUMENTATION.md              # Complete documentation
├── PROJECT_STRUCTURE.md          # Detailed project structure
├── SETUP_GUIDE.md                # Detailed setup instructions
├── IMPLEMENTATION_STATUS_REPORT.md  # Implementation tracking
├── CHAT_IMPLEMENTATION_SUMMARY.md   # Chatbot feature details
└── SMS_NOTIFICATION_TESTING_GUIDE.md  # SMS testing guide
```

---

## API Reference

### Base URL
- **Development**: `http://localhost:8000`
- **Production**: `https://your-domain.com`

### Authentication Endpoints

#### POST /api/v1/auth/signup
Create a new user account.

**Request Body**:
```json
{
  "email": "user@example.com",
  "password": "SecurePass123!",
  "full_name": "John Doe"
}
```

**Response**:
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "token_type": "bearer",
  "user": {
    "id": "uuid",
    "email": "user@example.com",
    "full_name": "John Doe"
  }
}
```

#### POST /api/v1/auth/login
Login with existing credentials.

**Request Body**:
```json
{
  "email": "user@example.com",
  "password": "SecurePass123!"
}
```

**Response**: Same as signup

#### POST /api/v1/auth/guest
Continue as guest (limited features).

**Response**:
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "token_type": "bearer",
  "user": {
    "id": "guest-uuid",
    "email": "guest@nirvami.app",
    "full_name": "Guest User"
  }
}
```

### Profile Endpoints

#### GET /api/v1/profile/me
Get current user profile.

**Headers**: `Authorization: Bearer <token>`

**Response**:
```json
{
  "id": "uuid",
  "email": "user@example.com",
  "full_name": "John Doe",
  "phone_number": "+1234567890",
  "dosha_type": "Vata",
  "created_at": "2024-12-01T00:00:00Z"
}
```

#### PUT /api/v1/profile/me
Update user profile.

**Headers**: `Authorization: Bearer <token>`

**Request Body**:
```json
{
  "full_name": "Jane Doe",
  "phone_number": "+1987654321"
}
```

#### GET /api/v1/profile/streak/current
Get current login streak.

**Response**:
```json
{
  "current_streak": 7,
  "longest_streak": 15,
  "last_login": "2024-12-08T10:30:00Z"
}
```

### Emotion Endpoints

#### POST /api/v1/emotions/log
Log emotion manually.

**Request Body**:
```json
{
  "emotion": "Joyful",
  "confidence": 0.85,
  "notes": "Great day at work!"
}
```

**Response**:
```json
{
  "id": "uuid",
  "emotion": "Joyful",
  "confidence": 0.85,
  "notes": "Great day at work!",
  "created_at": "2024-12-08T10:30:00Z"
}
```

#### GET /api/v1/emotions/logs
Get emotion history.

**Query Parameters**:
- `limit` (optional): Number of logs to return (default: 30)
- `offset` (optional): Pagination offset

**Response**:
```json
{
  "emotions": [
    {
      "id": "uuid",
      "emotion": "Joyful",
      "confidence": 0.85,
      "created_at": "2024-12-08T10:30:00Z"
    }
  ],
  "total": 100
}
```

#### GET /api/v1/emotions/timeline
Get emotion timeline with analytics.

**Response**:
```json
{
  "timeline": [
    {
      "date": "2024-12-08",
      "emotions": ["Joyful", "Energized"],
      "dominant_emotion": "Joyful",
      "average_confidence": 0.82
    }
  ],
  "summary": {
    "most_common_emotion": "Joyful",
    "emotion_distribution": {
      "Joyful": 25,
      "Stressed": 10,
      "Balanced": 15
    }
  }
}
```

### Aura Endpoints

#### GET /api/v1/aura/today
Get today's aura.

**Response**:
```json
{
  "color": "Gold",
  "intensity": 0.9,
  "chakra": "Crown",
  "element": "Spirit",
  "description": "Balanced and enlightened",
  "created_at": "2024-12-08T00:00:00Z"
}
```

#### GET /api/v1/aura/from-latest-emotion
Get dynamic aura from latest mood log.

**Response**: Same as above

#### POST /api/v1/aura/generate
Regenerate today's aura.

**Response**: Same as above

#### GET /api/v1/aura/timeline
Get aura history (30 days).

**Response**:
```json
{
  "auras": [
    {
      "date": "2024-12-08",
      "color": "Gold",
      "intensity": 0.9
    }
  ]
}
```

### Wellness Endpoints

#### GET /api/v1/wellness/today
Get today's wellness score.

**Response**:
```json
{
  "score": 85,
  "components": {
    "emotional": 34,
    "physical": 26,
    "lifestyle": 25
  },
  "breakdown": {
    "emotion_score": 20,
    "sleep_score": 15,
    "activity_score": 5,
    "meal_consistency": 10
  },
  "date": "2024-12-08"
}
```

#### GET /api/v1/wellness/history
Get wellness score history.

**Query Parameters**:
- `days` (optional): Number of days (default: 30)

**Response**:
```json
{
  "history": [
    {
      "date": "2024-12-08",
      "score": 85
    }
  ],
  "average": 78,
  "trend": "improving"
}
```

### Dosha Endpoints

#### POST /api/v1/dosha/assess
Submit dosha quiz answers.

**Request Body**:
```json
{
  "answers": [
    {"question_id": 1, "answer": "A"},
    {"question_id": 2, "answer": "B"}
  ]
}
```

**Response**:
```json
{
  "dosha_type": "Vata",
  "vata_score": 12,
  "pitta_score": 5,
  "kapha_score": 3,
  "description": "You are predominantly Vata...",
  "created_at": "2024-12-08T10:30:00Z"
}
```

#### GET /api/v1/dosha/latest
Get latest dosha assessment.

**Response**: Same as POST response

#### GET /api/v1/dosha/recommendations
Get personalized dosha recommendations.

**Response**:
```json
{
  "diet": [
    "Favor warm, cooked foods",
    "Avoid cold, raw foods"
  ],
  "yoga": ["Tree Pose", "Warrior II"],
  "lifestyle": [
    "Wake up by 6 AM",
    "Practice grounding meditation"
  ]
}
```

### Meal Endpoints

#### POST /api/v1/meals
Log a meal.

**Request Body**:
```json
{
  "description": "Oatmeal with berries",
  "meal_type": "breakfast"
}
```

**Response**:
```json
{
  "id": "uuid",
  "description": "Oatmeal with berries",
  "meal_type": "breakfast",
  "created_at": "2024-12-08T08:00:00Z"
}
```

#### GET /api/v1/meals
Get meal history.

**Query Parameters**:
- `limit` (optional): Number of meals (default: 30)

**Response**:
```json
{
  "meals": [
    {
      "id": "uuid",
      "description": "Oatmeal with berries",
      "meal_type": "breakfast",
      "created_at": "2024-12-08T08:00:00Z"
    }
  ]
}
```

#### GET /api/v1/meals/correlations
Get meal-emotion correlations.

**Response**:
```json
{
  "correlations": [
    {
      "meal": "Oatmeal with berries",
      "emotion": "Energized",
      "correlation": 0.75
    }
  ]
}
```

### Wearable Endpoints

#### POST /api/v1/wearable/manual-entry
Log health metrics manually.

**Request Body**:
```json
{
  "sleep_hours": 7.5,
  "heart_rate": 72,
  "steps": 10500,
  "stress_level": 3,
  "calories": 2200
}
```

**Response**:
```json
{
  "id": "uuid",
  "sleep_hours": 7.5,
  "heart_rate": 72,
  "steps": 10500,
  "stress_level": 3,
  "calories": 2200,
  "source": "manual",
  "created_at": "2024-12-08T10:30:00Z"
}
```

#### POST /api/v1/wearable/upload-xml
Upload Apple Health XML export.

**Request**: Multipart form data with file

**Response**:
```json
{
  "success": true,
  "data_saved": {
    "sleep_hours": 7.2,
    "heart_rate": 68,
    "steps": 9800,
    "calories": 2100,
    "source": "watch"
  },
  "analysis": {
    "concerns": ["High stress detected"],
    "recommendations": ["Practice relaxation"]
  }
}
```

#### GET /api/v1/wearable/latest
Get latest health snapshot.

**Response**: Same as manual-entry response

#### GET /api/v1/wearable/analyze
Analyze health data and detect anomalies.

**Response**:
```json
{
  "concerns": [
    {
      "type": "high_stress",
      "severity": "high",
      "message": "Your stress level is elevated",
      "recommendation": "Practice deep breathing"
    }
  ],
  "overall_health": "needs_attention"
}
```

#### GET /api/v1/wearable/history
Get health history (30 days).

**Response**:
```json
{
  "history": [
    {
      "date": "2024-12-08",
      "sleep_hours": 7.5,
      "heart_rate": 72,
      "steps": 10500
    }
  ]
}
```

### Yoga Endpoints

#### GET /api/v1/yoga/poses
Get yoga pose library.

**Query Parameters**:
- `difficulty` (optional): Filter by difficulty
- `dosha` (optional): Filter by dosha type

**Response**:
```json
{
  "poses": [
    {
      "id": "uuid",
      "name": "Tree Pose",
      "sanskrit_name": "Vrikshasana",
      "difficulty": "beginner",
      "benefits": ["Balance", "Focus"],
      "dosha": ["Vata"],
      "image_url": "https://..."
    }
  ]
}
```

#### GET /api/v1/yoga/recommendations
Get dosha-specific yoga poses.

**Response**: Same as poses endpoint, filtered

#### GET /api/v1/yoga/ayurveda-resources
Get Ayurvedic resources.

**Response**:
```json
{
  "resources": [
    {
      "title": "Understanding Doshas",
      "content": "...",
      "category": "education"
    }
  ]
}
```

### Daily Routine Endpoints

#### POST /api/v1/routines/entry
Add routine entry.

**Request Body**:
```json
{
  "activity": "Morning meditation",
  "duration_minutes": 20,
  "time_of_day": "morning"
}
```

**Response**:
```json
{
  "id": "uuid",
  "activity": "Morning meditation",
  "duration_minutes": 20,
  "time_of_day": "morning",
  "created_at": "2024-12-08T06:30:00Z"
}
```

#### GET /api/v1/routines/entries
Get routine history.

**Response**:
```json
{
  "entries": [
    {
      "id": "uuid",
      "activity": "Morning meditation",
      "duration_minutes": 20,
      "created_at": "2024-12-08T06:30:00Z"
    }
  ]
}
```

#### DELETE /api/v1/routines/entry/{id}
Delete routine entry.

**Response**: `204 No Content`

### Chat Endpoints

#### POST /api/v1/chat/message
Send message to AI chatbot.

**Request Body**:
```json
{
  "message": "I'm feeling stressed, any advice?"
}
```

**Response**:
```json
{
  "response": "Try these breathing exercises...",
  "emotion_detected": "Stressed",
  "confidence": 0.82,
  "recommendations_extracted": [
    {
      "category": "breathing",
      "text": "Practice 4-7-8 breathing"
    }
  ]
}
```

#### GET /api/v1/chat/history
Get chat conversation history.

**Response**:
```json
{
  "messages": [
    {
      "role": "user",
      "content": "I'm feeling stressed",
      "timestamp": "2024-12-08T10:30:00Z"
    },
    {
      "role": "assistant",
      "content": "Try these exercises...",
      "timestamp": "2024-12-08T10:30:05Z"
    }
  ]
}
```

#### GET /api/v1/recommendations
Get AI-extracted recommendations by category.

**Query Parameters**:
- `category` (optional): Filter by category (yoga, breathing, meditation, lifestyle)

**Response**:
```json
{
  "recommendations": [
    {
      "category": "yoga",
      "text": "Practice Tree Pose for balance",
      "source": "chatbot",
      "created_at": "2024-12-08T10:30:00Z"
    }
  ]
}
```

### Alert Endpoints

#### GET /api/v1/alerts/active
Get active health alerts.

**Response**:
```json
{
  "alerts": [
    {
      "id": "uuid",
      "type": "high_stress",
      "message": "High stress detected",
      "severity": "high",
      "created_at": "2024-12-08T10:30:00Z",
      "dismissed": false
    }
  ]
}
```

#### POST /api/v1/alerts/dismiss
Dismiss an alert.

**Request Body**:
```json
{
  "alert_id": "uuid"
}
```

**Response**: `200 OK`

---

## Database Schema

### Core Tables

#### profiles
Stores user account information.

```sql
CREATE TABLE profiles (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  email TEXT UNIQUE NOT NULL,
  full_name TEXT,
  phone_number TEXT,
  dosha_type TEXT,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

#### emotion_logs
Stores emotion detection results.

```sql
CREATE TABLE emotion_logs (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  user_id UUID REFERENCES profiles(id) ON DELETE CASCADE,
  emotion TEXT NOT NULL,
  confidence NUMERIC(5,2),
  notes TEXT,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

#### aura_entries
Stores daily aura visualizations.

```sql
CREATE TABLE aura_entries (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  user_id UUID REFERENCES profiles(id) ON DELETE CASCADE,
  color TEXT NOT NULL,
  intensity NUMERIC(3,2),
  chakra TEXT,
  element TEXT,
  description TEXT,
  date DATE NOT NULL,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  UNIQUE(user_id, date)
);
```

#### wellness_scores
Stores comprehensive wellness calculations.

```sql
CREATE TABLE wellness_scores (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  user_id UUID REFERENCES profiles(id) ON DELETE CASCADE,
  score INTEGER NOT NULL CHECK (score >= 0 AND score <= 100),
  emotional_score INTEGER,
  physical_score INTEGER,
  lifestyle_score INTEGER,
  date DATE NOT NULL,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  UNIQUE(user_id, date)
);
```

#### dosha_assessments
Stores Ayurvedic constitution evaluations.

```sql
CREATE TABLE dosha_assessments (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  user_id UUID REFERENCES profiles(id) ON DELETE CASCADE,
  dosha_type TEXT NOT NULL,
  vata_score INTEGER,
  pitta_score INTEGER,
  kapha_score INTEGER,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

#### meal_logs
Stores diet tracking with timestamps.

```sql
CREATE TABLE meal_logs (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  user_id UUID REFERENCES profiles(id) ON DELETE CASCADE,
  description TEXT NOT NULL,
  meal_type TEXT,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

#### wearable_snapshots
Stores health metrics from devices/manual entry.

```sql
CREATE TABLE wearable_snapshots (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  user_id UUID REFERENCES profiles(id) ON DELETE CASCADE,
  sleep_hours NUMERIC(4,2),
  heart_rate INTEGER,
  steps INTEGER,
  stress_level INTEGER,
  calories INTEGER,
  hrv INTEGER,
  source TEXT DEFAULT 'manual', -- 'manual' or 'watch'
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

#### daily_routines
Stores Ayurvedic daily activity tracking.

```sql
CREATE TABLE daily_routines (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  user_id UUID REFERENCES profiles(id) ON DELETE CASCADE,
  activity TEXT NOT NULL,
  duration_minutes INTEGER,
  time_of_day TEXT,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

#### yoga_content
Stores yoga pose library.

```sql
CREATE TABLE yoga_content (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  name TEXT NOT NULL,
  sanskrit_name TEXT,
  difficulty TEXT,
  benefits TEXT[],
  dosha TEXT[],
  instructions TEXT,
  image_url TEXT,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

#### messages
Stores chat conversation history.

```sql
CREATE TABLE messages (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  user_id UUID REFERENCES profiles(id) ON DELETE CASCADE,
  role TEXT NOT NULL, -- 'user' or 'assistant'
  content TEXT NOT NULL,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

#### health_alerts
Stores automated health notifications.

```sql
CREATE TABLE health_alerts (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  user_id UUID REFERENCES profiles(id) ON DELETE CASCADE,
  type TEXT NOT NULL,
  message TEXT NOT NULL,
  severity TEXT NOT NULL,
  dismissed BOOLEAN DEFAULT FALSE,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

#### recommendations
Stores AI-extracted wellness recommendations.

```sql
CREATE TABLE recommendations (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  user_id UUID REFERENCES profiles(id) ON DELETE CASCADE,
  category TEXT NOT NULL, -- 'yoga', 'breathing', 'meditation', 'lifestyle'
  text TEXT NOT NULL,
  source TEXT DEFAULT 'chatbot',
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

### Row-Level Security (RLS)

All tables have RLS policies ensuring users can only access their own data:

```sql
ALTER TABLE emotion_logs ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can view own emotion logs"
  ON emotion_logs FOR SELECT
  USING (auth.uid() = user_id);

CREATE POLICY "Users can insert own emotion logs"
  ON emotion_logs FOR INSERT
  WITH CHECK (auth.uid() = user_id);
```

### Indexes

Performance-optimized indexes on frequently queried columns:

```sql
CREATE INDEX idx_emotion_logs_user_id ON emotion_logs(user_id);
CREATE INDEX idx_emotion_logs_created_at ON emotion_logs(created_at);
CREATE INDEX idx_aura_entries_user_date ON aura_entries(user_id, date);
CREATE INDEX idx_wellness_scores_user_date ON wellness_scores(user_id, date);
```

---

## Installation Guide

### Prerequisites

| Requirement | Version | Download |
|------------|---------|----------|
| **Python** | 3.10+ | [python.org](https://www.python.org/downloads/) |
| **Node.js** | 18+ | [nodejs.org](https://nodejs.org/) |
| **Supabase Account** | - | [supabase.com](https://supabase.com) |
| **Google Gemini API** | gemini-flash-latest | [makersuite.google.com](https://makersuite.google.com/app/apikey) |
| **Twilio Account** | (Optional) | [twilio.com](https://www.twilio.com/try-twilio) |
| **Redis** | Latest | [redis.io](https://redis.io/download) |

### Step 1: Clone Repository

```bash
git clone https://github.com/Supriya-gouda/Nirvami.git
cd Nirvami
```

### Step 2: Backend Setup

```bash
# Navigate to backend
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
.\venv\Scripts\Activate.ps1  # Windows PowerShell
venv\Scripts\activate        # Windows CMD
source venv/bin/activate     # Mac/Linux

# Install dependencies
pip install -r requirements.txt

# Setup environment variables
cp .env.example .env
# Edit .env with your credentials
```

**Required Environment Variables (.env)**:

```env
# Supabase Configuration
# Get from Supabase Dashboard → Project Settings → API
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your_supabase_anon_key
SUPABASE_SERVICE_ROLE_KEY=your_service_role_key

# Google Gemini Configuration
# Get from Google AI Studio
GEMINI_API_KEY=your_gemini_api_key

# JWT Configuration
JWT_SECRET_KEY=your_random_secret_key_here
JWT_ALGORITHM=HS256

# Twilio Configuration (Optional - for SMS notifications)
TWILIO_ACCOUNT_SID=your_twilio_account_sid
TWILIO_AUTH_TOKEN=your_twilio_auth_token
TWILIO_PHONE_NUMBER=+1234567890

# Redis Configuration (for background jobs)
REDIS_URL=redis://localhost:6379
```

**Apply Database Schema**:

```bash
python scripts/apply_schema.py
```

**Seed Initial Data (Optional)**:

```bash
python scripts/seed_dosha_recommendations.py
python scripts/seed_yoga_content.py
python scripts/seed_ayurveda_resources.py
```

**Start Backend Server**:

```bash
python run_dev.py
# Backend runs on http://localhost:8000
# API docs at http://localhost:8000/docs
```

**Note**: On first run, ML models (~300MB total) will auto-download to `models_cache/` directory. This takes 2-5 minutes depending on internet speed.

### Step 3: Frontend Setup

Open a new terminal:

```bash
# Navigate to frontend
cd frontend

# Install dependencies
npm install

# Setup environment variables
cp .env.example .env.local
# Edit .env.local with same Supabase credentials
```

**Required Environment Variables (.env.local)**:

```env
VITE_API_URL=http://localhost:8000
VITE_SUPABASE_URL=https://your-project.supabase.co
VITE_SUPABASE_ANON_KEY=your_supabase_anon_key
```

**Start Frontend Server**:

```bash
npm run dev
# Frontend runs on http://localhost:3000
```

### Step 4: Open Application

Visit **http://localhost:3000** in your browser and create an account!

### Verification Checklist

- ✅ Backend running on http://localhost:8000
- ✅ Frontend running on http://localhost:3000
- ✅ API docs accessible at http://localhost:8000/docs
- ✅ ML models downloaded to `backend/models_cache/`
- ✅ Database schema applied successfully
- ✅ Can create account and login

### Troubleshooting

**Backend Issues**:

- **Module not found**: Run `pip install -r requirements.txt` in activated venv
- **Supabase connection error**: Verify credentials in `.env` file
- **Models not downloading**: Check internet connection and ~500MB free disk space
- **Port 8000 already in use**: Change port in `run_dev.py` or stop conflicting process

**Frontend Issues**:

- **npm install fails**: Delete `node_modules/` and `package-lock.json`, retry
- **CORS error**: Ensure backend is running on port 8000
- **.env.local not found**: Copy from `.env.example` and fill in values
- **Build errors**: Check TypeScript version compatibility

**Database Issues**:

- **Schema apply fails**: Ensure Supabase service role key is correct
- **RLS errors**: Verify JWT token is being sent in API requests
- **Connection timeout**: Check Supabase project is not paused

---

## Testing

### Backend Testing

#### Unit Tests

```bash
cd backend/scripts

# Test emotion detection service
python -c "from app.services.emotion_service import EmotionService; service = EmotionService(); print(service.detect_emotion('I am very happy today'))"

# Test database connectivity
python test_database.py

# Test wearable feature
python test_wearable_feature.py

# Test daily routines
python test_daily_routines.py

# Test yoga feature
python test_yoga_feature.py
```

#### Integration Tests

```bash
# Test dosha end-to-end flow
python test_dosha_end_to_end.py

# Test dashboard analytics
python test_dashboard_analytics.py

# Test real user workflow
python test_real_user.py

# Test final integration
python test_final_integration.py
```

#### Data Verification

```bash
# Verify database content
python verify_content.py

# Verify emotion schema
python verify_emotion_schema.py

# Check database status
python check_db.py
```

### Frontend Testing

#### Manual Testing Guide

See [FRONTEND_TESTING_GUIDE.md](FRONTEND_TESTING_GUIDE.md) for comprehensive frontend testing procedures.

#### SMS Notification Testing

See [SMS_NOTIFICATION_TESTING_GUIDE.md](SMS_NOTIFICATION_TESTING_GUIDE.md) for SMS testing guide.

### API Testing

Use the Swagger UI at `http://localhost:8000/docs` for interactive API testing:

1. Click "Authorize" and enter JWT token
2. Expand any endpoint
3. Click "Try it out"
4. Fill in parameters
5. Click "Execute"
6. View response

---

## Security

### Authentication & Authorization

- **JWT Tokens**: Secure token-based authentication using HS256 algorithm
- **Token Expiry**: Tokens expire after 24 hours (configurable)
- **Refresh Mechanism**: Users must login again after token expires
- **Password Hashing**: Bcrypt with salt for secure password storage
- **Guest Mode**: Limited-feature guest access without persistent data

### Database Security

- **Row-Level Security (RLS)**: Every table has RLS policies
- **User Isolation**: Users can only access their own data
- **Service Role Key**: Used only for server-side admin operations
- **Cascade Deletes**: User data deleted when account is removed
- **Prepared Statements**: SQL injection prevention via Supabase client

### API Security

- **CORS Configuration**: Restricted to authorized frontend origins only
- **Input Validation**: Pydantic models validate all API inputs
- **Rate Limiting**: (Recommended for production) Limit requests per IP/user
- **HTTPS**: (Production) Enforce HTTPS for all connections

### Data Privacy

- **Environment Variables**: Sensitive keys stored in `.env` (not committed to Git)
- **API Key Protection**: Keys never exposed to frontend (backend only)
- **User Data Encryption**: Database-level encryption via Supabase
- **No Third-Party Analytics**: User privacy respected (no tracking)

### SMS Security

- **Twilio Authentication**: SID and Auth Token for secure API access
- **Phone Number Validation**: Verify user phone numbers before sending
- **Message Sanitization**: Clean user data before including in SMS
- **Opt-In Required**: Users must provide phone number explicitly

### Production Recommendations

1. **Enable HTTPS**: Use SSL/TLS certificates
2. **Implement Rate Limiting**: Prevent API abuse
3. **Add CAPTCHA**: On signup/login to prevent bots
4. **Monitor Logs**: Track suspicious activity
5. **Regular Updates**: Keep dependencies updated
6. **Backup Strategy**: Regular database backups
7. **Audit Trail**: Log all sensitive operations

---

## Implementation Status

### ✅ Fully Implemented Features

#### Core System
- ✅ User authentication (signup, login, guest mode)
- ✅ JWT token-based security
- ✅ Row-Level Security (RLS) on all database tables
- ✅ Responsive UI with mobile support
- ✅ Navigation system with bottom navigation bar
- ✅ Onboarding flow for new users

#### Emotion & Mental Health
- ✅ Multi-modal emotion detection (text, voice context)
- ✅ 15 mental states classification
- ✅ Emotion logging with confidence scores
- ✅ Emotion timeline and analytics
- ✅ Historical emotion tracking (30+ days)
- ✅ Emotion distribution charts

#### Aura Visualization
- ✅ Dynamic aura generation from latest emotion
- ✅ 9 aura colors with gradient effects
- ✅ 3D spinning sphere visualization (Framer Motion)
- ✅ Real-time aura updates on mood logs
- ✅ 24-hour aura reset mechanism
- ✅ Chakra and element associations
- ✅ Aura history timeline (30 days)
- ✅ Aura description and meaning display

#### Wellness Scoring
- ✅ Comprehensive wellness calculation algorithm
- ✅ Multi-factor scoring (emotion 40%, physical 30%, lifestyle 30%)
- ✅ Daily wellness score generation
- ✅ Historical wellness tracking (90+ days)
- ✅ Wellness trends and analytics
- ✅ Granular component breakdown
- ✅ Trend indicators (improving, declining, stable)

#### Dosha System
- ✅ Interactive dosha assessment quiz (15 questions)
- ✅ Vata, Pitta, Kapha constitution determination
- ✅ Dosha-specific recommendations (diet, yoga, lifestyle)
- ✅ Dosha balance tracking
- ✅ Ayurvedic resources library (50+ resources)
- ✅ Dosha description and characteristics
- ✅ Seasonal recommendations

#### Wearable Integration
- ✅ Manual health data entry (sleep, HR, steps, stress, calories, HRV)
- ✅ Apple Health XML bulk upload with parser
- ✅ XML data averaging across multiple days
- ✅ Source tracking ('manual' vs 'watch')
- ✅ Real-time health anomaly detection (6+ types)
- ✅ Automated health alerts with severity levels
- ✅ SMS notifications via Twilio (on analysis complete)
- ✅ In-app critical health popups (horizontal format)
- ✅ 30-day health history tracking
- ✅ Latest snapshot display on dashboard
- ✅ Health metrics visualization (charts/graphs)

#### Diet & Meals
- ✅ Meal logging with timestamps
- ✅ Meal-emotion correlation analysis (AI-powered)
- ✅ Meal history retrieval (90+ days)
- ✅ Meal type categorization
- ✅ Integration with wellness scoring
- ✅ Ayurvedic diet suggestions
- ✅ Trigger food identification

#### Yoga & Sound Therapy
- ✅ Yoga pose library (50+ poses with images)
- ✅ Dosha-specific yoga recommendations
- ✅ Pose instructions with Sanskrit names
- ✅ Difficulty levels (beginner, intermediate, advanced)
- ✅ Sound therapy content library
- ✅ Practice tracking and history
- ✅ Chakra-specific poses

#### Daily Routines
- ✅ Ayurvedic routine (dinacharya) tracking
- ✅ Multiple entries per day support
- ✅ Time-based activity logging (morning, midday, evening)
- ✅ Routine history and analytics
- ✅ Activity duration tracking
- ✅ Routine consistency scoring

#### AI Chatbot
- ✅ Google Gemini gemini-flash-latest powered conversational AI
- ✅ Context-aware responses with mental health focus
- ✅ Real-time emotion detection from chat conversations
- ✅ Personalized guidance based on user state, dosha, history
- ✅ Chat history storage and retrieval (persistent)
- ✅ Automatic recommendation extraction (yoga, breathing, meditation, lifestyle)
- ✅ Smart parsing of chat responses into actionable wellness tips
- ✅ Recommendations saved to dedicated pages by category
- ✅ Crisis detection with emergency resources
- ✅ Crisis alert popup for concerning language
- ✅ Conversation context (remembers past 10 messages)

#### Dashboard & Analytics
- ✅ Unified health overview dashboard
- ✅ Daily login streak tracking
- ✅ Recent activity feed (emotions, meals, health)
- ✅ Real-time data updates
- ✅ Visual wellness indicators with colors
- ✅ Quick action buttons (log mood, add meal, enter health data)
- ✅ Welcome messages based on time of day
- ✅ Summary cards for key metrics

#### Notification System
- ✅ In-app notification center
- ✅ Red pulsing indicator for crisis-type alerts
- ✅ Critical health concern popups (horizontal, 3-column)
- ✅ Notification history and dismissal
- ✅ SMS notifications for health alerts (Twilio)
- ✅ Multi-channel notification support

### 🚧 Planned Enhancements

- 🔜 Direct smartwatch sync (Apple Watch, Fitbit, Garmin API integration)
- 🔜 Advanced trend analysis with ML predictions
- 🔜 Weekly/monthly health report emails (automated)
- 🔜 Social features (community forum, sharing progress, leaderboards)
- 🔜 Guided meditation sessions (audio/video)
- 🔜 Advanced yoga pose detection via camera (ML-based)
- 🔜 Export health data (CSV, PDF reports, JSON backup)
- 🔜 Multi-language support (Hindi, Spanish, French)
- 🔜 Dark mode theme (full UI)
- 🔜 Voice interaction with chatbot (speech-to-text)
- 🔜 Integration with other health apps (MyFitnessPal, Strava)
- 🔜 Personalized meditation recommendations
- 🔜 Mood journaling with prompts
- 🔜 Goal setting and progress tracking
- 🔜 Health coaching via chatbot (proactive suggestions)

### 🐛 Known Issues

- ⚠️ XML upload processing time can be slow for large files (>100MB)
- ⚠️ First-time ML model download requires stable internet
- ⚠️ Chat history limited to 10 messages (older messages not considered)
- ⚠️ Emotion detection accuracy varies with text length
- ⚠️ Wearable data analysis timeouts for very old accounts (>1 year data)

---

## Contributing

This is a private project currently under active development. For questions or collaboration inquiries, please contact the repository owner.

### Development Guidelines

- **Code Style**: Follow PEP 8 for Python, ESLint/Prettier for TypeScript
- **Commit Messages**: Use conventional commits (feat, fix, docs, etc.)
- **Branching**: Create feature branches from `main`
- **Testing**: Write tests for new features
- **Documentation**: Update docs when adding features

---

## License

Copyright © 2025 Nirvami. All rights reserved.

---

## Acknowledgments

- **Ayurvedic Wisdom**: Ancient principles adapted for modern wellness
- **Google Gemini**: Conversational AI capabilities (gemini-flash-latest model)
- **Supabase**: Backend infrastructure and PostgreSQL database
- **Twilio**: SMS notification service for health alerts
- **Hugging Face**: Open-source ML models (Flan-T5-Base, Sentence Transformers MiniLM)
- **React Community**: UI component libraries and patterns
- **Framer Motion**: Beautiful animation library
- **Open Source Community**: Countless libraries and tools that made this possible

---

<div align="center">

**Built with ❤️ for mental wellness**

*Empowering individuals through AI-driven holistic health solutions*

For complete setup instructions, see [SETUP_GUIDE.md](SETUP_GUIDE.md)

For implementation status, see [IMPLEMENTATION_STATUS_REPORT.md](IMPLEMENTATION_STATUS_REPORT.md)

Last Updated: December 13, 2024

</div>
