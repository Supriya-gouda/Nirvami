# Nirvami Backend

AI-powered mental wellness platform with Ayurvedic intelligence - FastAPI Backend

## 🏗️ Architecture

### Tech Stack
- **Framework**: FastAPI (Python)
- **Database**: Supabase (PostgreSQL + pgvector)
- **Auth**: Supabase Auth (JWT)
- **ML Models**:
  - Emotion Detection: `SamLowe/roberta-base-go_emotions` (28 emotions mapped to 7 core emotions)
  - Emotion: `SamLowe/roberta-base-go_emotions` (go_emotions with 28 fine-grained emotions)
- **Background Jobs**: RQ (Redis Queue)
- **Notifications**: Twilio (SMS), SMTP (Email)

## 📋 Prerequisites

- Python 3.9+
- PostgreSQL (via Supabase)
- Redis
- Supabase Account
- (Optional) Twilio Account for SMS

## 🚀 Quick Start

### 1. Install Dependencies

```bash
cd backend
pip install -r requirements.txt
```

### 2. Set Up Supabase

1. Create a Supabase project at https://supabase.com
2. Run the database schema:
   ```bash
   # Copy the content of database/schema.sql and run it in Supabase SQL Editor
   ```
3. Enable pgvector extension in Supabase

4. Create the vector similarity function in Supabase SQL Editor:
   ```sql
   CREATE OR REPLACE FUNCTION match_ayurveda_resources(
     query_embedding vector(384),
     match_threshold float,
     match_count int
   )
   RETURNS TABLE (
     id uuid,
     title text,
     content text,
     category text,
     dosha_tags text[],
     similarity float
   )
   LANGUAGE sql STABLE
   AS $$
     SELECT
       id,
       title,
       content,
       category,
       dosha_tags,
       1 - (embedding <=> query_embedding) as similarity
     FROM ayurveda_resources
     WHERE 1 - (embedding <=> query_embedding) > match_threshold
     ORDER BY embedding <=> query_embedding
     LIMIT match_count;
   $$;
   ```

### 3. Configure Environment

```bash
# Copy example env file
cp .env.example .env

# Edit .env with your credentials
nano .env
```

Required environment variables:
- `SUPABASE_URL`: Your Supabase project URL
- `SUPABASE_KEY`: Supabase anon key
- `SUPABASE_SERVICE_ROLE_KEY`: Supabase service role key
- `SECRET_KEY`: JWT secret (same as Supabase JWT secret)
- `REDIS_URL`: Redis connection URL
- `DATABASE_URL`: PostgreSQL connection string

### 4. Install Redis

**Windows (using WSL or Docker):**
```bash
# Using Docker
docker run -d -p 6379:6379 redis:latest

# Or using WSL
sudo apt-get install redis-server
redis-server
```

**macOS:**
```bash
brew install redis
brew services start redis
```

**Linux:**
```bash
sudo apt-get install redis-server
sudo systemctl start redis
```

### 5. Download ML Models (First Run)

Models will auto-download on first run, but you can pre-download:

```bash
python -c "
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM

# Download models
"
```

### 6. Seed Ayurvedic Resources (Optional)

Create a script to seed initial Ayurvedic content:

```bash
python scripts/seed_ayurveda_resources.py
```

### 7. Run the Application

**Terminal 1 - FastAPI Server:**
```bash
cd backend
uvicorn app.main:app --reload --port 8000
```

**Terminal 2 - RQ Worker:**
```bash
cd backend
python -m app.workers.worker
```

**Terminal 3 - Job Scheduler:**
```bash
cd backend
python -m app.workers.scheduler
```

## 📁 Project Structure

```
backend/
├── app/
│   ├── api/
│   │   └── routes/          # API endpoints
│   │       ├── auth.py      # Authentication
│   │       ├── chat.py      # Conversational AI
│   │       ├── emotions.py  # Emotion detection
│   │       ├── aura.py      # Aura visualization
│   │       ├── wellness.py  # Wellness scoring
│   │       ├── dosha.py     # Dosha assessment
│   │       ├── meals.py     # Meal tracking
│   │       ├── wearable.py  # Wearable integration
│   │       ├── analytics.py # Analytics
│   │       ├── alerts.py    # Alerts & notifications
│   │       └── admin.py     # Admin dashboard
│   ├── ml/
│   │   └── model_manager.py # ML model loading
│   ├── models/
│   │   └── schemas.py       # Pydantic models
│   ├── services/
│   │   ├── crisis_detector.py
│   │   ├── rag_service.py
│   │   ├── alert_service.py
│   │   ├── aura_service.py
│   │   └── dosha_service.py
│   ├── utils/
│   │   ├── database.py      # Supabase client
│   │   └── auth.py          # Auth utilities
│   ├── workers/
│   │   ├── worker.py        # RQ worker
│   │   ├── jobs.py          # Background jobs
│   │   └── scheduler.py     # Job scheduler
│   ├── config.py            # Configuration
│   └── main.py              # FastAPI app
├── database/
│   └── schema.sql           # Database schema
├── requirements.txt
├── .env.example
└── README.md
```

