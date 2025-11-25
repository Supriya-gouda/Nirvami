#!/usr/bin/env python3
"""
Test script for wearable device v2 feature
Tests the complete flow: manual entry → analysis → notifications
"""

import asyncio
import sys
from datetime import date
from pathlib import Path

# Add backend to path
backend_path = Path(__file__).parent.parent
sys.path.insert(0, str(backend_path))

from app.services.wearable_service_v2 import WearableService
from app.services.notification_service import NotificationService
from app.config import settings

async def test_wearable_v2():
    """Test complete wearable v2 workflow"""
    
    print("=" * 60)
    print("🧪 Testing Wearable Device V2 Feature")
    print("=" * 60)
    
    # Initialize services
    wearable_service = WearableService()
    notification_service = NotificationService()
    
    # Test user ID (replace with actual user ID from your database)
    # You can get this from: SELECT id FROM profiles LIMIT 1;
    test_user_id = "YOUR_USER_ID_HERE"
    
    if test_user_id == "YOUR_USER_ID_HERE":
        print("\n❌ ERROR: Please update test_user_id with a real user ID from your database")
        print("   Run this query in Supabase SQL Editor:")
        print("   SELECT id, email FROM profiles LIMIT 1;")
        return
    
    print(f"\n📋 Test User ID: {test_user_id}")
    
    # Test 1: Save manual entry
    print("\n" + "=" * 60)
    print("Test 1: Save Manual Health Entry")
    print("=" * 60)
    
    test_data = {
        "date": str(date.today()),
        "sleep_hours": 5.5,  # Low sleep to trigger warning
        "avg_heart_rate": 95,  # Elevated HR
        "steps": 3000,
        "stress_level": 7,  # High stress
        "calories_burned": 1800
    }
    
    print("\n📊 Test Data:")
    for key, value in test_data.items():
        print(f"   {key}: {value}")
    
    try:
        result = await wearable_service.save_manual_entry(test_user_id, test_data)
        print("\n✅ Manual entry saved successfully!")
        print(f"   Entry ID: {result.get('id')}")
    except Exception as e:
        print(f"\n❌ Failed to save manual entry: {e}")
        return
    
    # Test 2: Get latest entry
    print("\n" + "=" * 60)
    print("Test 2: Retrieve Latest Entry")
    print("=" * 60)
    
    try:
        latest = await wearable_service.get_latest(test_user_id)
        if latest:
            print("\n✅ Latest entry retrieved:")
            print(f"   Date: {latest.get('date')}")
            print(f"   Sleep: {latest.get('sleep_hours')} hrs")
            print(f"   Heart Rate: {latest.get('avg_heart_rate')} bpm")
            print(f"   Steps: {latest.get('steps')}")
            print(f"   Stress: {latest.get('stress_level')}/10")
        else:
            print("\n⚠️  No data found")
    except Exception as e:
        print(f"\n❌ Failed to retrieve latest entry: {e}")
    
    # Test 3: Analyze health risks
    print("\n" + "=" * 60)
    print("Test 3: Analyze Health Risks")
    print("=" * 60)
    
    try:
        analysis = await wearable_service.analyze_health_risks(test_user_id)
        
        print(f"\n📈 Analysis Results:")
        print(f"   Has Risks: {analysis['has_risks']}")
        print(f"   Risk Level: {analysis['risk_level'].upper()}")
        
        if analysis['risks']:
            print(f"\n⚠️  Detected Concerns ({len(analysis['risks'])}):")
            for i, risk in enumerate(analysis['risks'], 1):
                print(f"   {i}. {risk}")
        
        if analysis['recommendations']:
            print(f"\n💡 Recommendations ({len(analysis['recommendations'])}):")
            for i, rec in enumerate(analysis['recommendations'], 1):
                print(f"   {i}. {rec}")
        
        # Test 4: Create notification
        print("\n" + "=" * 60)
        print("Test 4: Create In-App Notification")
        print("=" * 60)
        
        notification_message = f"Health Analysis: {analysis['risk_level'].upper()} risk level detected"
        if analysis['risks']:
            notification_message += f"\n{len(analysis['risks'])} concern(s) found"
        
        try:
            notification = await notification_service.create_notification(
                user_id=test_user_id,
                title="🏥 Health Analysis Complete",
                message=notification_message,
                type="health_alert",
                priority="high" if analysis['risk_level'] in ['high', 'critical'] else "medium"
            )
            print(f"\n✅ Notification created:")
            print(f"   ID: {notification.get('id')}")
            print(f"   Title: {notification.get('title')}")
            print(f"   Priority: {notification.get('priority')}")
        except Exception as e:
            print(f"\n⚠️  Could not create notification: {e}")
        
        # Test 5: SMS Alert (if high/critical risk)
        if analysis['risk_level'] in ['high', 'critical']:
            print("\n" + "=" * 60)
            print("Test 5: SMS Alert (High/Critical Risk)")
            print("=" * 60)
            
            print(f"\n📱 SMS should be sent for {analysis['risk_level'].upper()} risk level")
            print("   Check Twilio configuration in backend/app/config.py")
            
            if settings.TWILIO_ACCOUNT_SID and settings.TWILIO_AUTH_TOKEN:
                print("   ✅ Twilio credentials configured")
            else:
                print("   ⚠️  Twilio credentials not configured - SMS will not be sent")
        
    except Exception as e:
        print(f"\n❌ Analysis failed: {e}")
        import traceback
        traceback.print_exc()
    
    # Test 6: Get history
    print("\n" + "=" * 60)
    print("Test 6: Retrieve Entry History")
    print("=" * 60)
    
    try:
        history = await wearable_service.get_all_for_user(test_user_id, limit=5)
        print(f"\n✅ Found {len(history)} entries")
        for i, entry in enumerate(history, 1):
            print(f"\n   Entry {i}:")
            print(f"      Date: {entry.get('date')}")
            print(f"      Sleep: {entry.get('sleep_hours')} hrs")
            print(f"      HR: {entry.get('avg_heart_rate')} bpm")
            print(f"      Steps: {entry.get('steps')}")
    except Exception as e:
        print(f"\n❌ Failed to retrieve history: {e}")
    
    print("\n" + "=" * 60)
    print("🎉 Testing Complete!")
    print("=" * 60)
    
    print("\n📝 Next Steps:")
    print("   1. Check Supabase → wearable_snapshots table for saved data")
    print("   2. Check Supabase → notifications table for created notification")
    print("   3. Test the frontend at http://localhost:5173")
    print("   4. Navigate to Device Page and click Analyze button")
    print("   5. Check Dashboard for latest data display")

if __name__ == "__main__":
    asyncio.run(test_wearable_v2())
