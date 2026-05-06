# 🌟 Nirvami - AI-Powered Holistic Wellness Platform

[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![React](https://img.shields.io/badge/React-18-61DAFB.svg)](https://reactjs.org/)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.0-3178C6.svg)](https://www.typescriptlang.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-009688.svg)](https://fastapi.tiangolo.com/)
[![License](https://img.shields.io/badge/License-Proprietary-red.svg)](LICENSE)

An intelligent mental health companion that seamlessly integrates **ancient Ayurvedic wisdom** with **cutting-edge AI technology** to provide personalized mental wellness support, emotional intelligence, and holistic health tracking.

**Version**: 2.0.0 | **Status**: Production Ready ✅ | **Last Updated**: January 9, 2026

---

## 📸 Platform Preview

![Nirvami Home Page](HomePage.png)
*Beautiful landing page with smooth animations and responsive design*

![Nirvami Dashboard](Dashborad.png)
*Comprehensive wellness dashboard with real-time analytics*

---

## 🎯 Overview

Nirvami is a revolutionary mental wellness platform that combines the timeless principles of Ayurveda with modern artificial intelligence to create a personalized health companion. The platform offers:

- **AI-Driven Insights**: Advanced emotion detection and conversational AI
- **Ayurvedic Personalization**: Dosha-based recommendations tailored to your constitution
- **Comprehensive Tracking**: Emotions, meals, wearables, and wellness activities
- **Visual Analytics**: Interactive dashboards, 3D aura visualization, and trend graphs
- **Holistic Approach**: Integration of mind, body, and spirit for complete wellness

---

## ✨ Core Features

### 🤖 AI-Powered Intelligence
- **ML Emotion Detection**: Fine-tuned RoBERTa model with 28 emotion categories mapped to 7 core emotions
- **Confidence Scoring**: Real-time emotion classification with accuracy metrics
- **Google Gemini Integration**: Context-aware conversational AI with Retrieval-Augmented Generation (RAG)
- **Smart Recommendation Extraction**: Automatically parses AI conversations for actionable wellness suggestions
- **Crisis Detection System**: Intelligent monitoring and alert system for mental health emergencies
- **Semantic Search**: Vector-based RAG using sentence transformers for personalized content retrieval

### 🎨 Visualization & Tracking
- **3D Aura Sphere**: Interactive three.js visualization with 9 emotion-based colors
- **Emotion Timeline**: Historical emotion tracking with trends and pattern analysis
- **Progress Dashboard**: 
  - 7 live metrics (today's data)
  - 3 interactive graphs (trend analysis)
  - Real-time adherence tracking
- **Mood-Food Correlation**: AI-powered analysis connecting dietary choices with emotional states
- **Wellness Score**: Composite metric (40% emotion + 30% engagement + 30% consistency)

### 🧘 Ayurvedic Intelligence System
- **Comprehensive Dosha Quiz**: 12-question assessment for Vata, Pitta, and Kapha constitution
- **Multi-Dosha Detection**: 
  - Single dosha (clear dominant type)
  - Dual dosha (top 2 within 10% margin)
  - Tri-dosha (balanced, all 3 within 10%)
- **Personalized Recommendations**: 
  - Yoga poses matched to dosha type
  - Dietary suggestions based on constitution
  - Lifestyle and daily routine recommendations
- **Dynamic Balance Display**: Real-time dosha percentage visualization
- **Seasonal Adjustments**: Recommendations adapted to current season and dosha needs

### 📊 Wellness Analytics

**Live Metrics (Today's Real-Time Data):**
- 😊 Average Mood Score (1-10 scale)
- 😰 Stress Level (combined emotion + wearable data)
- ✅ Total Recommendations vs Completed
- 📈 Live Adherence Percentage

**Historical Metrics (Yesterday & Beyond):**
- 🔥 Consistency Score (7-day streak system, max 10/10)
- 💯 Wellness Score (weighted composite metric)
- 📉 Trend Analysis (30-day moving averages)

**Interactive Graphs:**
- Emotion Trends Over Time
- Wellness Score Evolution
- Adherence Tracking Timeline

### 🍽️ Nutrition & Health
- **Meal Tracking System**: 
  - Breakfast, lunch, dinner, and snacks logging
  - Photo upload capability
  - Nutritional notes and tags
- **Mood-Food AI Analysis**: 
  - Correlation patterns between meals and emotions
  - Personalized dietary insights
  - Trigger food identification
- **Wearable Integration**: 
  - Manual health metric entry
  - Apple Health XML file upload and parsing
  - Heart rate, steps, sleep, and more
- **Health Anomaly Detection**: 
  - Flags unusual vital signs
  - Trend-based alerts
  - Personalized threshold monitoring

### 🧘‍♀️ Practice & Wellness Routines
- **Yoga Library**: 50+ poses with detailed instructions and dosha tags
- **Sound Therapy**: Curated meditation tracks from YouTube integration
- **Daily Routines (Dinacharya)**: 
  - Morning and evening Ayurvedic practices
  - Habit tracking with streak counting
  - Personalized routine recommendations
- **Practice Session Logging**: 
  - Duration and intensity tracking
  - Personal ratings and notes
  - Progress analytics

### 💬 AI Chatbot & Journaling
- **Conversational Wellness Coach**: Natural language interaction with Gemini AI
- **Context-Aware Responses**: Remembers user history and preferences
- **Recommendation Generation**: Creates actionable items from conversations
- **Emotional Journal**: Private journaling with emotion detection
- **Guided Reflection**: Prompts for deeper self-awareness

### 🔔 Notifications & Alerts
- **SMS Notifications**: Twilio integration for critical alerts
- **Email Reminders**: Practice and routine notifications
- **Crisis Alerts**: Automatic notifications for detected mental health crises
- **Customizable Settings**: User-controlled notification preferences

---

## 🏗️ Technology Stack

### Frontend
- **Framework**: React 18 with TypeScript 5.0
- **Build Tool**: Vite (lightning-fast HMR)
- **Styling**: TailwindCSS with custom design system
- **Animations**: Framer Motion for fluid UI transitions
- **Charts**: Recharts for data visualization
- **3D Graphics**: Three.js for aura sphere
- **Icons**: Lucide React
- **HTTP Client**: Axios with interceptors
- **State Management**: React Context API
- **Routing**: React Router v6

### Backend
- **Framework**: FastAPI (Python 3.10+)
- **Database**: PostgreSQL via Supabase
- **Vector Store**: pgvector for semantic search
- **Authentication**: Supabase Auth with JWT
- **Background Jobs**: Redis Queue (RQ)
- **Caching**: Redis
- **ORM**: Raw SQL with Supabase client

### AI & Machine Learning
- **LLM**: Google Gemini 1.5 Flash
- **Emotion Detection**: `SamLowe/roberta-base-go_emotions` (28 emotions)
- **Embeddings**: `sentence-transformers/all-MiniLM-L6-v2` (384 dimensions)
- **RAG System**: Custom implementation with pgvector
- **Model Caching**: Local HuggingFace model cache

### External Services
- **Database & Auth**: Supabase
- **SMS**: Twilio
- **Email**: SMTP (configurable)
- **Video Content**: YouTube Data API v3
- **AI API**: Google Generative AI

### DevOps & Tools
- **Version Control**: Git
- **Package Management**: pip (Python), npm (Node.js)
- **Environment**: `.env` configuration
- **Development Server**: Uvicorn (backend), Vite (frontend)

---

## 📁 Project Structure

```
Nirvami/
├── frontend/                       # React TypeScript Application
│   ├── src/
│   │   ├── components/            # React Components
│   │   │   ├── ui/               # Reusable UI components
│   │   │   ├── Dashboard.tsx     # Main wellness dashboard
│   │   │   ├── ChatbotPage.tsx   # AI chatbot interface
│   │   │   ├── AuraPage.tsx      # 3D aura visualization
│   │   │   ├── DoshaQuiz.tsx     # Ayurvedic assessment
│   │   │   ├── EmotionHistory.tsx # Emotion tracking
│   │   │   ├── MealTracker.tsx   # Nutrition logging
│   │   │   ├── WearableData.tsx  # Health data management
│   │   │   ├── YogaLibrary.tsx   # Yoga pose library
│   │   │   └── ...               # More feature components
│   │   ├── pages/
│   │   │   └── Journal.tsx       # Journaling interface
│   │   ├── services/
│   │   │   └── api.ts            # API client (50+ endpoints)
│   │   ├── contexts/
│   │   │   └── AuthContext.tsx   # Authentication state
│   │   ├── types/
│   │   │   └── api.types.ts      # TypeScript definitions
│   │   ├── styles/               # Global CSS
│   │   ├── assets/               # Images and static files
│   │   ├── App.tsx               # Root component
│   │   └── main.tsx              # Application entry point
│   ├── index.html                # HTML template
│   ├── package.json              # Dependencies
│   ├── tsconfig.json             # TypeScript configuration
│   ├── vite.config.ts            # Vite build config
│   ├── .env.example              # Environment template
│   └── README.md                 # Frontend documentation
│
├── backend/                       # FastAPI Python Backend
│   ├── app/
│   │   ├── api/
│   │   │   └── routes/           # API Route Modules
│   │   │       ├── auth.py       # Authentication endpoints
│   │   │       ├── emotions.py   # Emotion tracking
│   │   │       ├── chatbot.py    # AI chatbot
│   │   │       ├── dosha.py      # Ayurvedic assessment
│   │   │       ├── recommendations.py
│   │   │       ├── meals.py      # Meal tracking
│   │   │       ├── wearable.py   # Health data
│   │   │       ├── yoga.py       # Yoga content
│   │   │       ├── practice.py   # Practice sessions
│   │   │       ├── progress.py   # Analytics
│   │   │       └── ...           # 20+ total routes
│   │   ├── services/             # Business Logic Layer
│   │   │   ├── emotion_service.py
│   │   │   ├── gemini_chatbot.py
│   │   │   ├── dosha_service.py
│   │   │   ├── recommendation_service.py
│   │   │   ├── meal_service.py
│   │   │   ├── wearable_service_v2.py
│   │   │   ├── rag_service.py    # RAG implementation
│   │   │   ├── crisis_detector.py
│   │   │   ├── alert_service.py
│   │   │   ├── notification_service.py
│   │   │   ├── sms_service.py
│   │   │   ├── apple_health_parser.py
│   │   │   ├── aura_service.py
│   │   │   └── ...
│   │   ├── ml/
│   │   │   └── model_manager.py  # ML model loader
│   │   ├── models/
│   │   │   └── schemas.py        # Pydantic models
│   │   ├── utils/
│   │   │   ├── auth.py           # JWT utilities
│   │   │   ├── database.py       # DB connection
│   │   │   └── email.py          # Email utilities
│   │   ├── workers/              # Background Jobs
│   │   │   ├── scheduler.py      # Job scheduling
│   │   │   ├── jobs.py           # Task definitions
│   │   │   └── worker.py         # RQ worker
│   │   ├── config.py             # App configuration
│   │   └── main.py               # FastAPI application
│   ├── database/
│   │   ├── schema.sql            # Complete database schema
│   │   └── migrations/           # Schema migrations
│   ├── scripts/                  # Utility Scripts
│   │   ├── apply_schema.py       # Database setup
│   │   ├── seed_ayurveda_resources.py
│   │   ├── seed_dosha_recommendations.py
│   │   ├── seed_practice_content.py
│   │   ├── seed_yoga_content.py
│   │   └── setup_yoga_feature.py
│   ├── models_cache/             # Cached ML models
│   ├── songs/                    # Audio resources
│   ├── requirements.txt          # Python dependencies
│   ├── run_dev.py                # Development server
│   ├── start-dev.ps1             # PowerShell start script
│   ├── .env.example              # Environment template
│   └── README.md                 # Backend documentation
│
├── .git/                         # Git repository
├── .gitignore                    # Git ignore rules
├── .vscode/                      # VS Code settings
├── HomePage.png                  # Landing page screenshot
├── Dashborad.png                 # Dashboard screenshot
└── README.md                     # This file
```

---

## 🚀 Quick Start Guide

### Prerequisites

Before you begin, ensure you have the following installed:

- **Python 3.10 or higher** - [Download Python](https://www.python.org/downloads/)
- **Node.js 18 or higher** - [Download Node.js](https://nodejs.org/)
- **Git** - [Download Git](https://git-scm.com/)
- **Supabase Account** - [Sign up at Supabase](https://supabase.com)
- **Google Gemini API Key** - [Get API Key](https://makersuite.google.com/app/apikey)
- **YouTube API Key** - [Get API Key](https://console.cloud.google.com/)
- **Redis** (optional for background jobs) - [Download Redis](https://redis.io/download)

### Step 1: Clone the Repository

```bash
git clone https://github.com/yourusername/Nirvami.git
cd Nirvami
```

### Step 2: Backend Setup

```bash
# Navigate to backend directory
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows PowerShell:
.\venv\Scripts\Activate.ps1
# Windows CMD:
.\venv\Scripts\activate.bat
# Linux/Mac:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Create environment file
cp .env.example .env

# Edit .env with your credentials (see configuration section below)
```

#### Configure Backend Environment

Edit `backend/.env` with your credentials:

```env
# Supabase Configuration
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-anon-key
SUPABASE_SERVICE_ROLE_KEY=your-service-role-key

# Database
DATABASE_URL=postgresql://postgres:[password]@db.your-project.supabase.co:5432/postgres

# JWT Secret (from Supabase project settings)
SECRET_KEY=your-jwt-secret

# AI Services
GEMINI_API_KEY=your-gemini-api-key
YOUTUBE_API_KEY=your-youtube-api-key

# Redis (for background jobs - optional)
REDIS_URL=redis://localhost:6379/0

# Twilio (for SMS - optional)
TWILIO_ACCOUNT_SID=your-twilio-sid
TWILIO_AUTH_TOKEN=your-twilio-token
TWILIO_PHONE_NUMBER=your-twilio-phone

# Email (optional)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password
```

#### Initialize Database

```bash
# Run database schema setup
python scripts/apply_schema.py

# Seed initial data (optional but recommended)
python scripts/seed_ayurveda_resources.py
python scripts/seed_dosha_recommendations.py
python scripts/seed_yoga_content.py
python scripts/seed_practice_content.py
```

#### Start Backend Server

```bash
# Start development server
python run_dev.py

# Or use PowerShell script
.\start-dev.ps1
```

Backend will be running at: **http://localhost:8000**  
API documentation: **http://localhost:8000/docs**

### Step 3: Frontend Setup

Open a new terminal window:

```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install

# Create environment file
cp .env.example .env

# Edit .env with your configuration
```

#### Configure Frontend Environment

Edit `frontend/.env`:

```env
# API Configuration
VITE_API_URL=http://localhost:8000

# Supabase (same as backend)
VITE_SUPABASE_URL=https://your-project.supabase.co
VITE_SUPABASE_ANON_KEY=your-anon-key

# YouTube API
VITE_YOUTUBE_API_KEY=your-youtube-api-key
```

#### Start Frontend Server

```bash
# Start development server
npm run dev
```

Frontend will be running at: **http://localhost:5173**

### Step 4: Access the Application

1. Open your browser and navigate to **http://localhost:5173**
2. Create a new account or sign in
3. Complete your dosha assessment
4. Start tracking your wellness journey!

---

## 🔧 Configuration Guide

### Supabase Setup

1. **Create Project**: Go to [Supabase](https://supabase.com) and create a new project
2. **Enable pgvector**: In SQL Editor, run:
   ```sql
   CREATE EXTENSION IF NOT EXISTS vector;
   ```
3. **Run Schema**: Copy contents of `backend/database/schema.sql` and execute in SQL Editor
4. **Get Credentials**: 
   - Project URL: Settings → API → Project URL
   - Anon Key: Settings → API → anon/public key
   - Service Role Key: Settings → API → service_role key
   - JWT Secret: Settings → API → JWT Settings

### Google Gemini API

1. Visit [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Create a new API key
3. Add to your `.env` file

### YouTube API

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing
3. Enable YouTube Data API v3
4. Create credentials (API Key)
5. Add to your `.env` files

### Twilio (Optional - for SMS)

1. Sign up at [Twilio](https://www.twilio.com/)
2. Get your Account SID and Auth Token
3. Purchase a phone number
4. Add credentials to backend `.env`

---

## 📊 Key Features Implementation

### Progress Analytics System

**Live Metrics (Today's Data):**
- Calculated in real-time from current day's activities
- Mood average from emotion entries
- Stress level from emotion detection + wearable data
- Recommendation tracking with completion percentage

**Historical Metrics (Yesterday & Before):**
- Consistency Score: 7-day streak system (1 point per day, max 10)
- Wellness Score Formula: `(0.4 × emotion_health) + (0.3 × engagement) + (0.3 × consistency)`
- All calculations exclude today for stable historical data

**Graphs:**
- 30-day emotion trend line
- Wellness score evolution
- Adherence percentage over time

### Dosha Assessment & Scoring

**Quiz System:**
- 12 carefully crafted questions
- 3 answer options per question (Vata, Pitta, Kapha)
- Simple point counting system

**Dosha Categorization:**
```
Single Dosha: One type > 50% of total
Dual Dosha: Top 2 types within 10% of each other
Tri-Dosha: All 3 types within 10% range (balanced)
```

**Dynamic Recommendations:**
- Yoga poses tagged with primary/secondary dosha benefits
- Dietary guidelines based on dosha constitution
- Seasonal adjustments for dosha balance

### Emotion-to-Aura Color Mapping

| Emotion | Aura Color | RGB Code |
|---------|-----------|----------|
| Joy | Yellow | `#FFD700` |
| Love | Pink | `#FF69B4` |
| Calm | Blue | `#4169E1` |
| Neutral | White | `#FFFFFF` |
| Surprise | Orange | `#FFA500` |
| Fear | Purple | `#800080` |
| Stress | Gray | `#808080` |
| Anger | Red | `#DC143C` |
| Sadness | Dark Blue | `#000080` |

### AI Recommendation Extraction

The chatbot automatically extracts recommendations from conversations:
- Detects actionable suggestions in AI responses
- Categorizes by type (yoga, diet, lifestyle, meditation)
- Links to dosha type when applicable
- Adds to user's recommendation list
- Tracks completion and adherence

---

## 🧪 Development

### Running Tests

```bash
# Backend tests (if available)
cd backend
pytest

# Frontend tests
cd frontend
npm run test
```

### Code Quality

```bash
# Frontend linting
cd frontend
npm run lint

# Backend formatting
cd backend
black app/
flake8 app/
```

### Building for Production

**Backend:**
```bash
# The FastAPI app can be deployed with:
gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker
```

**Frontend:**
```bash
cd frontend
npm run build
# Output in dist/ directory
```

---

## 📚 API Documentation

Once the backend is running, visit:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### Key API Endpoints

**Authentication:**
- `POST /api/v1/auth/register` - User registration
- `POST /api/v1/auth/login` - User login
- `POST /api/v1/auth/refresh` - Refresh token

**Emotions:**
- `POST /api/v1/emotions` - Log emotion entry
- `GET /api/v1/emotions/history` - Get emotion timeline
- `GET /api/v1/emotions/analysis` - Emotion analytics

**Dosha:**
- `POST /api/v1/dosha/quiz` - Submit quiz results
- `GET /api/v1/dosha/profile` - Get user's dosha profile
- `GET /api/v1/dosha/recommendations` - Dosha-based recommendations

**AI Chatbot:**
- `POST /api/v1/chatbot/message` - Send message to AI
- `GET /api/v1/chatbot/history` - Conversation history

**Progress:**
- `GET /api/v1/progress/dashboard-metrics` - Live dashboard data
- `GET /api/v1/progress/analytics` - Historical analytics

**Wellness:**
- `GET /api/v1/yoga/library` - Yoga pose library
- `POST /api/v1/practice/session` - Log practice session
- `GET /api/v1/meals` - Meal tracking

*...and 40+ more endpoints*

---

## 🤝 Contributing

This is a proprietary project. Contributions are not currently accepted.

---

## 🐛 Troubleshooting

### Common Issues

**Backend won't start:**
- Ensure virtual environment is activated
- Check all environment variables are set
- Verify Supabase connection
- Check Python version (3.10+ required)

**Frontend build errors:**
- Clear node_modules: `rm -rf node_modules && npm install`
- Check Node.js version (18+ required)
- Verify all environment variables

**Database connection issues:**
- Verify DATABASE_URL format
- Check Supabase project is active
- Ensure pgvector extension is enabled

**ML models not loading:**
- First run downloads models (may take time)
- Check internet connection
- Verify disk space for model cache

**API key errors:**
- Double-check all API keys are correct
- Ensure no extra spaces in .env file
- Verify API quotas haven't been exceeded

---

## 📄 License

Copyright © 2026 Nirvami. All rights reserved.

This is proprietary software. Unauthorized copying, modification, distribution, or use of this software, via any medium, is strictly prohibited.

---

## 👥 Team & Contact

**Project Lead**: Your Name  
**Email**: contact@nirvami.com  
**Website**: https://nirvami.com

---

## 🙏 Acknowledgments

- **Ayurvedic Wisdom**: Based on traditional Ayurvedic texts and modern practitioners
- **AI Models**: 
  - Google Gemini for conversational AI
  - HuggingFace for emotion detection models
  - Sentence Transformers for RAG embeddings
- **Open Source**: Built with amazing open-source technologies

---

## 📈 Roadmap

### Upcoming Features (v2.1)
- [ ] Mobile app (React Native)
- [ ] Smartwatch integration (Fitbit, Garmin)
- [ ] Social features (share progress, community)
- [ ] Advanced analytics with ML predictions
- [ ] Meditation timer with guided sessions
- [ ] Ayurvedic recipe database
- [ ] Practitioner portal for health coaches

### Future Vision (v3.0)
- [ ] Voice-based journaling
- [ ] AR yoga instructor
- [ ] Personalized herbal supplement recommendations
- [ ] Integration with electronic health records
- [ ] Multi-language support
- [ ] Offline mode capabilities

---

<div align="center">


*Empowering individuals through AI-driven holistic health solutions*

### Version 2.0.0 • Production Ready ✅

Last Updated: January 9, 2026

---

**[Homepage](https://nirvami.com)** • **[Documentation](https://docs.nirvami.com)** • **[Support](mailto:support@nirvami.com)**

</div>
