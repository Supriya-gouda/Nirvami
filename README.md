# Nirvami - AI-Powered Mental Wellness Platform

[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![React](https://img.shields.io/badge/React-18-61DAFB.svg)](https://reactjs.org/)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.0-3178C6.svg)](https://www.typescriptlang.org/)

An intelligent mental health companion that bridges ancient Ayurvedic wisdom with modern AI technology for personalized mental wellness support.

**Last Updated**: December 13, 2024

---

## 📸 Platform Preview

![Nirvami Home Page](HomePage.png)
![Nirvami Dashboard](Dashborad.png)

---

## ✨ Features

- **🧠 AI Emotion Detection**: 7 emotion states with ML-powered analysis (RoBERTa go_emotions)
- **🎨 Aura Visualization**: Dynamic 3D aura sphere with 9 colors based on emotions
- **🧘 Ayurvedic Dosha**: Personalized Vata/Pitta/Kapha recommendations
- **💪 Wellness Score**: Multi-dimensional scoring (emotion, physical, lifestyle)
- **📊 Wearable Integration**: Manual entry + Apple Health XML upload with anomaly detection
- **🍽️ Meal Tracking**: AI-powered meal-emotion correlation analysis
- **🧘‍♀️ Yoga & Sound**: 50+ poses with dosha-specific sequences
- **📅 Daily Routines**: Ayurvedic dinacharya tracking
- **💬 AI Chatbot**: Google Gemini with automatic recommendation extraction
- **🔔 Smart Alerts**: In-app + SMS notifications for health concerns

---

## 🏗️ Technology Stack

**Frontend**: React 18 + TypeScript, TailwindCSS, Framer Motion, Axios, Vite  
**Backend**: FastAPI (Python 3.10+), Supabase PostgreSQL, JWT Auth  
**AI Models**: Google Gemini (gemini-flash-latest), RoBERTa go_emotions (28→7 emotions), MiniLM-L6-v2 (embeddings)  
**Services**: Twilio SMS, Redis (RQ jobs)

---

## 🚀 Quick Start

### Prerequisites
- Python 3.10+ | Node.js 18+ | Supabase Account | Google Gemini API Key

### Installation

```bash
# 1. Clone repository
git clone https://github.com/Supriya-gouda/Nirvami.git
cd Nirvami

# 2. Backend setup
cd backend
python -m venv venv
.\venv\Scripts\Activate.ps1  # Windows PowerShell
pip install -r requirements.txt
cp .env.example .env  # Edit with your credentials
python run_dev.py  # Runs on http://localhost:8000

# 3. Frontend setup (new terminal)
cd frontend
npm install
cp .env.example .env.local  # Edit with your credentials
npm run dev  # Runs on http://localhost:3000
```

### Environment Variables

**Backend (.env)**:
```env
SUPABASE_URL=your_supabase_url
SUPABASE_KEY=your_supabase_key
SUPABASE_SERVICE_ROLE_KEY=your_service_role_key
GEMINI_API_KEY=your_gemini_key
TWILIO_ACCOUNT_SID=your_twilio_sid  # Optional
TWILIO_AUTH_TOKEN=your_twilio_token  # Optional
TWILIO_PHONE_NUMBER=+1234567890  # Optional
```

**Frontend (.env.local)**:
```env
VITE_API_URL=http://localhost:8000
VITE_SUPABASE_URL=your_supabase_url
VITE_SUPABASE_ANON_KEY=your_supabase_key
```

**Note**: ML models (~300MB) auto-download on first run (2-5 mins).

---

## � Documentation

For complete documentation including API reference, database schema, detailed features, and troubleshooting, see:

- **[DOCUMENTATION.md](DOCUMENTATION.md)** - Complete technical documentation (includes project structure)
- **[SETUP_GUIDE.md](SETUP_GUIDE.md)** - Detailed installation and setup guide
- **[API Docs](http://localhost:8000/docs)** - Interactive Swagger UI (when backend running)

---

## 📄 License

Copyright © 2025 Nirvami. All rights reserved.

---

## 🙏 Acknowledgments

Built with: Google Gemini AI • Supabase • Twilio • Hugging Face • Ayurvedic Wisdom

---

<<<<<<< HEAD
**Repository**: [github.com/Supriya-gouda/Nirvami](https://github.com/Supriya-gouda/Nirvami)  
**Version**: 1.0.0 (December 2024)
=======
<div align="center">

**Built with ❤️ for mental wellness**

*Empowering individuals through AI-driven holistic health solutions*

Last Updated: December 8, 2024

</div>
- **Framer Motion**: Beautiful UI animations
- **Open Source Community**: ML models and libraries
>>>>>>> 8d6bf0a58d9b13bf19d2a5853b77dfea6be2a018
