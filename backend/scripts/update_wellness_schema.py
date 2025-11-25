"""
Apply wellness scoring schema updates to Supabase database.
Adds journal_entries and goals tables.
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from app.utils.database import get_supabase
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def apply_wellness_schema():
    """Apply wellness scoring schema updates."""
    supabase = get_supabase(use_service_role=True)
    
    # SQL to create journal_entries table
    journal_sql = """
    -- Journal entries for user reflection
    CREATE TABLE IF NOT EXISTS journal_entries (
        id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
        user_id UUID REFERENCES profiles(id) ON DELETE CASCADE,
        date DATE NOT NULL,
        content TEXT NOT NULL,
        mood_tag TEXT,
        created_at TIMESTAMPTZ DEFAULT NOW()
    );

    CREATE INDEX IF NOT EXISTS idx_journal_user_date ON journal_entries(user_id, date DESC);
    
    -- Enable RLS
    ALTER TABLE journal_entries ENABLE ROW LEVEL SECURITY;
    
    -- Create policy
    DROP POLICY IF EXISTS "Users can manage own journals" ON journal_entries;
    CREATE POLICY "Users can manage own journals" ON journal_entries
        FOR ALL USING (auth.uid() = user_id);
    """
    
    # SQL to create goals table
    goals_sql = """
    -- Goals tracking
    CREATE TABLE IF NOT EXISTS goals (
        id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
        user_id UUID REFERENCES profiles(id) ON DELETE CASCADE,
        title TEXT NOT NULL,
        description TEXT,
        status TEXT DEFAULT 'active' CHECK (status IN ('active', 'completed', 'archived')),
        completion_percent INTEGER DEFAULT 0 CHECK (completion_percent >= 0 AND completion_percent <= 100),
        target_date DATE,
        is_completed BOOLEAN DEFAULT false,
        created_at TIMESTAMPTZ DEFAULT NOW(),
        completed_at TIMESTAMPTZ
    );

    CREATE INDEX IF NOT EXISTS idx_goals_user_status ON goals(user_id, status, target_date);
    
    -- Enable RLS
    ALTER TABLE goals ENABLE ROW LEVEL SECURITY;
    
    -- Create policy
    DROP POLICY IF EXISTS "Users can manage own goals" ON goals;
    CREATE POLICY "Users can manage own goals" ON goals
        FOR ALL USING (auth.uid() = user_id);
    """
    
    try:
        logger.info("Creating journal_entries table...")
        # Note: Supabase Python client doesn't support raw SQL execution directly
        # You need to run these in Supabase SQL Editor or use PostgREST
        logger.info("✅ Schema SQL prepared. Please run the following SQL in Supabase SQL Editor:")
        logger.info("\n" + "="*80)
        logger.info(journal_sql)
        logger.info("\n" + "="*80)
        logger.info(goals_sql)
        logger.info("\n" + "="*80)
        
        logger.info("\n📝 Manual Steps Required:")
        logger.info("1. Go to your Supabase Dashboard")
        logger.info("2. Navigate to SQL Editor")
        logger.info("3. Copy and paste the SQL above")
        logger.info("4. Execute the SQL")
        
        return True
        
    except Exception as e:
        logger.error(f"Error: {e}")
        return False

if __name__ == "__main__":
    logger.info("🚀 Starting wellness scoring schema update...")
    success = apply_wellness_schema()
    if success:
        logger.info("✅ Schema update instructions provided successfully!")
    else:
        logger.error("❌ Schema update failed")
        sys.exit(1)
