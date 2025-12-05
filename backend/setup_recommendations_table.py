"""
Script to apply the new recommendations table to the database
"""
import os
import sys
from app.utils.database import get_supabase

def create_recommendations_table():
    """Apply the recommendations table schema to the database"""
    
    # SQL to create the recommendations table
    create_table_sql = """
    -- Unified recommendations from chat AI and device analysis
    CREATE TABLE IF NOT EXISTS recommendations (
        id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
        user_id UUID REFERENCES profiles(id) ON DELETE CASCADE,
        date DATE NOT NULL,
        source TEXT NOT NULL CHECK (source IN ('chat', 'device', 'system')),
        category TEXT NOT NULL CHECK (category IN ('yoga', 'ayurveda', 'lifestyle', 'sleep', 'breathing', 'meditation', 'diet')),
        title TEXT NOT NULL,
        content TEXT NOT NULL,
        created_at TIMESTAMPTZ DEFAULT NOW(),
        meta JSONB DEFAULT '{}'::jsonb
    );

    CREATE INDEX IF NOT EXISTS idx_recommendations_user_date ON recommendations(user_id, date DESC);
    CREATE INDEX IF NOT EXISTS idx_recommendations_category ON recommendations(category);
    CREATE INDEX IF NOT EXISTS idx_recommendations_source ON recommendations(source);

    -- Unique constraint to prevent exact duplicates per user/date/category
    CREATE UNIQUE INDEX IF NOT EXISTS idx_recommendations_dedup ON recommendations(user_id, date, category, md5(content));

    COMMENT ON TABLE recommendations IS 'Unified daily recommendations from AI chat and device analysis';
    """
    
    try:
        supabase = get_supabase(use_service_role=True)
        
        print("Creating recommendations table...")
        
        # Execute the SQL using Supabase's RPC functionality
        result = supabase.rpc('exec_sql', {'sql': create_table_sql}).execute()
        
        print("✅ Recommendations table created successfully!")
        
        # Test if table exists by trying to query it
        test_result = supabase.table("recommendations").select("id").limit(1).execute()
        print("✅ Table verification successful - recommendations table is accessible!")
        
        return True
        
    except Exception as e:
        print(f"❌ Error creating recommendations table: {e}")
        print("\nTrying alternative approach...")
        
        # Alternative: Try to create table using direct SQL execution
        try:
            # This assumes you have a way to execute raw SQL in your Supabase setup
            print("Please manually run the following SQL in your Supabase SQL editor:")
            print("\n" + "="*50)
            print(create_table_sql)
            print("="*50)
            print("\nAfter running the SQL, the recommendation system will work properly.")
            return False
        except Exception as e2:
            print(f"❌ Alternative approach also failed: {e2}")
            return False

if __name__ == "__main__":
    success = create_recommendations_table()
    if success:
        print("\n🎉 Database setup complete! Recommendation system is ready to use.")
    else:
        print("\n⚠️ Manual SQL execution required. See instructions above.")