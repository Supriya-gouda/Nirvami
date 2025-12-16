"""
Apply journal emotion schema updates
Adds emotion tracking to journal entries and creates insights table.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.utils.database import get_supabase
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def apply_schema():
    """Apply the journal emotion schema updates."""
    supabase = get_supabase()
    
    # Read the schema file
    schema_path = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        'database',
        'journal_emotion_schema.sql'
    )
    
    with open(schema_path, 'r') as f:
        schema_sql = f.read()
    
    logger.info("Applying journal emotion schema...")
    
    try:
        # Execute the schema
        result = supabase.rpc('exec_sql', {'sql': schema_sql}).execute()
        logger.info("✅ Schema applied successfully!")
        return True
    except Exception as e:
        logger.error(f"❌ Error applying schema: {e}")
        logger.info("Manual application may be required. SQL file location:")
        logger.info(schema_path)
        return False

if __name__ == "__main__":
    success = apply_schema()
    sys.exit(0 if success else 1)
