"""Create user profile using service role key to bypass RLS."""
import os
from supabase import create_client, Client
from dotenv import load_dotenv
import logging

# Load environment variables
load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def create_profile_with_service_role(user_id: str, email: str = None) -> bool:
    """
    Create a user profile using service role key to bypass RLS.
    
    Args:
        user_id: The user's UUID
        email: Optional email address
        
    Returns:
        True if successful, False otherwise
    """
    # Get service role credentials
    supabase_url = os.getenv("SUPABASE_URL")
    service_role_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
    
    if not supabase_url or not service_role_key:
        logger.error("Missing SUPABASE_URL or SUPABASE_SERVICE_ROLE_KEY in environment")
        return False
    
    # Create admin client with service role
    admin_client: Client = create_client(supabase_url, service_role_key)
    
    try:
        # Check if profile exists
        result = admin_client.table('profiles').select('*').eq('id', user_id).execute()
        
        if result.data and len(result.data) > 0:
            logger.info(f"✅ Profile already exists for user {user_id}")
            logger.info(f"   Email: {result.data[0].get('email')}")
            logger.info(f"   Name: {result.data[0].get('full_name', 'Not set')}")
            return True
        
        # Create profile
        logger.info(f"Creating profile for user {user_id}...")
        
        profile_data = {
            'id': user_id,
            'email': email or f"user_{user_id[:8]}@nirvami.app",
            'full_name': 'Nirvami User',
            'consent_data_collection': True,
            'consent_ai_processing': True,
            'consent_notifications': True,
            'timezone': 'UTC'
        }
        
        insert_result = admin_client.table('profiles').insert(profile_data).execute()
        
        if insert_result.data:
            logger.info(f"✅ Profile created successfully!")
            logger.info(f"   User ID: {user_id}")
            logger.info(f"   Email: {profile_data['email']}")
            
            # Create user preferences
            try:
                prefs_data = {
                    'user_id': user_id,
                    'notification_email': True,
                    'notification_sms': False,
                    'notification_push': True,
                    'crisis_alerts_enabled': True,
                    'data_retention_days': 365
                }
                admin_client.table('user_preferences').insert(prefs_data).execute()
                logger.info(f"✅ User preferences created")
            except Exception as pref_error:
                logger.warning(f"⚠️  Could not create preferences: {pref_error}")
            
            return True
        else:
            logger.error(f"❌ Failed to create profile - no data returned")
            return False
            
    except Exception as e:
        logger.error(f"❌ Error creating profile: {e}", exc_info=True)
        return False


if __name__ == "__main__":
    import sys
    
    # The user ID from the error message
    USER_ID = "c61e78d5-f0b4-475a-a41c-d605a0616d49"
    
    print("=" * 80)
    print("CREATING USER PROFILE (Using Service Role)")
    print("=" * 80)
    print(f"\nUser ID: {USER_ID}")
    print("\nThis will create a profile using admin privileges.")
    print()
    
    success = create_profile_with_service_role(USER_ID)
    
    if success:
        print("\n" + "=" * 80)
        print("✅ SUCCESS - User profile created!")
        print("=" * 80)
        print("\nYou can now:")
        print("1. Upload your Apple Health XML file again")
        print("2. Data will be saved successfully")
        print("3. Check the dashboard to see your health metrics")
        print("\nThe user can update their profile information through the app.")
        sys.exit(0)
    else:
        print("\n" + "=" * 80)
        print("❌ FAILED - Could not create profile")
        print("=" * 80)
        print("\nPlease check the error messages above.")
        sys.exit(1)
