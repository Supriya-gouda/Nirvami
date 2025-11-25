import requests
import sys
import time

def verify_db_write():
    print("Attempting to connect to backend...")
    max_retries = 5
    for i in range(max_retries):
        try:
            response = requests.post("http://localhost:8000/debug/db-test")
            print(f"Status Code: {response.status_code}")
            print(f"Response: {response.json()}")
            
            if response.status_code == 200 and response.json().get("ok"):
                print("SUCCESS: DB Write Verified")
                return
            else:
                print("FAILURE: DB Write Failed")
                sys.exit(1)
        except requests.exceptions.ConnectionError:
            print(f"Connection failed (attempt {i+1}/{max_retries}). Retrying in 2s...")
            time.sleep(2)
        except Exception as e:
            print(f"Error: {e}")
            sys.exit(1)
    
    print("Could not connect to backend after retries.")
    sys.exit(1)

if __name__ == "__main__":
    verify_db_write()
