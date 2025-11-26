"""Test XML upload with wearable-v2 endpoint."""
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import requests

# Sample Apple Health XML with heart rate data
SAMPLE_XML = """<?xml version="1.0" encoding="UTF-8"?>
<HealthData locale="en_US">
  <Record type="HKQuantityTypeIdentifierHeartRate" sourceName="Apple Watch" unit="count/min" 
          creationDate="2025-11-25 10:30:00 +0000" startDate="2025-11-25 10:30:00 +0000" 
          endDate="2025-11-25 10:30:00 +0000" value="72"/>
  <Record type="HKQuantityTypeIdentifierHeartRate" sourceName="Apple Watch" unit="count/min" 
          creationDate="2025-11-25 11:00:00 +0000" startDate="2025-11-25 11:00:00 +0000" 
          endDate="2025-11-25 11:00:00 +0000" value="68"/>
  <Record type="HKQuantityTypeIdentifierHeartRate" sourceName="Apple Watch" unit="count/min" 
          creationDate="2025-11-25 11:30:00 +0000" startDate="2025-11-25 11:30:00 +0000" 
          endDate="2025-11-25 11:30:00 +0000" value="95"/>
  <Record type="HKQuantityTypeIdentifierHeartRate" sourceName="Apple Watch" unit="count/min" 
          creationDate="2025-11-25 12:00:00 +0000" startDate="2025-11-25 12:00:00 +0000" 
          endDate="2025-11-25 12:00:00 +0000" value="85"/>
  <Record type="HKQuantityTypeIdentifierStepCount" sourceName="iPhone" unit="count" 
          creationDate="2025-11-25 10:00:00 +0000" startDate="2025-11-25 10:00:00 +0000" 
          endDate="2025-11-25 11:00:00 +0000" value="500"/>
</HealthData>
"""

def test_xml_upload():
    """Test uploading XML to wearable-v2 endpoint."""
    
    # You need to get a valid auth token first
    # For testing, you can use the login endpoint or hardcode a token
    
    BASE_URL = "http://localhost:8000/api/v1"
    
    # First, login to get token
    print("🔐 Logging in...")
    login_data = {
        "email": "test@example.com",  # Replace with your test user
        "password": "testpassword123"   # Replace with your test password
    }
    
    try:
        login_response = requests.post(f"{BASE_URL}/auth/login", json=login_data)
        if login_response.status_code != 200:
            print(f"❌ Login failed: {login_response.text}")
            print("\n⚠️  Please update the test credentials in test_xml_upload_v2.py")
            return
        
        token = login_response.json()["access_token"]
        print(f"✅ Login successful")
        
    except Exception as e:
        print(f"❌ Login error: {e}")
        print("\n⚠️  Make sure the backend is running on http://localhost:8000")
        return
    
    # Upload XML
    print("\n📤 Uploading XML file...")
    
    # Create temporary XML file
    import tempfile
    with tempfile.NamedTemporaryFile(mode='w', suffix='.xml', delete=False) as f:
        f.write(SAMPLE_XML)
        xml_path = f.name
    
    try:
        with open(xml_path, 'rb') as f:
            files = {'file': ('export.xml', f, 'text/xml')}
            headers = {'Authorization': f'Bearer {token}'}
            
            response = requests.post(
                f"{BASE_URL}/wearable-v2/upload-xml",
                files=files,
                headers=headers
            )
        
        print(f"\n📊 Response Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Upload successful!")
            print(f"\n📈 Results:")
            print(f"  • Success: {data.get('success')}")
            print(f"  • Message: {data.get('message')}")
            print(f"  • Records: {data.get('records_count')}")
            print(f"  • Latest HR: {data.get('latest_heart_rate')} bpm")
            print(f"  • Average HR: {data.get('average_heart_rate')} bpm")
            
            analysis = data.get('analysis', {})
            print(f"\n🔍 Analysis Results:")
            print(f"  • Has Risks: {analysis.get('has_risks')}")
            print(f"  • Risk Level: {analysis.get('risk_level')}")
            
            if analysis.get('risks'):
                print(f"  • Risks:")
                for risk in analysis['risks']:
                    print(f"    - {risk}")
            
            if analysis.get('recommendations'):
                print(f"  • Recommendations:")
                for rec in analysis['recommendations'][:3]:
                    print(f"    - {rec}")
        else:
            print(f"❌ Upload failed: {response.text}")
    
    finally:
        # Cleanup temp file
        os.unlink(xml_path)


if __name__ == "__main__":
    print("=" * 60)
    print("Testing XML Upload with Wearable V2 Endpoint")
    print("=" * 60)
    test_xml_upload()
    print("\n" + "=" * 60)
