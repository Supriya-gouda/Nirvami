"""Inspect export.xml to see actual record types."""
import xml.etree.ElementTree as ET
from collections import Counter
import sys

# Path to export.xml - you'll need to provide this
xml_path = input("Enter path to export.xml: ").strip('"').strip("'")

try:
    tree = ET.parse(xml_path)
    root = tree.getroot()
    
    print(f"\n✅ Root tag: {root.tag}")
    print(f"✅ Root attributes: {root.attrib}")
    
    # Find all Record elements
    records = root.findall('.//Record')
    print(f"\n📊 Found {len(records)} Record elements")
    
    # Count record types
    type_counter = Counter()
    for record in records:
        record_type = record.get('type', 'NO_TYPE')
        type_counter[record_type] += 1
    
    print(f"\n📋 Top 20 Record Types:")
    for record_type, count in type_counter.most_common(20):
        print(f"  - {record_type}: {count} records")
    
    # Show sample of first HeartRate record
    print(f"\n🔍 Looking for HeartRate records...")
    hr_records = [r for r in records if 'HeartRate' in r.get('type', '')]
    if hr_records:
        print(f"✅ Found {len(hr_records)} HeartRate records")
        print(f"\nSample HeartRate record:")
        sample = hr_records[0]
        for key, value in sample.attrib.items():
            print(f"  {key}: {value}")
    else:
        print("❌ No HeartRate records found")
        print("\nChecking for any heart-related records:")
        heart_records = [r for r in records if 'heart' in r.get('type', '').lower()]
        if heart_records:
            print(f"Found {len(heart_records)} heart-related records:")
            for r in heart_records[:5]:
                print(f"  Type: {r.get('type')}")
        
    # Show sample of first StepCount record
    print(f"\n🔍 Looking for StepCount records...")
    step_records = [r for r in records if 'Step' in r.get('type', '')]
    if step_records:
        print(f"✅ Found {len(step_records)} StepCount records")
        print(f"\nSample StepCount record:")
        sample = step_records[0]
        for key, value in sample.attrib.items():
            print(f"  {key}: {value}")
    else:
        print("❌ No StepCount records found")

    # Show sample of first Sleep record
    print(f"\n🔍 Looking for Sleep records...")
    sleep_records = [r for r in records if 'Sleep' in r.get('type', '')]
    if sleep_records:
        print(f"✅ Found {len(sleep_records)} Sleep records")
        print(f"\nSample Sleep record:")
        sample = sleep_records[0]
        for key, value in sample.attrib.items():
            print(f"  {key}: {value}")
    else:
        print("❌ No Sleep records found")
        
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
