"""Update guideline_type constraint to allow new types."""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.utils.database import get_supabase

def update_constraint():
    """Update guideline_type check constraint"""
    supabase = get_supabase(use_service_role=True)
    
    print("⚠️  This script needs to be run manually in Supabase SQL Editor:")
    print("\n" + "="*60)
    print("SQL to execute in Supabase dashboard (SQL Editor):")
    print("="*60 + "\n")
    
    sql = """
-- Drop the old constraint
ALTER TABLE meal_ayurveda_guidelines DROP CONSTRAINT IF EXISTS guideline_type_check;

-- Add the new constraint with additional types
ALTER TABLE meal_ayurveda_guidelines ADD CONSTRAINT guideline_type_check
CHECK (guideline_type = ANY(ARRAY['avoid', 'favor', 'balance', 'health', 'dosha', 'mood', 'general']));
"""
    
    print(sql)
    print("\n" + "="*60)
    print("\nSteps:")
    print("1. Go to your Supabase dashboard")
    print("2. Click on 'SQL Editor'")
    print("3. Copy and paste the SQL above")
    print("4. Click 'Run'")
    print("\nThis will update the constraint to allow: health, dosha, mood, general types")

if __name__ == "__main__":
    update_constraint()
