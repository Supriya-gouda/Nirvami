"""
Test script for journal API with emotion detection and Gemini insights.
"""

import requests
import json
from datetime import date

# Configuration
BASE_URL = "http://localhost:8000"
API_PREFIX = "/api/v1"

# You'll need a valid JWT token - get it from your frontend login
AUTH_TOKEN = "YOUR_JWT_TOKEN_HERE"

headers = {
    "Authorization": f"Bearer {AUTH_TOKEN}",
    "Content-Type": "application/json"
}


def test_create_journal():
    """Test creating a journal entry with emotion detection."""
    print("\n=== Testing Journal Creation ===")
    
    url = f"{BASE_URL}{API_PREFIX}/journal"
    payload = {
        "content": "Today was an amazing day! I woke up feeling energized and accomplished so much. Had a great workout, connected with friends, and made progress on my projects. Feeling really grateful and motivated for tomorrow!",
        "date": date.today().isoformat()
    }
    
    response = requests.post(url, json=payload, headers=headers)
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    
    if response.status_code == 201:
        return response.json()['id']
    return None


def test_get_journal_entries():
    """Test retrieving journal entries."""
    print("\n=== Testing Get Journal Entries ===")
    
    url = f"{BASE_URL}{API_PREFIX}/journal"
    response = requests.get(url, headers=headers)
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")


def test_update_journal(entry_id: str):
    """Test updating a journal entry."""
    print("\n=== Testing Journal Update ===")
    
    url = f"{BASE_URL}{API_PREFIX}/journal/{entry_id}"
    payload = {
        "content": "Update: The day got even better! Just received some exciting news that made me feel absolutely joyful. This is one of the best days I've had in a long time!"
    }
    
    response = requests.put(url, json=payload, headers=headers)
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")


def test_generate_summary():
    """Test generating Gemini-powered journal summary."""
    print("\n=== Testing Journal Summary Generation ===")
    
    url = f"{BASE_URL}{API_PREFIX}/journal/summarize"
    payload = {
        "date": date.today().isoformat(),
        "regenerate": False
    }
    
    response = requests.post(url, json=payload, headers=headers)
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        print(f"\n📊 Daily Insight for {payload['date']}")
        print("=" * 60)
        
        summary_data = result.get('summary', {})
        print(f"\n💭 Summary:")
        print(f"   {summary_data.get('summary', 'N/A')}")
        
        print(f"\n😊 Dominant Emotions:")
        emotions = summary_data.get('dominant_emotions', [])
        print(f"   {', '.join(emotions)}")
        
        print(f"\n📈 Patterns Observed:")
        print(f"   {summary_data.get('patterns', 'N/A')}")
        
        print(f"\n✨ Positive Signals:")
        print(f"   {summary_data.get('positive_signals', 'N/A')}")
        
        print(f"\n💡 Gentle Suggestion:")
        print(f"   {summary_data.get('gentle_suggestion', 'N/A')}")
        
        print("\n" + "=" * 60)
    else:
        print(f"Error: {json.dumps(response.json(), indent=2)}")


def test_delete_journal(entry_id: str):
    """Test deleting a journal entry."""
    print("\n=== Testing Journal Deletion ===")
    
    url = f"{BASE_URL}{API_PREFIX}/journal/{entry_id}"
    response = requests.delete(url, headers=headers)
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")


if __name__ == "__main__":
    print("🧪 Journal API Test Suite")
    print("=" * 60)
    print("⚠️  Make sure to:")
    print("1. Update AUTH_TOKEN with a valid JWT token")
    print("2. Start the backend server (python run_dev.py)")
    print("3. Apply database schema (python scripts/apply_journal_emotion_schema.py)")
    print("=" * 60)
    
    # Run tests
    entry_id = test_create_journal()
    
    if entry_id:
        test_get_journal_entries()
        test_update_journal(entry_id)
        test_generate_summary()
        
        # Uncomment to test deletion
        # test_delete_journal(entry_id)
    
    print("\n✅ Test suite completed!")
