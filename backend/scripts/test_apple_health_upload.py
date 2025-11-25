"""Test Apple Health XML upload end-to-end."""
import sys
import asyncio
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.services.apple_health_parser import AppleHealthParser
from app.services.apple_health_storage import AppleHealthStorage


def test_xml_parsing():
    """Test XML parsing with sample Apple Health data."""
    
    # Sample Apple Health XML structure
    sample_xml = """<?xml version="1.0" encoding="UTF-8"?>
<HealthData locale="en_US">
    <Record type="HKQuantityTypeIdentifierHeartRate" sourceName="Apple Watch" sourceVersion="9.0" unit="count/min" creationDate="2025-11-24 08:00:00 -0800" startDate="2025-11-24 08:00:00 -0800" endDate="2025-11-24 08:00:00 -0800" value="75"/>
    <Record type="HKQuantityTypeIdentifierHeartRate" sourceName="Apple Watch" sourceVersion="9.0" unit="count/min" creationDate="2025-11-24 09:00:00 -0800" startDate="2025-11-24 09:00:00 -0800" endDate="2025-11-24 09:00:00 -0800" value="82"/>
    <Record type="HKQuantityTypeIdentifierHeartRate" sourceName="Apple Watch" sourceVersion="9.0" unit="count/min" creationDate="2025-11-24 10:00:00 -0800" startDate="2025-11-24 10:00:00 -0800" endDate="2025-11-24 10:00:00 -0800" value="78"/>
    <Record type="HKQuantityTypeIdentifierStepCount" sourceName="iPhone" sourceVersion="iOS 17" unit="count" creationDate="2025-11-24 12:00:00 -0800" startDate="2025-11-24 12:00:00 -0800" endDate="2025-11-24 12:00:00 -0800" value="1500"/>
    <Record type="HKQuantityTypeIdentifierStepCount" sourceName="iPhone" sourceVersion="iOS 17" unit="count" creationDate="2025-11-24 15:00:00 -0800" startDate="2025-11-24 15:00:00 -0800" endDate="2025-11-24 15:00:00 -0800" value="2300"/>
    <Record type="HKCategoryTypeIdentifierSleepAnalysis" sourceName="Apple Watch" sourceVersion="9.0" creationDate="2025-11-24 06:00:00 -0800" startDate="2025-11-23 23:00:00 -0800" endDate="2025-11-24 06:30:00 -0800" value="HKCategoryValueSleepAnalysisAsleep"/>
    <Record type="HKQuantityTypeIdentifierActiveEnergyBurned" sourceName="Apple Watch" sourceVersion="9.0" unit="kcal" creationDate="2025-11-24 18:00:00 -0800" startDate="2025-11-24 18:00:00 -0800" endDate="2025-11-24 18:00:00 -0800" value="450"/>
</HealthData>"""
    
    print("=" * 80)
    print("TESTING APPLE HEALTH XML PARSER")
    print("=" * 80)
    
    # Step 1: Parse XML
    print("\n📋 Step 1: Parsing XML...")
    result = AppleHealthParser.parse_xml_file(sample_xml)
    
    if not result['success']:
        print(f"❌ Parsing failed: {result.get('error')}")
        return False
    
    print(f"✅ Parsing successful!")
    print(f"   - Total records: {result['stats']['total_records']}")
    print(f"   - Days with data: {result['stats']['days_with_data']}")
    print(f"   - Sample types: {result['stats']['sample_types'][:5]}")
    
    daily_data = result['daily_data']
    print(f"\n📊 Daily data extracted:")
    for date_str, metrics in daily_data.items():
        print(f"   {date_str}:")
        for key, value in metrics.items():
            print(f"      - {key}: {value}")
    
    # Step 2: Convert to snapshots
    print("\n🔄 Step 2: Converting to snapshots...")
    # Use a test user ID (you'll need to replace this with an actual user ID from your DB)
    test_user_id = "00000000-0000-0000-0000-000000000000"  # Replace with actual user ID
    
    snapshots = AppleHealthParser.convert_to_snapshots(daily_data, test_user_id)
    print(f"✅ Created {len(snapshots)} snapshots")
    
    for i, snapshot in enumerate(snapshots, 1):
        print(f"\n   Snapshot {i}:")
        for key, value in snapshot.items():
            print(f"      - {key}: {value}")
    
    print("\n" + "=" * 80)
    print("✅ TEST COMPLETED SUCCESSFULLY")
    print("=" * 80)
    print("\nTo test database storage:")
    print("1. Get your actual user_id from the profiles table")
    print("2. Replace test_user_id in this script")
    print("3. Uncomment the save_snapshots section below")
    print("\n# Uncomment to test database storage:")
    print("# save_result = AppleHealthStorage.save_snapshots(snapshots)")
    print("# print(f'Save result: {save_result}')")
    
    return True


if __name__ == "__main__":
    success = test_xml_parsing()
    sys.exit(0 if success else 1)
