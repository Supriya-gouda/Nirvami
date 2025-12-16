# 🚀 Quick Start: Journal Emotion Detection

## ⚡ Database Migration (REQUIRED FIRST)

### Option A: Supabase SQL Editor (Recommended)
1. Open your Supabase project
2. Go to SQL Editor
3. Run this:

```sql
ALTER TABLE journal_entries 
ADD COLUMN IF NOT EXISTS emotion VARCHAR(50);

ALTER TABLE journal_entries 
ADD COLUMN IF NOT EXISTS emotion_confidence FLOAT;
```

### Option B: Run Migration Script
```bash
cd backend
python scripts/add_journal_emotion_columns.py
```

## 🧪 Testing (After Migration)

### Test 1: Anxious Text
```
Journal Entry: "I'm really worried about the meeting tomorrow. 
What if I mess up? I can't stop thinking about it."

Expected: fear/anxiety (NOT neutral)
```

### Test 2: Happy Text
```
Journal Entry: "Today was incredible! I finally achieved my goal 
and I'm so proud of myself!"

Expected: joy (NOT neutral)
```

### Test 3: Sad Text
```
Journal Entry: "I miss my old friends. Everything feels different 
now and I feel so alone."

Expected: sadness (NOT neutral)
```

## 🔍 Verify in Console

### Backend Logs (Terminal)
```
[JOURNAL] Creating journal entry...
[JOURNAL][EMOTION] Running ML emotion detection
[JOURNAL][EMOTION] Detected: fear (confidence: 0.82)
[JOURNAL][EMOTION] Source: ml
[JOURNAL][DB] Saving entry with emotion: fear, confidence: 0.82
[JOURNAL][DB] Journal entry saved successfully
```

### Frontend Logs (Browser)
```
[Journal] Save successful
[Journal] Emotion received: fear (0.82)
```

## 🎯 Expected UI Behavior

1. **Write journal entry** → Click "💾 Save Entry" button (large, purple gradient)
2. **Inline feedback appears** below editor:
   ```
   ✅ Saved successfully
   Emotion detected: Fear 😨 (82% confidence)
   ```
3. **Colored badge** matches emotion (fear = purple, joy = yellow, etc.)
4. **Feedback auto-hides** after 10 seconds

## ❌ What NOT to See

- ❌ No browser alerts
- ❌ No "neutral" for emotional text
- ❌ No save button that's hard to find
- ❌ No disappearing entries after reload

## 🐛 Troubleshooting

### Problem: Still getting "neutral" for emotional text
**Solution:** Check backend logs. If you see "Source: rules" instead of "Source: ml", the ML model isn't loading.

### Problem: Save button not visible
**Solution:** Clear browser cache, reload page. New button is purple gradient, large, bold.

### Problem: Entries disappear after relogin
**Solution:** Check console for `[Journal] Loaded X entries for today`. Should load on every mount.

### Problem: Database errors on save
**Solution:** Run the migration SQL to add emotion columns.

## 📊 Complete Flow

```
User writes → Click Save → 
  Backend: Detect emotion with ML →
  Backend: Save to DB with emotion →
  Frontend: Show inline feedback →
  Frontend: Add to entries list →
  User sees: Emotion badge with confidence
```

## ✅ Success Indicators

- Backend logs show `[JOURNAL][EMOTION] Source: ml`
- Different journal texts produce different emotions
- Inline feedback panel appears (no alerts)
- Entries persist across page reloads
- Save button is large and prominent
