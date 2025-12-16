"""Test the actual chat endpoint to see what emotion is returned."""
import requests
import json

# You need to replace this with an actual JWT token from your logged in session
# Get it from browser DevTools -> Application -> Storage -> Local Storage -> jwt_token
JWT_TOKEN = "YOUR_JWT_TOKEN_HERE"

url = "http://localhost:8000/chat/message"
headers = {
    "Authorization": f"Bearer {JWT_TOKEN}",
    "Content-Type": "application/json"
}

payload = {
    "content": "Hello",
    "context_type": "general"
}

print("\n" + "="*80)
print("🧪 TESTING CHAT ENDPOINT WITH 'Hello'")
print("="*80)

print(f"\n📤 Sending POST to: {url}")
print(f"📝 Payload: {json.dumps(payload, indent=2)}")

try:
    response = requests.post(url, json=payload, headers=headers, timeout=10)
    
    print(f"\n📥 Status Code: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"\n✅ Response received:")
        print(json.dumps(data, indent=2))
        
        # Check emotion
        if 'emotion_detected' in data:
            emotion = data['emotion_detected']
            print(f"\n🎭 Emotion Detected: {emotion}")
            
            if emotion == 'anger':
                print(f"   ❌ ERROR: 'Hello' detected as ANGER!")
            elif emotion in ['neutral', 'joy']:
                print(f"   ✅ CORRECT: Greeting detected as {emotion}")
            else:
                print(f"   ⚠️  UNEXPECTED: Got {emotion}")
        else:
            print(f"\n⚠️  No emotion_detected field in response")
    else:
        print(f"\n❌ Request failed:")
        print(response.text)
        
except requests.exceptions.ConnectionError:
    print(f"\n❌ Connection Error: Is the backend server running on localhost:8000?")
    print(f"   Run: cd d:\\Nirvami\\backend && python run_dev.py")
except requests.exceptions.Timeout:
    print(f"\n❌ Request timed out")
except Exception as e:
    print(f"\n❌ Error: {e}")

print("\n" + "="*80)
