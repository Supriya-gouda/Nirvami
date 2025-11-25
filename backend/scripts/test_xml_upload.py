"""
Test script for Apple Health XML upload functionality.
Creates a sample Apple Health export XML and tests the upload endpoint.
"""
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta
import requests
import os

# Sample Apple Health XML structure
def create_sample_xml():
    """Create a sample Apple Health export XML with realistic data."""
    root = ET.Element("HealthData", locale="en_US")
    
    # Add some sample records over 3 days
    base_date = datetime.now() - timedelta(days=2)
    
    for day in range(3):
        current_date = base_date + timedelta(days=day)
        
        # Heart rate readings (multiple per day)
        for hour in range(8, 22, 2):  # Every 2 hours from 8am to 10pm
            record_time = current_date.replace(hour=hour, minute=0, second=0)
            hr_value = 72 + (hour % 3) * 5  # Varies between 72-82
            
            ET.SubElement(root, "Record", {
                "type": "HKQuantityTypeIdentifierHeartRate",
                "sourceName": "Apple Watch",
                "unit": "count/min",
                "value": str(hr_value),
                "startDate": record_time.strftime("%Y-%m-%d %H:%M:%S +0000"),
                "endDate": record_time.strftime("%Y-%m-%d %H:%M:%S +0000")
            })
        
        # Steps
        steps_value = 8500 + day * 500
        ET.SubElement(root, "Record", {
            "type": "HKQuantityTypeIdentifierStepCount",
            "sourceName": "iPhone",
            "unit": "count",
            "value": str(steps_value),
            "startDate": current_date.strftime("%Y-%m-%d 00:00:00 +0000"),
            "endDate": current_date.strftime("%Y-%m-%d 23:59:59 +0000")
        })
        
        # Sleep
        sleep_start = current_date.replace(hour=23, minute=0, second=0)
        sleep_end = (current_date + timedelta(days=1)).replace(hour=6, minute=30, second=0)
        ET.SubElement(root, "Record", {
            "type": "HKCategoryTypeIdentifierSleepAnalysis",
            "sourceName": "Apple Watch",
            "value": "HKCategoryValueSleepAnalysisAsleep",
            "startDate": sleep_start.strftime("%Y-%m-%d %H:%M:%S +0000"),
            "endDate": sleep_end.strftime("%Y-%m-%d %H:%M:%S +0000")
        })
        
        # Calories burned
        calories_value = 420 + day * 30
        ET.SubElement(root, "Record", {
            "type": "HKQuantityTypeIdentifierActiveEnergyBurned",
            "sourceName": "Apple Watch",
            "unit": "kcal",
            "value": str(calories_value),
            "startDate": current_date.strftime("%Y-%m-%d 00:00:00 +0000"),
            "endDate": current_date.strftime("%Y-%m-%d 23:59:59 +0000")
        })
    
    # Write to file
    tree = ET.ElementTree(root)
    filepath = "sample_apple_health_export.xml"
    tree.write(filepath, encoding="UTF-8", xml_declaration=True)
    print(f"✅ Created sample XML: {filepath}")
    return filepath


def test_xml_upload(xml_filepath, token):
    """Test the XML upload endpoint."""
    url = "http://localhost:8000/api/v1/wearable/upload-xml"
    
    headers = {
        "Authorization": f"Bearer {token}"
    }
    
    with open(xml_filepath, 'rb') as f:
        files = {'file': ('export.xml', f, 'text/xml')}
        
        print(f"\n📤 Uploading XML to {url}...")
        response = requests.post(url, files=files, headers=headers)
    
    if response.status_code == 200:
        result = response.json()
        print(f"\n✅ Upload successful!")
        print(f"   Records processed: {result.get('records_count')}")
        print(f"   Snapshots created: {result.get('snapshots_created')}")
        print(f"   Days processed: {result.get('days_processed')}")
        print(f"   Date range: {result.get('date_range')}")
    else:
        print(f"\n❌ Upload failed: {response.status_code}")
        print(f"   Error: {response.text}")
    
    return response


if __name__ == "__main__":
    print("=" * 60)
    print("Apple Health XML Upload Test")
    print("=" * 60)
    
    # Step 1: Create sample XML
    xml_file = create_sample_xml()
    
    # Step 2: Get authentication token
    print("\n🔐 Please provide your authentication token:")
    print("   (You can get this from the browser after logging in)")
    print("   Look in localStorage.getItem('token')")
    token = input("\nToken: ").strip()
    
    if not token:
        print("\n⚠️  No token provided. Exiting...")
        exit(1)
    
    # Step 3: Test upload
    response = test_xml_upload(xml_file, token)
    
    # Clean up
    if os.path.exists(xml_file):
        os.remove(xml_file)
        print(f"\n🧹 Cleaned up {xml_file}")
    
    print("\n" + "=" * 60)
    print("Test complete!")
    print("=" * 60)
