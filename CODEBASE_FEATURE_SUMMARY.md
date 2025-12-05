# Nirvami — Codebase Feature Summary

This file is a consolidated, single-file summary of the Nirvami repository features, implementation details, file references, data flows, and suggested next steps. It combines the repository analysis performed on December 4, 2025.

**Overview**
- **Backend:** `backend/` — FastAPI application entry at `backend/app/main.py`. Uses Supabase for DB and auth, optional local ML models, and Google Gemini integration.
- **Frontend:** `frontend/` — React + Vite app with UI components in `frontend/src/components/`.
- **ML models cache:** `models_cache/` — local model blobs for offline ML usage.
- **Scripts & seeds:** `backend/scripts/` — data seeding and migration helper scripts.

**How I analyzed**
- Scanned repository structure and service list under `backend/app/services/`.
- Opened key backend files: `backend/app/main.py`, `backend/app/utils/database.py`, `backend/app/utils/auth.py`, `backend/app/models/schemas.py`, selected service implementations (`gemini_chatbot.py`, `rag_service.py`, `apple_health_xml_parser.py`, `wearable_service_v2.py`, `emotion_service.py`, `ml/model_manager.py`).
- Reviewed representative frontend pages: `ChatbotPage.tsx`, `AuraVisualizationPage.tsx`, `DoshaQuizPage.tsx`, `DevicePage.tsx`.

**High-level features (by area)**

**Authentication & Database**
- **Provider:** Supabase (DB + Auth). Key helpers: `backend/app/utils/auth.py`, `backend/app/utils/database.py`.
- **Auth flows:** Token verification via `supabase.auth.get_user(token)`; dev fallback `get_current_user_id()` returns test UUID when unauthenticated.
- **DB client:** `SupabaseClient.get_client()` supports both normal and service-role clients (`use_service_role=True`) for RLS bypass operations.

**API & Routing**
- Entry point: `backend/app/main.py` — registers routers for `auth`, `profile`, `chat`, `emotions`, `aura`, `wellness`, `dosha`, `meals`, `wearable`, `wearable_v2`, `watch`, `analytics`, `alerts`, `admin`, `yoga`, `routines`, `dinacharya`, `journal`, `goals`.
- Health check endpoint: `/health`.
- Global exception handler returns JSON 500 for unhandled exceptions.

**ML & Model Management**
- `backend/app/ml/model_manager.py` loads:
  - Embedding model (SentenceTransformer) — `settings.EMBEDDING_MODEL`.
  - Emotion classifier (Hugging Face pipeline) — `settings.EMOTION_MODEL`.
  - LLM (FLAN-T5 style) for local generation — `settings.LLM_MODEL`.
- Exposes `generate_embedding`, `batch_generate_embeddings`, `detect_emotion`, `generate_response`.
- Models are optional — app respects `settings.ENABLE_ML_MODELS` and provides rule-based fallbacks.

**Chat / Conversational Assistant**
- Frontend: `frontend/src/components/ChatbotPage.tsx` — message UI, voice simulation, crisis banner, history retrieval via `api.getChatHistory`.
- Backend Gemini wrapper: `backend/app/services/gemini_chatbot.py` — integrates Google Gemini (`genai`) with a strict system instruction limiting scope to Yoga & Ayurveda and crisis handling.
- RAG (Retrieval-Augmented Generation): `backend/app/services/rag_service.py` — retrieves Ayurvedic resources from `ayurveda_resources` table using a Supabase RPC `match_ayurveda_resources` and builds context-aware prompts including dosha and emotion context.
- Flow: frontend sends message → backend chat endpoint uses RAG + Gemini (or local LLM) → emotion detection → stores message + response, returns to frontend. Crisis detection flags front-end alert.

