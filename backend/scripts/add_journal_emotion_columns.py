"""
Add emotion and emotion_confidence columns to journal_entries table.
Run this script to update your existing database.
"""
import os
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.utils.database import get_supabase

def add_emotion_columns():
    """Add emotion columns to journal_entries table."""
    supabase = get_supabase(use_service_role=True)
    
    print("🔧 Adding emotion columns to journal_entries table...")
    
    # SQL to add columns if they don't exist
    sql_commands = [
        """
        ALTER TABLE journal_entries 
        ADD COLUMN IF NOT EXISTS emotion VARCHAR(50);
        """,
        """
        ALTER TABLE journal_entries 
        ADD COLUMN IF NOT EXISTS emotion_confidence FLOAT;
        """,
        """
        COMMENT ON COLUMN journal_entries.emotion IS 
        'ML-detected emotion: joy, sadness, anger, fear, surprise, disgust, neutral';
        """,
        """
        COMMENT ON COLUMN journal_entries.emotion_confidence IS 
        'ML confidence score (0-1)';
        """
    ]
    
    try:
        # Execute each SQL command
        for i, sql in enumerate(sql_commands, 1):
            print(f"  [{i}/{len(sql_commands)}] Executing SQL...")
            supabase.rpc('exec_sql', {'query': sql}).execute()
        
        print("✅ Successfully added emotion columns to journal_entries table")
        print("\nColumns added:")
        print("  - emotion (VARCHAR(50))")
        print("  - emotion_confidence (FLOAT)")
        
    except Exception as e:
        print(f"❌ Error adding columns: {e}")
        print("\nAlternative: Run this SQL manually in your Supabase SQL editor:")
        print("\n".join(sql_commands))
        sys.exit(1)

if __name__ == "__main__":
    add_emotion_columns()
