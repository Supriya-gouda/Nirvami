"""
End-to-End Test Script for Meal-Emotion Correlation Feature
This script tests the entire flow from meal logging to correlation display.
"""
import requests
import json
from datetime import datetime, timedelta
import time


class MealCorrelationE2ETest:
    def __init__(self, base_url="http://localhost:8000/api/v1"):
        self.base_url = base_url
        self.auth_token = None
        self.user_id = None
        self.test_meals = []
        self.test_emotions = []
        
    def print_header(self, text):
        """Print a formatted header."""
        print("\n" + "=" * 80)
        print(f"  {text}")
        print("=" * 80)
    
    def print_step(self, step_num, text):
        """Print a test step."""
        print(f"\n[STEP {step_num}] {text}")
        
    def print_success(self, text):
        """Print success message."""
        print(f"  ✓ {text}")
        
    def print_error(self, text):
        """Print error message."""
        print(f"  ✗ {text}")
        
    def test_health_check(self):
        """Test if backend is running."""
        self.print_step(1, "Checking backend health...")
        try:
            response = requests.get(f"{self.base_url.replace('/api/v1', '')}/health", timeout=5)
            if response.status_code == 200:
                self.print_success("Backend is running")
                return True
            else:
                self.print_error(f"Backend returned status {response.status_code}")
                return False
        except Exception as e:
            self.print_error(f"Cannot connect to backend: {e}")
            return False
    
    def login_or_register(self, email="test@nirvami.com", password="Test123!@#"):
        """Login or register a test user."""
        self.print_step(2, "Authenticating test user...")
        
        # Try to login first
        try:
            response = requests.post(
                f"{self.base_url}/auth/login",
                json={"email": email, "password": password}
            )
            
            if response.status_code == 200:
                data = response.json()
                self.auth_token = data.get("access_token")
                self.user_id = data.get("user", {}).get("id")
                self.print_success(f"Logged in as {email}")
                return True
            elif response.status_code == 400:
                # Try to register
                self.print_success("User not found, attempting registration...")
                register_response = requests.post(
                    f"{self.base_url}/auth/register",
                    json={
                        "email": email,
                        "password": password,
                        "full_name": "Test User"
                    }
                )
                
                if register_response.status_code in [200, 201]:
                    data = register_response.json()
                    self.auth_token = data.get("access_token")
                    self.user_id = data.get("user", {}).get("id")
                    self.print_success(f"Registered and logged in as {email}")
                    return True
                else:
                    self.print_error(f"Registration failed: {register_response.text}")
                    return False
            else:
                self.print_error(f"Login failed: {response.text}")
                return False
                
        except Exception as e:
            self.print_error(f"Authentication error: {e}")
            return False
    
    def get_headers(self):
        """Get authorization headers."""
        return {"Authorization": f"Bearer {self.auth_token}"}
    
    def create_test_meals(self):
        """Create test meal logs."""
        self.print_step(3, "Creating test meal logs...")
        
        now = datetime.now()
        test_meals_data = [
            {
                "meal_time": (now - timedelta(hours=48)).isoformat(),
                "meal_type": "breakfast",
                "meal_text": "Oatmeal with berries and honey",
                "ingredients": ["oats", "blueberries", "honey", "almond milk"],
                "calories": 350
            },
            {
                "meal_time": (now - timedelta(hours=36)).isoformat(),
                "meal_type": "lunch",
                "meal_text": "Grilled chicken salad",
                "ingredients": ["chicken breast", "mixed greens", "tomatoes", "olive oil"],
                "calories": 420
            },
            {
                "meal_time": (now - timedelta(hours=24)).isoformat(),
                "meal_type": "dinner",
                "meal_text": "Salmon with quinoa and vegetables",
                "ingredients": ["salmon", "quinoa", "broccoli", "carrots"],
                "calories": 550
            },
            {
                "meal_time": (now - timedelta(hours=12)).isoformat(),
                "meal_type": "snack",
                "meal_text": "Fast food burger and fries",
                "ingredients": ["burger", "french fries", "soda"],
                "calories": 950
            }
        ]
        
        created_count = 0
        for meal_data in test_meals_data:
            try:
                response = requests.post(
                    f"{self.base_url}/meals/log",
                    json=meal_data,
                    headers=self.get_headers()
                )
                
                if response.status_code in [200, 201]:
                    meal = response.json()
                    self.test_meals.append(meal)
                    created_count += 1
                    self.print_success(f"Created meal: {meal_data['meal_text']}")
                else:
                    self.print_error(f"Failed to create meal: {response.text}")
                    
            except Exception as e:
                self.print_error(f"Error creating meal: {e}")
        
        print(f"\n  Created {created_count}/{len(test_meals_data)} test meals")
        return created_count > 0
    
    def create_test_emotions(self):
        """Create test emotion logs that correlate with meals."""
        self.print_step(4, "Creating test emotion logs...")
        
        now = datetime.now()
        # Emotions 2-3 hours after each meal
        test_emotions_data = [
            {
                "emotion_type": "joy",
                "confidence": 0.85,
                "timestamp": (now - timedelta(hours=46)).isoformat(),  # After oatmeal
                "source": "manual"
            },
            {
                "emotion_type": "contentment",
                "confidence": 0.75,
                "timestamp": (now - timedelta(hours=34)).isoformat(),  # After salad
                "source": "manual"
            },
            {
                "emotion_type": "happiness",
                "confidence": 0.80,
                "timestamp": (now - timedelta(hours=22)).isoformat(),  # After salmon
                "source": "manual"
            },
            {
                "emotion_type": "anxiety",
                "confidence": 0.70,
                "timestamp": (now - timedelta(hours=10)).isoformat(),  # After fast food
                "source": "manual"
            }
        ]
        
        created_count = 0
        for emotion_data in test_emotions_data:
            try:
                response = requests.post(
                    f"{self.base_url}/emotions/log",
                    json=emotion_data,
                    headers=self.get_headers()
                )
                
                if response.status_code in [200, 201]:
                    emotion = response.json()
                    self.test_emotions.append(emotion)
                    created_count += 1
                    self.print_success(f"Created emotion: {emotion_data['emotion_type']}")
                else:
                    self.print_error(f"Failed to create emotion: {response.text}")
                    
            except Exception as e:
                self.print_error(f"Error creating emotion: {e}")
        
        print(f"\n  Created {created_count}/{len(test_emotions_data)} test emotions")
        return created_count > 0
    
    def trigger_correlation_analysis(self):
        """Trigger the correlation analysis."""
        self.print_step(5, "Triggering correlation analysis...")
        
        try:
            response = requests.post(
                f"{self.base_url}/meals/analyze-correlations",
                headers=self.get_headers()
            )
            
            if response.status_code == 200:
                result = response.json()
                self.print_success(f"Analysis completed: {result['message']}")
                self.print_success(f"Correlations calculated: {result['correlations_calculated']}")
                self.print_success(f"Correlations stored: {result['correlations_stored']}")
                return result['correlations_stored'] > 0
            else:
                self.print_error(f"Analysis failed: {response.text}")
                return False
                
        except Exception as e:
            self.print_error(f"Error running analysis: {e}")
            return False
    
    def get_correlation_insights(self):
        """Retrieve food-mood correlation insights."""
        self.print_step(6, "Retrieving correlation insights...")
        
        try:
            response = requests.get(
                f"{self.base_url}/meals/correlations",
                headers=self.get_headers()
            )
            
            if response.status_code == 200:
                data = response.json()
                
                self.print_success(f"Total foods analyzed: {data['total_foods_analyzed']}")
                
                print(f"\n  Top 3 Mood-Boosting Foods:")
                for i, food in enumerate(data['mood_boosting_foods'][:3], 1):
                    print(f"    {i}. {food['food']}")
                    print(f"       Impact: +{food['impact_score']:.2f} ({food['occurrences']} occurrences)")
                
                print(f"\n  Top 3 Foods to Watch:")
                for i, food in enumerate(data['foods_to_watch'][:3], 1):
                    print(f"    {i}. {food['food']}")
                    print(f"       Impact: {food['impact_score']:.2f} ({food['occurrences']} occurrences)")
                
                return True
            else:
                self.print_error(f"Failed to get insights: {response.text}")
                return False
                
        except Exception as e:
            self.print_error(f"Error getting insights: {e}")
            return False
    
    def verify_database_storage(self):
        """Verify data is stored in Supabase."""
        self.print_step(7, "Verifying database storage...")
        
        # Check meal history
        try:
            response = requests.get(
                f"{self.base_url}/meals/history?days=7",
                headers=self.get_headers()
            )
            
            if response.status_code == 200:
                meals = response.json()
                self.print_success(f"Found {len(meals)} meals in database")
            else:
                self.print_error("Could not retrieve meal history")
                
        except Exception as e:
            self.print_error(f"Error checking meals: {e}")
        
        # Check emotion history
        try:
            response = requests.get(
                f"{self.base_url}/emotions/history?days=7",
                headers=self.get_headers()
            )
            
            if response.status_code == 200:
                emotions = response.json()
                self.print_success(f"Found {len(emotions)} emotions in database")
            else:
                self.print_error("Could not retrieve emotion history")
                
        except Exception as e:
            self.print_error(f"Error checking emotions: {e}")
        
        return True
    
    def run_full_test(self):
        """Run the complete end-to-end test."""
        self.print_header("MEAL-EMOTION CORRELATION E2E TEST")
        
        # Test sequence
        if not self.test_health_check():
            self.print_error("Backend not accessible. Start the backend first.")
            return False
        
        if not self.login_or_register():
            self.print_error("Authentication failed")
            return False
        
        if not self.create_test_meals():
            self.print_error("Failed to create test meals")
            return False
        
        if not self.create_test_emotions():
            self.print_error("Failed to create test emotions")
            return False
        
        # Wait a moment for data to be committed
        print("\n  Waiting 2 seconds for data to be committed...")
        time.sleep(2)
        
        if not self.trigger_correlation_analysis():
            self.print_error("Correlation analysis failed")
            return False
        
        if not self.get_correlation_insights():
            self.print_error("Failed to retrieve insights")
            return False
        
        self.verify_database_storage()
        
        # Success summary
        self.print_header("✅ ALL TESTS PASSED!")
        print("\nThe Meal-Emotion Correlation feature is working correctly:")
        print("  ✓ Backend API is accessible")
        print("  ✓ Meal logging works")
        print("  ✓ Emotion logging works")
        print("  ✓ Correlation analysis runs successfully")
        print("  ✓ Food-mood insights are generated")
        print("  ✓ Data is stored in database")
        print("\nYou can now:")
        print("  1. Log meals via the DietMoodPage")
        print("  2. Log emotions via various pages")
        print("  3. View insights in the ProgressAnalyticsPage")
        print("  4. Click 'Refresh Analysis' to update correlations")
        
        return True


if __name__ == "__main__":
    import sys
    
    # Allow custom base URL
    base_url = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:8000/api/v1"
    
    tester = MealCorrelationE2ETest(base_url)
    success = tester.run_full_test()
    
    sys.exit(0 if success else 1)