**Emotion Detection & Logging**
- Service: `backend/app/services/emotion_service.py`.
- Supports ML pipeline detection (via `model_manager.emotion_pipeline`) or a rule-based keyword fallback.
- `detect_contextual_emotion` aggregates recent messages, weighting recency.
- `create_emotion_log` prepares log entries for DB; `analyze_sentiment_trend` computes distribution and valence.

**Aura Visualization**
- Frontend: `frontend/src/components/AuraVisualizationPage.tsx` — displays aura color, gradient, intensity, chakra, traits, and small insights.
- Backend: `backend/app/services/aura_service.py` (present in services directory) computes aura from emotion logs and wellness/wearable data and stores `aura_entries`.

**Dosha (Ayurvedic Constitution)**
- Frontend: `frontend/src/components/DoshaQuizPage.tsx` — 10-question quiz, computes scores, posts to backend, and displays diet/lifestyle/yoga/meditation recommendations.
- Backend: `backend/app/services/dosha_service.py` computes `vata/pitta/kapha` scores and returns `DoshaRecommendation`s from `ayurveda_resources`.

**Wearables & Health Ingestion**
- Apple Health XML parser: `backend/app/services/apple_health_xml_parser.py` parses HealthKit export XML, extracts heart rate, steps, sleep segments, calories, HRV; aggregates into daily snapshots matching `wearable_snapshots` schema and infers `stress_level`.
- Wearable service v2: `backend/app/services/wearable_service_v2.py` — `save_manual_entry()`, `get_latest()`, `get_all_for_user()`, `analyze_health_risks()` which applies heuristics to identify health risks and returns prioritized recommendations.
- Frontend: `frontend/src/components/DevicePage.tsx`, `WatchDataUpload.tsx`, `ManualHealthEntry.tsx` for uploading XML and manual entries.

**Meals & Emotion Correlation**
- Schemas in `backend/app/models/schemas.py` define `Meal` and `MealEmotionCorrelation`.
- Backend `meal_service.py` stores meals and correlates meal entries with emotion logs (implementation present in services).

**Routines, Dinacharya, Yoga, Sound Therapy**
- Frontend pages: `DailyRoutinesPage.tsx`, `DinacharyaPage.tsx`, `YogaLifestylePage.tsx`, `SoundTherapyPage.tsx` provide curated content.
- Backend routers `routines`, `dinacharya`, `yoga` serve content and may schedule reminders via worker jobs.

**Analytics & Progress**
- Frontend: `ProgressAnalyticsPage.tsx`, `EmotionHistoryPage.tsx`, `AuraHistory.tsx` show emotion trends, wellness trends, and analytics.
- Backend: `analytics` router and associated services aggregate emotion logs, wellness scores, and wearable trends (`AnalyticsResponse` schema exists).

**Alerts & Crisis Detection**
- `crisis_detector.py` identifies crisis language and flags alerts.
- `alert_service.py` manages alert creation, severity, and notification channels.
- Frontend: `NotificationCenter.tsx` and in-chat crisis banners; wearable analysis can also create alerts.

**RAG / Ayurvedic Knowledgebase**
- `rag_service.py` uses embeddings to retrieve relevant Ayurvedic documents from `ayurveda_resources` and constructs prompts tailored to user `dosha` and current emotion.
- Seed data and scripts: `backend/scripts/seed_ayurveda_resources.py` and related seeders.

**Workers & Background Jobs**
- `backend/app/workers/` contains `jobs.py`, `scheduler.py`, `worker.py` used for scheduled tasks such as daily summaries, notifications, background embedding indexing, and data cleanup.

**Data Models & Schemas**
- Central Pydantic schemas: `backend/app/models/schemas.py`. Notable models:
  - `UserProfile`, `UserPreferences`
  - Chat: `Message`, `ChatSession`, `ChatResponse`
  - Emotions: `EmotionLog`, `EmotionDetectionResponse`, `EmotionAggregate`
  - Aura: `AuraEntry`, `AuraInsight`
  - Wellness: `WellnessScore`
  - Dosha: `DoshaAssessment`, `DoshaRecommendation`
  - Wearable: `WearableSnapshot`, `WearableIntakeRequest`, `ManualEntryRequest`
  - Analytics & Alerts: `AnalyticsResponse`, `Alert`, `CreateAlertRequest`

