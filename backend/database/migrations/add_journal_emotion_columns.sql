-- Migration: Add emotion detection columns to journal_entries
-- Date: 2025-12-16
-- Description: Adds ML emotion detection support to journal entries

-- Add emotion column
ALTER TABLE journal_entries 
ADD COLUMN IF NOT EXISTS emotion VARCHAR(50);

-- Add emotion_confidence column
ALTER TABLE journal_entries 
ADD COLUMN IF NOT EXISTS emotion_confidence FLOAT;

-- Add comments for documentation
COMMENT ON COLUMN journal_entries.emotion IS 'ML-detected emotion: joy, sadness, anger, fear, surprise, disgust, neutral';
COMMENT ON COLUMN journal_entries.emotion_confidence IS 'ML confidence score (0-1)';

-- Verify columns were added
SELECT 
    column_name, 
    data_type, 
    is_nullable
FROM information_schema.columns
WHERE table_name = 'journal_entries'
AND column_name IN ('emotion', 'emotion_confidence');
