# FRONTEND TESTING INSTRUCTIONS

## Quick Test (Browser Console)

1. Open your frontend in the browser (usually http://localhost:3000 or http://localhost:5173)

2. Open Browser Developer Console (F12)

3. Manually set authentication for testing:
```javascript
// Set test authentication token in localStorage
localStorage.setItem('token', 'test-token-for-user-6bde95c9-409c-40ae-aa40-c8894ffdf8e4');

// Refresh the page to load with authentication
window.location.reload();
```

4. Navigate to Yoga/Ayurveda pages and you should see recommendations!

## Proper Login Test

1. Register/Login with these credentials:
   - Email: test.user@nirvami.com
   - Password: TestPassword123!

2. Navigate to recommendation pages:
   - Yoga Recommendations: Should show 13+ recommendations
   - Ayurveda Recommendations: Should show 7+ recommendations

## API Test

If the frontend still shows no data, test the API endpoint directly:

```bash
# Test the API endpoint (replace YOUR_TOKEN with actual token)
curl -H "Authorization: Bearer YOUR_TOKEN" \
  "http://localhost:8000/api/v1/recommendations/yoga?date=2025-12-05"
```

## Troubleshooting

If you still see "No recommendations available":

1. Check browser console for authentication errors
2. Verify backend is running on port 8000
3. Check network tab for failed API calls
4. Try the browser console token method above

## Expected Results

You should now see:
- 13+ Yoga recommendations (mix of chat and device sources)
- 7+ Ayurveda recommendations (from chat interactions)  
- Recommendations grouped by source (chat/device)
- Date-based filtering working
- Persistent data that doesn't disappear