## 🔧 API Endpoints

### Authentication
- `POST /api/v1/auth/verify` - Verify JWT token
- `GET /api/v1/auth/me` - Get current user

### Profile
- `GET /api/v1/profile/{user_id}` - Get user profile
- `PUT /api/v1/profile/{user_id}` - Update profile
- `POST /api/v1/profile/{user_id}/export` - Export user data
- `DELETE /api/v1/profile/{user_id}` - Delete account

### Chat
- `POST /api/v1/chat/send` - Send message and get AI response
- `GET /api/v1/chat/sessions` - Get chat sessions
- `GET /api/v1/chat/sessions/{id}/messages` - Get session messages

### Emotions
- `POST /api/v1/emotions/detect` - Detect emotion from text
- `GET /api/v1/emotions/logs` - Get emotion logs
- `GET /api/v1/emotions/aggregates` - Get daily aggregates

### Aura
- `GET /api/v1/aura/today` - Get today's aura
- `GET /api/v1/aura/timeline` - Get aura history

### Wellness
- `GET /api/v1/wellness/today` - Get today's wellness score
- `GET /api/v1/wellness/history` - Get wellness history

### Dosha
- `POST /api/v1/dosha/assess` - Submit dosha quiz
- `GET /api/v1/dosha/recommendations` - Get personalized recommendations

### Meals
- `POST /api/v1/meals` - Log a meal
- `GET /api/v1/meals` - Get meal history

### Wearable
- `POST /api/v1/wearable/push` - Push wearable data

### Analytics
- `GET /api/v1/analytics/{user_id}` - Get analytics data

### Alerts
- `GET /api/v1/alerts` - Get user alerts
- `GET /api/v1/alerts/notifications` - Get notifications

## 🤖 Background Jobs

### Daily Jobs (2-3 AM)
- Aggregate daily emotions
- Generate aura visualizations
- Compute wellness scores

### Hourly Jobs
- Compute meal-emotion correlations

### Every 4 Hours
- Sync and process wearable data

## 🔒 Security

- Row-Level Security (RLS) enabled on all tables
- JWT authentication for all protected endpoints
- Service role key used only for server-side operations
- Encrypted sensitive data
- CORS configured for frontend origins

## 🧪 Testing

```bash
# Run tests (TODO: Add tests)
pytest
```

## 📊 Monitoring

- RQ Dashboard: Run `rq-dashboard` to monitor jobs
- Logs: Check application logs for errors
- Supabase Dashboard: Monitor database performance

## 🚢 Deployment

### Using Docker

```dockerfile
# Dockerfile
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Using Docker Compose

```yaml
# docker-compose.yml
version: '3.8'

services:
  api:
    build: .
    ports:
      - "8000:8000"
    env_file:
      - .env
    depends_on:
      - redis

  worker:
    build: .
    command: python -m app.workers.worker
    env_file:
      - .env
    depends_on:
      - redis

  scheduler:
    build: .
    command: python -m app.workers.scheduler
    env_file:
      - .env
    depends_on:
      - redis

  redis:
    image: redis:latest
    ports:
      - "6379:6379"
```

Run with:
```bash
docker-compose up
```

## 📝 Notes

- ML models require ~2-4GB RAM
- First startup downloads models (~500MB)
- Redis is required for background jobs
- Supabase handles auth, database, and real-time features

## 🤝 Contributing

1. Create feature branch
2. Make changes
3. Add tests
4. Submit pull request

## 📄 License

MIT License

## 🆘 Troubleshooting

### Models not loading
- Check internet connection for model download
- Ensure sufficient disk space (~2GB)
- Check `MODEL_CACHE_DIR` permissions

### Redis connection errors
- Ensure Redis is running: `redis-cli ping`
- Check `REDIS_URL` in .env

### Supabase connection issues
- Verify Supabase URL and keys
- Check network/firewall settings
- Ensure database schema is applied

### Crisis alerts not sending
- Check Twilio credentials
- Verify SMTP settings
- Check user preferences for notification channels
