# Quick Test Guide: Journal Emotion Detection

## 🚀 Step 1: Restart Backend

**REQUIRED - Changes won't work without restart!**

```bash
# Stop current backend (Ctrl+C)
# Then restart:
cd backend
python run_dev.py
```

## 🧪 Step 2: Run Test Script

```bash
cd backend
python test_journal_emotion.py
```

**Expected output:**
```
✅ PASS | Anxious Text: fear (0.51) from ml
✅ SUCCESS: Required test case passed (not neutral)
```

**If you see:**
```
❌ FAIL | Anxious Text: neutral (0.50) from rules
❌ CRITICAL FAILURE: Required test case returned neutral!
```
→ Backend not restarted or ML model not loading

## 🌐 Step 3: Test in UI

1. **Open Journal page** in browser
2. **Write this exact text:**
   ```
   I felt constantly on edge today. Even small tasks took more effort 
   than usual, and I kept worrying about whether I was doing enough.
   ```
3. **Click 💾 Save Entry**
4. **Check inline feedback:**
   - Should show: fear/anxiety/sadness (NOT neutral)
   - Should show: 40-65% confidence (NOT 50%)

## 🔍 Step 4: Verify Logs

### Backend Terminal Should Show:
```
[EMOTION] Detecting emotion for journal (threshold: 0.40)
[EMOTION] Text length: 135 chars
[EMOTION] ML returned: fear @ 0.51
[EMOTION] ML confidence 0.51 >= 0.40 → ACCEPTED
[JOURNAL][EMOTION] Detected: fear (confidence: 0.51)
[JOURNAL][EMOTION] Source: ml
[JOURNAL][DB] emotion=fear, confidence=0.51
```

### Browser Console Should Show:
```
[Journal] Save successful
[Journal] Emotion from backend: fear (0.51)
[Journal] Full response: {emotion: "fear", emotion_confidence: 0.51, ...}
```

## ✅ Success Criteria

- [ ] Test script passes (not neutral)
- [ ] UI shows non-neutral emotion
- [ ] Backend logs show `Source: ml`
- [ ] Backend logs show `threshold: 0.40`
- [ ] Confidence is NOT exactly 0.50
- [ ] Reload preserves the emotion

## ❌ Failure Indicators

**Backend logs show `threshold: 0.55`:**
→ Backend not restarted, still using old code

**Backend logs show `Source: rules`:**
→ ML model failed to load or confidence still too low

**UI shows neutral (50%):**
→ Fell back to rule-based detection

**No `[EMOTION]` logs:**
→ emotion_service not being called

## 🐛 Troubleshooting

### Problem: Still getting neutral

**Solution 1:** Verify backend restarted
```bash
# In backend terminal, you should see on startup:
Loading emotion model: j-hartmann/emotion-english-distilroberta-base
✓ Emotion model loaded successfully
```

**Solution 2:** Check threshold in logs
```bash
# Should see:
[EMOTION] Detecting emotion for journal (threshold: 0.40)

# NOT:
[EMOTION] Detecting emotion for journal (threshold: 0.55)
```

**Solution 3:** Try more explicit text
```
I'm feeling really anxious and worried. My heart is racing 
and I can't stop thinking about all the things that could go wrong.
```

### Problem: No logs appearing

**Solution:** Check log level
```python
# In backend, logs use logging.info
# Make sure logging is configured in run_dev.py
```

## 📊 Different Test Cases

### Test 1: Anxiety (REQUIRED)
```
I felt constantly on edge today. Even small tasks took more effort 
than usual, and I kept worrying about whether I was doing enough.
```
**Expected:** fear/anxiety, confidence 0.45-0.65

### Test 2: Joy
```
Today was incredible! I finally achieved my goal and I'm so proud 
of myself. Everything fell into place perfectly and I feel amazing.
```
**Expected:** joy, confidence 0.70-0.90

### Test 3: Sadness
```
I miss my old friends so much. Everything feels different now and 
I feel really alone. Nothing seems to bring me joy anymore.
```
**Expected:** sadness, confidence 0.55-0.75

### Test 4: Short Text (Should be neutral)
```
okay
```
**Expected:** neutral, confidence 0.50 (too short for ML)

## 🎯 Final Verification

If ALL these pass, emotion detection is working:

1. ✅ Test script: `python test_journal_emotion.py` → PASS
2. ✅ Backend logs: Show `threshold: 0.40` and `Source: ml`
3. ✅ UI feedback: Shows non-neutral emotion for anxious text
4. ✅ Confidence: Varies (not always 50%)
5. ✅ Persistence: Reload shows same emotion
