"""Test manual entry insertion directly."""
import os
import sys
from datetime import datetime, date
from dotenv import load_dotenv

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.services.wearable_service import WearableService

load_dotenv()

USER_ID = "c61e78d5-f0b4-475a-a41c-d605a0616d49"

def test_manual_entry():
    """Test manual entry insertion."""
    print("=" * 80)
    print("TESTING MANUAL ENTRY INSERTION")
    print("=" * 80)
    
    test_data = {
        "date": "2025-11-24",
        "sleep_hours": 8,
        "avg_heart_rate": 75,
        "steps": 8000,
        "stress_level": 8,
        "calories_burned": 450
    }
    
    print(f"\nUser ID: {USER_ID}")
    print(f"Test Data: {test_data}")
    print("\nAttempting to insert...")
    
    try:
        result = WearableService.ingest_manual_entry(USER_ID, test_data)
        print(f"\n✅ SUCCESS! Inserted manual entry:")
        print(f"   ID: {result.get('id')}")
        print(f"   Date: {result.get('captured_at')}")
        print(f"   Heart Rate: {result.get('heart_rate')}")
        print(f"   Steps: {result.get('steps')}")
        print(f"   Sleep: {result.get('sleep_hours')}")
        print(f"   Stress: {result.get('stress_level')}")
        
    except Exception as e:
        print(f"\n❌ FAILED: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_manual_entry()
