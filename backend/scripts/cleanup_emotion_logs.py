"""
Script to clean up redundant columns from emotion_logs table.

IMPORTANT: Run this script to remove duplicate columns that are no longer needed.

COLUMNS TO BE REMOVED (redundant):
✗ mood - Duplicates emotion_type
✗ intensity - Stored in all_scores JSON
✗ energy - Stored in all_scores JSON  
✗ notes - Stored in all_scores JSON
✗ logged_at - Duplicates created_at

COLUMNS THAT WILL REMAIN (essential):
✓ id - Primary key
✓ user_id - User reference
✓ message_id - For chat integration (nullable)
✓ emotion_type - The mood (happy, sad, anxious, etc.)
✓ confidence - Intensity as 0-1 scale
✓ all_scores - JSON with all mood data {mood, intensity, energy, notes}
✓ source - Log source (manual, text, voice)
✓ created_at - Timestamp

After cleanup, all mood data will be properly stored in:
  - emotion_type: The mood name
  - all_scores: JSON containing intensity, energy, notes, sub_source
"""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

SUPABASE_URL = os.getenv('SUPABASE_URL')

print("=" * 70)
print("🧹 EMOTION_LOGS TABLE CLEANUP")
print("=" * 70)
print("\n📋 REDUNDANT COLUMNS TO REMOVE:")
print("   ✗ mood (duplicates emotion_type)")
print("   ✗ intensity (duplicates all_scores.intensity)")
print("   ✗ energy (duplicates all_scores.energy)")
print("   ✗ notes (duplicates all_scores.notes)")
print("   ✗ logged_at (duplicates created_at)")
print("\n✅ ESSENTIAL COLUMNS TO KEEP:")
print("   ✓ id, user_id, message_id, emotion_type, confidence, all_scores, source, created_at")
print("\n" + "=" * 70)
print("📝 INSTRUCTIONS:")
print("=" * 70)
print("\n1. Open Supabase SQL Editor:")
print(f"   {SUPABASE_URL.replace('https://', 'https://app.')}/project/_/sql")
print("\n2. Copy and run the SQL from:")
print("   backend/database/cleanup_emotion_logs.sql")
print("\n3. This will:")
print("   - Remove all redundant columns")
print("   - Keep only essential columns")
print("   - All mood data will be in 'all_scores' JSON field")
print("\n4. After cleanup, mood logs will look like:")
print("   {")
print('     "id": "uuid",')
print('     "user_id": "uuid",')
print('     "emotion_type": "happy",')
print('     "confidence": 0.5,')
print('     "all_scores": {"mood": "happy", "intensity": 5, "energy": 7, "notes": "..."},')
print('     "source": "manual",')
print('     "created_at": "timestamp"')
print("   }")
print("\n" + "=" * 70)
print("⚠️  NOTE: This operation cannot be undone!")
print("=" * 70)
