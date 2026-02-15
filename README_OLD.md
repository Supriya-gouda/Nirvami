# 🌟 Nirvami - AI-Powered Holistic Wellness Platform

[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![React](https://img.shields.io/badge/React-18-61DAFB.svg)](https://reactjs.org/)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.0-3178C6.svg)](https://www.typescriptlang.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-009688.svg)](https://fastapi.tiangolo.com/)

An intelligent mental health companion that seamlessly integrates **ancient Ayurvedic wisdom** with **cutting-edge AI technology** to provide personalized mental wellness support, emotional intelligence, and holistic health tracking.

**Version**: 2.0.0 | **Status**: Production Ready ✅ | **Last Updated**: January 6, 2026

---

## 📸 Platform Preview

![Nirvami Home Page](HomePage.png)
*Beautiful landing page with smooth animations*

![Nirvami Dashboard](Dashborad.png)
*Comprehensive wellness dashboard*

---

## ✨ Core Features

### 🤖 AI-Powered Intelligence
- **ML Emotion Detection**: RoBERTa model (28→7 emotions) with confidence scoring
- **Google Gemini Integration**: Context-aware AI with RAG
- **Auto Recommendation Extraction**: Parses chat for actionable wellness items
- **Crisis Detection**: Intelligent alert system

### 🎨 Visualization & Tracking
- **3D Aura Sphere**: 9 distinct colors based on emotions
- **Emotion History**: Timeline with trends and analytics
- **Progress Dashboard**: 7 live metrics + 3 interactive graphs
- **Mood Correlation**: Food-emotion analysis

### 🧘 Ayurvedic System
- **Dosha Quiz**: 12-question Vata/Pitta/Kapha assessment
- **Dual/Tri-Dosha Detection**: Smart categorization
- **Personalized Recommendations**: Yoga, diet, lifestyle
- **Dynamic Balance Display**: Real-time dosha percentages

### 📊 Wellness Analytics
**Live Metrics (Today's Data):**
- Average Mood (1-10 scale)
- Stress Level (emotion + wearable)
- Total/Completed Recommendations
- Live Adherence Percentage

**Historical Metrics (Until Yesterday):**
- Consistency Score (7-day streak = 10/10)
- Wellness Score (40% emotion + 30% engagement + 30% consistency)

### 🍽️ Nutrition & Health
- **Meal Tracking**: Breakfast, lunch, dinner, snacks
- **Mood-Food Analysis**: AI-powered correlations
- **Wearable Integration**: Manual + Apple Health XML upload
- **Anomaly Detection**: Flags unusual health metrics

### 🧘‍♀️ Practice & Routines
- **Yoga Library**: 50+ poses with dosha tags
- **Sound Therapy**: Curated meditation tracks
- **Daily Routines**: Ayurvedic dinacharya tracking
- **Session Logging**: Track practice with ratings

---

## 🏗️ Technology Stack

**Frontend**: React 18, TypeScript, TailwindCSS, Framer Motion, Recharts, Vite  
**Backend**: FastAPI, PostgreSQL (Supabase), JWT Auth, Redis  
**AI**: Google Gemini 1.5 Flash, RoBERTa go_emotions, MiniLM-L6-v2  
**Services**: Twilio SMS, YouTube API

---

## 📁 Project Structure

```
Nirvami/
├── frontend/                 # React TypeScript App
│   ├── src/
│   │   ├── components/      # Dashboard, Chat, Aura, Emotion, Dosha, etc.
│   │   ├── pages/           # Journal
│   │   ├── services/        # API client (50+ endpoints)
│   │   ├── contexts/        # Auth state
│   │   └── types/           # TypeScript definitions
│   ├── .env.example
│   └── package.json
│
├── backend/                  # FastAPI Python Backend
│   ├── app/
│   │   ├── api/routes/      # 20+ route modules
│   │   ├── services/        # Business logic
│   │   ├── ml/              # Model manager
│   │   ├── models/          # Pydantic schemas
│   │   └── utils/           # Auth, database
│   ├── database/
│   │   └── schema.sql       # Complete DB schema
│   ├── scripts/             # Seed scripts
│   ├── .env.example
│   └── requirements.txt
│
├── README.md
├── HomePage.png
└── Dashborad.png
```

---

## 🚀 Quick Start

### Prerequisites
- Python 3.10+, Node.js 18+
- Supabase account
- Google Gemini API Key
- YouTube API Key

### Installation

```bash
# Clone repository
git clone https://github.com/yourusername/Nirvami.git
cd Nirvami

# Backend setup
cd backend
python -m venv venv
.\venv\Scripts\Activate.ps1  # Windows
pip install -r requirements.txt
cp .env.example .env  # Edit with your credentials
python scripts/apply_schema.py
python run_dev.py  # http://localhost:8000

# Frontend setup (new terminal)
cd frontend
npm install
cp .env.example .env  # Edit with your credentials
npm run dev  # http://localhost:5173
```

### Environment Variables

**Backend (.env):**
```env
SUPABASE_URL=your-url
SUPABASE_KEY=your-key
SUPABASE_SERVICE_ROLE_KEY=your-service-key
GEMINI_API_KEY=your-gemini-key
YOUTUBE_API_KEY=your-youtube-key
DATABASE_URL=postgresql://...
# Optional: TWILIO credentials for SMS
```

**Frontend (.env):**
```env
VITE_API_URL=http://localhost:8000
VITE_SUPABASE_URL=your-url
VITE_SUPABASE_ANON_KEY=your-key
VITE_YOUTUBE_API_KEY=your-youtube-key
```

---

## 📊 Key Implementations

### Progress Analytics
- **Live Today Metrics**: Mood, stress, recommendations, adherence
- **Yesterday Historical**: Consistency, wellness scores
- **3 Graphs**: Emotion trends, wellness trend, adherence trend

### Dosha Scoring
- Simple counting: 1 point per answer
- Dual dosha: Top 2 within 10%
- Tri-dosha: All 3 within 10%

### Emotion-to-Aura Mapping
- Joy → Yellow, Love → Pink, Calm → Blue
- Stress → Gray, Anger → Red, Sadness → Dark Blue

---

## 📄 License

Copyright © 2026 Nirvami. All rights reserved.

---

<div align="center">

**Built with ❤️ for Mental Wellness**

*Empowering individuals through AI-driven holistic health solutions*

**Version 2.0.0** • Production Ready ✅

Last Updated: January 6, 2026

</div>
