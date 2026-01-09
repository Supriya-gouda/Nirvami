-- Migration: Add Completed column to recommendations table
-- Purpose: Track completion status of recommendations for progress analytics

-- Add Completed column to track recommendation completion
ALTER TABLE recommendations 
ADD COLUMN IF NOT EXISTS Completed TEXT CHECK (Completed IN ('YES', 'NO'));

-- Add index for filtering completed recommendations
CREATE INDEX IF NOT EXISTS idx_recommendations_completed ON recommendations(user_id, date, Completed) 
WHERE Completed IS NOT NULL;

-- Add comment
COMMENT ON COLUMN recommendations.Completed IS 'Completion status: YES, NO, or NULL (not started)';
