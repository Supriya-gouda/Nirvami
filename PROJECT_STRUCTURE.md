# Nirvami - Project Structure

## 📂 Directory Overview

```
Nirvami/
├── frontend/              # React + TypeScript frontend application
├── backend/               # FastAPI Python backend server
├── .git/                  # Git version control
├── .gitignore            # Git ignore rules (updated for new structure)
├── .vscode/              # VS Code workspace settings
└── README.md             # Main project documentation
```

## 🎨 Frontend Structure

**Location:** `frontend/`

**Tech Stack:** React 18, TypeScript, Vite, TailwindCSS, Framer Motion

**Key Directories:**
- `src/components/` - All React components (30+ feature pages)
- `src/components/ui/` - Reusable UI components (shadcn/ui)
- `src/services/` - API client with 40+ endpoints
- `src/contexts/` - React context providers
- `src/types/` - TypeScript type definitions
- `src/styles/` - Global CSS styles

**Configuration Files:**
- `package.json` - Dependencies and scripts
- `tsconfig.json` - TypeScript compiler config
- `vite.config.ts` - Vite build configuration
- `.eslintrc.json` - ESLint rules
- `.env.local` - Environment variables

**Commands:**
```bash
cd frontend
npm install          # Install dependencies
npm run dev          # Start dev server (port 5173)
npm run build        # Build for production
npm run preview      # Preview production build
```

## 🔧 Backend Structure

**Location:** `backend/`

**Tech Stack:** FastAPI, Python 3.10+, Supabase, Redis, ML Models

**Key Directories:**
- `app/api/routes/` - API endpoint handlers (9 route files)
- `app/services/` - Business logic layer
- `app/models/` - Pydantic data schemas
- `app/utils/` - Authentication, database utilities
- `app/workers/` - Background job processing
- `database/` - Database schema (consolidated schema.sql)
- `scripts/` - Setup and seeding scripts (8 scripts)
- `models_cache/` - Cached ML models

**Configuration Files:**
- `requirements.txt` - Python dependencies
- `run_dev.py` - Development server launcher
- `start-dev.ps1` - Windows PowerShell startup script
- `.env` - Environment variables (not committed)

**Commands:**
```bash
cd backend
python -m venv venv            # Create virtual environment
.\venv\Scripts\activate        # Activate venv (Windows)
pip install -r requirements.txt  # Install dependencies
python run_dev.py              # Start server (port 8000)
```

## 📊 Database Structure

**Location:** `backend/database/schema.sql`

**Consolidated Schema:** Single file containing all 30+ tables

**Key Tables:**
- `profiles` - User accounts
- `emotion_logs` - AI emotion detection
- `aura_entries` - Daily aura visualizations
- `wellness_scores` - Comprehensive wellness metrics
- `dosha_assessments` - Ayurvedic constitution
- `wearable_snapshots` - Health device data
- `daily_routines` - Ayurvedic routine tracking
- `yoga_poses` - Yoga pose library
- `sound_tracks` - Sound therapy tracks
- `meals` - Meal logging
- `messages` - Chat history
- `alerts` - Health notifications

**Features:**
- Row-Level Security (RLS) enabled
- Optimized indexes for performance
- Triggers for auto-updates
- Complete with policies and comments

## 🚀 Quick Start

### 1. Clone & Setup
```bash
git clone https://github.com/Supriya-gouda/Nirvami.git
cd Nirvami
```

### 2. Start Backend
```bash
cd backend
python -m venv venv
.\venv\Scripts\activate
pip install -r requirements.txt
# Configure .env file with API keys
python run_dev.py
```

### 3. Start Frontend
```bash
cd frontend
npm install
npm run dev
```

### 4. Access Application
- Frontend: http://localhost:5173
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

## 🔄 What Changed?

### Before Restructuring:
```
Nirvami/
├── src/              # Frontend mixed with root
├── backend/          # Backend
├── build/            # Old build files
├── package.json      # In root
├── tsconfig.json     # In root
└── Many scattered migration files
```

### After Restructuring:
```
Nirvami/
├── frontend/         # All frontend code isolated
│   ├── src/
│   ├── package.json
│   └── README.md
├── backend/          # All backend code clean
│   ├── database/schema.sql  # Single schema file
│   └── README.md
└── README.md         # Updated project docs
```

## ✅ Improvements Made

### Cleanup:
- ✅ Removed 8+ MD documentation files (redundant guides)
- ✅ Removed 28+ test scripts (kept essential setup scripts)
- ✅ Removed 7+ migration SQL files (consolidated into schema.sql)
- ✅ Removed old `build/` directory
- ✅ Removed duplicate `LandingPage.tsx` (kept LandingPageNew.tsx)

### Organization:
- ✅ Separated frontend and backend into distinct directories
- ✅ Created dedicated README for each section
- ✅ Updated main README with new structure
- ✅ Enhanced .gitignore for better coverage
- ✅ Consolidated database schema into single file

### Documentation:
- ✅ Professional README for frontend
- ✅ Professional README for backend (existing, already good)
- ✅ Updated main README with complete feature list
- ✅ Clear installation instructions for each component

## 📝 Development Workflow

### Frontend Development:
1. Navigate to `frontend/` directory
2. Make changes in `src/`
3. Hot reload automatically updates browser
4. Test API integration with backend

### Backend Development:
1. Navigate to `backend/` directory
2. Make changes in `app/`
3. Server auto-reloads on file changes
4. Test endpoints at http://localhost:8000/docs

### Database Changes:
1. Update `backend/database/schema.sql`
2. Run `python scripts/apply_schema.py`
3. Or execute SQL directly in Supabase dashboard

## 🎯 Benefits of New Structure

1. **Clear Separation** - Frontend and backend completely isolated
2. **Easy Navigation** - Find files quickly with logical structure
3. **Better Documentation** - Each component has its own README
4. **Clean Git History** - Removed unnecessary files from tracking
5. **Professional Layout** - Follows industry standard practices
6. **Easier Onboarding** - New developers can understand structure quickly
7. **Scalable** - Easy to add new features without clutter
8. **Maintainable** - Clean codebase with minimal technical debt

## 🔗 Related Documentation

- [Frontend README](frontend/README.md) - React app documentation
- [Backend README](backend/README.md) - API server documentation
- [Main README](README.md) - Project overview and features

## 📦 Total File Count

- **Frontend:** ~90 files (components, services, types, configs)
- **Backend:** ~50 files (routes, services, scripts, models)
- **Database:** 1 consolidated schema file
- **Documentation:** 4 README files
- **Configuration:** ~10 config files

**Total:** ~155 essential files (removed 40+ redundant files)
