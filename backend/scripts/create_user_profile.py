"""Create user profile if it doesn't exist."""
import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.utils.database import get_supabase
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def ensure_user_profile_exists(user_id: str, email: str = None):
    """
    Ensure a user profile exists in the profiles table.
    
    Args:
        user_id: The user's UUID from authentication
        email: Optional email address for the profile
    """
    supabase = get_supabase()
    
    try:
        # Check if profile exists
        result = supabase.table('profiles').select('*').eq('id', user_id).execute()
        
        if result.data and len(result.data) > 0:
            logger.info(f"✅ Profile already exists for user {user_id}")
            logger.info(f"   Email: {result.data[0].get('email')}")
            logger.info(f"   Name: {result.data[0].get('full_name', 'Not set')}")
            return True
        
        # Profile doesn't exist, create it
        logger.warning(f"⚠️  Profile does not exist for user {user_id}")
        logger.info(f"Creating profile...")
        
        profile_data = {
            'id': user_id,
            'email': email or f"user_{user_id[:8]}@example.com",
            'consent_data_collection': True,
            'consent_ai_processing': True,
            'consent_notifications': True
        }
        
        insert_result = supabase.table('profiles').insert(profile_data).execute()
        
        if insert_result.data:
            logger.info(f"✅ Profile created successfully!")
            logger.info(f"   User ID: {user_id}")
            logger.info(f"   Email: {profile_data['email']}")
            
            # Also create user preferences
            try:
                prefs_data = {
                    'user_id': user_id,
                    'notification_email': True,
                    'notification_sms': False,
                    'notification_push': True,
                    'crisis_alerts_enabled': True
                }
                supabase.table('user_preferences').insert(prefs_data).execute()
                logger.info(f"✅ User preferences created")
            except Exception as pref_error:
                logger.warning(f"Could not create preferences: {pref_error}")
            
            return True
        else:
            logger.error(f"❌ Failed to create profile")
            return False
            
    except Exception as e:
        logger.error(f"❌ Error: {e}", exc_info=True)
        return False


if __name__ == "__main__":
    # The user ID from the error message
    USER_ID = "c61e78d5-f0b4-475a-a41c-d605a0616d49"
    
    print("=" * 80)
    print("CREATING USER PROFILE")
    print("=" * 80)
    print(f"\nUser ID: {USER_ID}")
    print("\nThis will create a profile entry in the database for this user.")
    print("The user can update their profile information later through the app.")
    print()
    
    success = ensure_user_profile_exists(USER_ID)
    
    if success:
        print("\n" + "=" * 80)
        print("✅ SUCCESS - User profile is ready!")
        print("=" * 80)
        print("\nYou can now:")
        print("1. Upload your Apple Health XML file again")
        print("2. The data will be saved successfully")
        print("3. Check the dashboard to see your health metrics")
        sys.exit(0)
    else:
        print("\n" + "=" * 80)
        print("❌ FAILED - Could not create profile")
        print("=" * 80)
        print("\nPlease check:")
        print("1. Database connection is working")
        print("2. Supabase credentials are correct in .env")
        print("3. You have permission to insert into profiles table")
        sys.exit(1)
