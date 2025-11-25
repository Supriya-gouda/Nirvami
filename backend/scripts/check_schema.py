"""Check the actual table schema."""
import os
from dotenv import load_dotenv
from supabase import create_client

load_dotenv()

def check_schema():
    """Check table schema."""
    supabase_url = os.getenv("SUPABASE_URL")
    service_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
    
    admin_client = create_client(supabase_url, service_key)
    
    # Try to get table info via a query
    result = admin_client.rpc('exec_sql', {
        'query': """
        SELECT column_name, data_type, is_nullable, column_default
        FROM information_schema.columns
        WHERE table_name = 'wearable_snapshots'
        ORDER BY ordinal_position;
        """
    }).execute()
    
    print("wearable_snapshots columns:")
    for col in result.data:
        print(f"  {col}")

if __name__ == "__main__":
    check_schema()