**Security & Configuration**
- `backend/app/config.py` centralizes configuration: Supabase keys, Gemini API key, model names, `ENABLE_ML_MODELS`, `MODEL_CACHE_DIR`, `ENVIRONMENT`, `API_VERSION`.
- CORS: development allows origins `*` in `main.py`.

**Notable Implementation Details & Heuristics**
- Emotion detection has ML pipeline and keyword-based fallback. The fallback uses a small keyword dictionary and computes confidence heuristically.
- Apple Health parsing validates ranges and aggregates time-series into daily snapshots, inferring stress via HR/HRV/sleep heuristics.
- Wearable risk analysis applies multi-rule heuristics and combines signals to detect compound issues (e.g., low sleep + high HR => burnout alert).
- Chatbot system instruction enforces scope, crisis-handling scripts, and uses Gemini when configured; local LLM fallback via `ModelManager.generate_response` is available.

**File Map (representative)**
- `backend/app/main.py` — app entry and router registration
- `backend/app/utils/database.py` — Supabase client
- `backend/app/utils/auth.py` — auth dependencies
- `backend/app/models/schemas.py` — central Pydantic schemas
- `backend/app/ml/model_manager.py` — model loading / utilities
- `backend/app/services/gemini_chatbot.py` — Gemini wrapper and fallback
- `backend/app/services/rag_service.py` — retrieval & prompt builder
- `backend/app/services/emotion_service.py` — emotion detection
- `backend/app/services/apple_health_xml_parser.py` — XML parsing & aggregation
- `backend/app/services/wearable_service_v2.py` — wearable storage & analysis
- `backend/app/services/dosha_service.py` — dosha assessment & recommendations
- `backend/app/services/*` — `meal_service.py`, `aura_service.py`, `alert_service.py`, `crisis_detector.py`, `watch_service.py`, etc.
- `backend/app/workers/` — scheduled jobs
- `backend/database/schema.sql` — DB schema (review this for exact table columns)
- `backend/scripts/` — seed and schema migration scripts
- `frontend/src/components/` — UI pages and components (ChatbotPage, AuraVisualizationPage, DoshaQuizPage, DevicePage, etc.)

**Known Limitations & Assumptions**
- Gemini and local ML models require API keys and/or local model files — must be configured to enable full AI features.
- Supabase DB and RPC functions (e.g., `match_ayurveda_resources`) must exist for RAG similarity search to work.
- Apple Watch direct integration is via XML upload (export). Real-time HealthKit integration is not implemented in the web client.
- Voice input on the frontend is simulated — a Web Speech API integration would be needed to capture real voice.

**Suggested Next Steps**
1. Generate an API reference by scanning `backend/app/api/routes/` to list endpoints, methods, and request/response schemas — I can produce this as a separate `API_SPEC.md` or OpenAPI export.
2. Produce a DB schema summary by opening `backend/database/schema.sql` (I can extract exact table definitions).
3. If you want runnable verification, provide Supabase credentials and model API keys (or enable mock mode) and I can run the backend locally and exercise key endpoints.
4. Create sequence diagrams for major flows (Chat RAG flow, Wearable ingestion flow) if helpful.

**Quick local run hints**
 - Start backend (PowerShell):
```powershell
cd backend
.\start-dev.ps1
```

 - Frontend (from repo root):
```powershell
cd frontend
npm install
npm run dev
```

**If you want more**
- I can produce: full endpoint list and sample cURL requests, a cleaned `README.md` for developers, or export this summary in another format (HTML, PDF). Tell me which format you prefer.

---
Generated by repository analysis on 2025-12-04. If you'd like edits, extra detail per-feature, or an API spec extracted to a second file, tell me which next step to take.
