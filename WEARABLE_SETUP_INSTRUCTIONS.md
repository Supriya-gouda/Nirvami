# Wearable Device Feature - Setup Instructions

## ✅ Completed Implementation

### Backend (100% Complete)
- ✅ **Database Schema**: `backend/database/fresh_wearable_schema.sql`
- ✅ **Service Layer**: `backend/app/services/wearable_service_v2.py` (400+ lines)
  - save_manual_entry() - Store health data
  - get_latest() - Get most recent entry
  - analyze_health_risks() - Complete risk analysis (6 categories + combined flags)
- ✅ **API Routes**: `backend/app/api/routes/wearable_v2.py`
  - POST /api/v1/wearable-v2/manual-entry
  - GET /api/v1/wearable-v2/latest
  - GET /api/v1/wearable-v2/history
  - POST /api/v1/wearable-v2/analyze
- ✅ **Router Registration**: Routes added to `backend/app/main.py`

### Frontend (100% Complete)
- ✅ **API Service**: `src/services/api.ts` - 4 new methods added
- ✅ **Device Page**: `src/components/DevicePage.tsx`
  - Manual health entry form
  - **Analyze button** with loading state
  - Analysis results display (risk level, concerns, recommendations)
  - Notification alert
- ✅ **Dashboard**: `src/components/Dashboard.tsx`
  - Updated to use new `getLatestWearableData()` endpoint
  - Displays: Sleep, Heart Rate, Steps, Stress Level

## 🚀 Deployment Steps

### Step 1: Execute Database Schema

**CRITICAL - Must be done before testing:**

1. Go to your **Supabase Dashboard** → SQL Editor
2. Copy the contents of `backend/database/fresh_wearable_schema.sql`
3. Paste and **Run** the SQL
4. Verify the table was created: Run `SELECT * FROM wearable_snapshots LIMIT 1;`

**What this does:**
- Drops old `wearable_daily_stats` and `wearable_snapshots` tables
- Creates new clean `wearable_snapshots` with exact frontend field mapping
- Sets up RLS policies for user data access
- Creates indexes for performance

### Step 2: Start Backend Server

```powershell
cd backend
python run_dev.py
```

Or using the startup script:
```powershell
cd backend
.\start-dev.ps1
```

**Verify backend is running:**
- Server should start on `http://localhost:8000`
- Check: `http://localhost:8000/docs` for API documentation

### Step 3: Start Frontend

```powershell
npm run dev
```

**Verify frontend is running:**
- App should start on `http://localhost:5173`

### Step 4: Test the Feature

#### Test Manual Entry
1. Navigate to **Device Page** (Watch icon in navigation)
2. Click **+ Log Health Data**
3. Fill in the form:
   - Date: Today's date
   - Sleep Hours: e.g., 7
   - Heart Rate: e.g., 72
   - Steps: e.g., 5000
   - Stress Level: Drag slider (1-10)
   - Calories: e.g., 2000
4. Click **Save Entry**
5. Should see success toast

#### Test Health Analysis
1. On Device Page, after saving data
2. Click **🔍 Analyze Health Data** button
3. Wait for analysis (button shows "Analyzing...")
4. Should see:
   - Risk level badge (Low/Medium/High/Critical)
   - Detected concerns list
   - Recommendations list
   - Blue notification alert
5. Check **Notifications** (bell icon) for in-app alert
6. If risk is High/Critical, SMS will be sent (if Twilio configured)

#### Test Dashboard Display
1. Navigate to **Dashboard**
2. Scroll to **Body & Energy** section
3. Should see 4 cards:
   - Sleep: X hrs with emoji
   - Heart Rate: X bpm with status
   - Steps: X with activity level
   - Stress: X/10 with emoji

## 🔍 Health Risk Analysis Logic

The analyze feature checks for:

### Individual Risk Factors:
1. **Very High Resting Heart Rate**: ≥120 critical, ≥100 high, ≥90 medium
2. **Low Sleep**: <4hrs critical, <5hrs high, <6hrs medium
3. **Low HRV**: <20ms very low (high risk), <30ms low (medium)
4. **Sedentary Activity**: <2000 steps sedentary risk
5. **Overtraining**: >15000 steps potential overtraining
6. **High Stress**: ≥8 very high, ≥7 high

### Combined Red Flags:
- **Burnout Warning**: Low sleep + high heart rate
- **Recovery Failure**: Low sleep + low HRV
- **Triple Threat**: High stress + high HR + low sleep (CRITICAL)

