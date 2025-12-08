"""Update meal_emotion_correlations table schema to include additional fields."""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.utils.database import get_supabase

def update_schema():
    """Add new columns to meal_emotion_correlations table"""
    supabase = get_supabase(use_service_role=True)
    
    try:
        # Add new columns using SQL
        sql_commands = [
            """
            ALTER TABLE meal_emotion_correlations 
            ADD COLUMN IF NOT EXISTS emotion_type TEXT,
            ADD COLUMN IF NOT EXISTS emotion_intensity DOUBLE PRECISION,
            ADD COLUMN IF NOT EXISTS meal_type TEXT,
            ADD COLUMN IF NOT EXISTS ingredients JSONB,
            ADD COLUMN IF NOT EXISTS dosha_impact JSONB;
            """,
        ]
        
        for sql in sql_commands:
            try:
                result = supabase.rpc('exec_sql', {'sql': sql}).execute()
                print(f"✅ Executed SQL successfully")
            except Exception as e:
                print(f"Note: {e}")
                print("Columns may already exist or need manual addition via Supabase dashboard")
        
        print("\n✅ Schema update completed!")
        print("\nIf columns weren't added automatically, please add them manually in Supabase:")
        print("1. Go to Table Editor > meal_emotion_correlations")
        print("2. Add columns:")
        print("   - emotion_type (text)")
        print("   - emotion_intensity (float8)")
        print("   - meal_type (text)")
        print("   - ingredients (jsonb)")
        print("   - dosha_impact (jsonb)")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        print("\nPlease add columns manually in Supabase dashboard:")
        print("1. Go to Table Editor > meal_emotion_correlations")
        print("2. Add the columns listed above")

if __name__ == "__main__":
    update_schema()