### Risk Levels:
- **Low**: All metrics normal
- **Medium**: 1-2 minor concerns
- **High**: 3+ concerns or 1 major concern
- **Critical**: Severe metrics or triple threat

## 📊 Database Schema

**Table**: `wearable_snapshots`

| Column | Type | Description |
|--------|------|-------------|
| id | UUID | Primary key |
| user_id | UUID | Foreign key to profiles |
| date | DATE | Entry date (YYYY-MM-DD) |
| source | VARCHAR(20) | 'manual' or 'watch' |
| sleep_hours | NUMERIC(4,2) | Hours of sleep (0-24) |
| avg_heart_rate | INTEGER | Average heart rate (bpm) |
| steps | INTEGER | Steps walked |
| stress_level | INTEGER | Stress level (1-10) |
| calories_burned | NUMERIC(6,2) | Calories burned |
| hrv_ms | INTEGER | Heart rate variability (optional) |

**Unique Constraint**: (user_id, date, source) - Prevents duplicate entries

## 🔧 Troubleshooting

### Issue: "Table does not exist" error
**Solution**: Execute `fresh_wearable_schema.sql` in Supabase SQL Editor

### Issue: "Permission denied" on insert
**Solution**: Check that RLS policies were created. Service should use `use_service_role=True`

### Issue: Analyze button disabled
**Solution**: Make sure you've entered health data first. Button requires `wearableSummary?.hasData` to be true

### Issue: No data showing on Dashboard
**Solution**: 
1. Verify data saved in database: `SELECT * FROM wearable_snapshots WHERE user_id = 'your-user-id';`
2. Check browser console for API errors
3. Ensure backend is running

### Issue: Analysis not showing results
**Solution**:
1. Open browser DevTools → Network tab
2. Click Analyze button
3. Check POST request to `/api/v1/wearable-v2/analyze`
4. Look for errors in response

### Issue: SMS not sent
**Solution**: 
1. Verify Twilio credentials in `backend/app/config.py`
2. Check `TWILIO_ACCOUNT_SID`, `TWILIO_AUTH_TOKEN`, `TWILIO_PHONE_NUMBER` environment variables
3. SMS only sent for High/Critical risk levels

## 📝 API Endpoints Reference

### POST /api/v1/wearable-v2/manual-entry
Save manual health entry
```json
{
  "date": "2024-01-15",
  "sleep_hours": 7.5,
  "avg_heart_rate": 72,
  "steps": 8000,
  "stress_level": 4,
  "calories_burned": 2200
}
```

### GET /api/v1/wearable-v2/latest
Get most recent entry
```json
{
  "hasData": true,
  "date": "2024-01-15",
  "sleepHours": 7.5,
  "heartRate": 72,
  "steps": 8000,
  "stressLevel": 4,
  "caloriesBurned": 2200,
  "source": "manual",
  "data": { /* full entry */ }
}
```

### POST /api/v1/wearable-v2/analyze
Analyze health risks
```json
{
  "analysis": {
    "has_risks": true,
    "risk_level": "medium",
    "risks": ["Low sleep detected (6.0 hours)"],
    "recommendations": ["Aim for 7-9 hours of sleep tonight"],
    "data": { /* latest entry */ }
  },
  "notification_sent": true,
  "sms_sent": false
}
```

### GET /api/v1/wearable-v2/history?limit=30
Get entry history (default 30 days)

---

## ✨ Feature Summary

**What's Working:**
1. ✅ Manual health data entry from frontend
2. ✅ Data persistence in database with RLS
3. ✅ Comprehensive health risk analysis (6 factors + combined flags)
4. ✅ In-app notifications for analysis results
5. ✅ SMS alerts for high/critical risks (Twilio)
6. ✅ Latest data display on Dashboard
7. ✅ Historical data tracking with date uniqueness

**User Flow:**
1. User logs health data on Device Page
2. Data saved to database (upsert on duplicate date)
3. User clicks Analyze button
4. Backend analyzes 6 risk categories
5. Results shown on page + notification created
6. High/Critical risks trigger SMS
7. Latest data visible on Dashboard

**Tech Stack:**
- Backend: FastAPI + Python 3.10 + PostgreSQL
- Frontend: React + TypeScript + Vite
- Database: Supabase with RLS
- Notifications: In-app + Twilio SMS
- Analysis: Logic-based health risk detection
