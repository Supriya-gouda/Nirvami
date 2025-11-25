-- Update emotion_logs table to support mood logging from popup
-- Add missing columns: mood, intensity, energy, notes, logged_at
-- Make emotion_type, confidence, all_scores nullable for mood-only logs OR provide defaults

-- First, make NOT NULL constraints more flexible for mood logging
ALTER TABLE emotion_logs 
ALTER COLUMN emotion_type DROP NOT NULL,
ALTER COLUMN confidence DROP NOT NULL,
ALTER COLUMN all_scores DROP NOT NULL;

-- Add new columns for mood popup
ALTER TABLE emotion_logs 
ADD COLUMN IF NOT EXISTS mood TEXT,
ADD COLUMN IF NOT EXISTS intensity INTEGER CHECK (intensity >= 1 AND intensity <= 10),
ADD COLUMN IF NOT EXISTS energy INTEGER CHECK (energy >= 1 AND energy <= 10),
ADD COLUMN IF NOT EXISTS notes TEXT,
ADD COLUMN IF NOT EXISTS logged_at TIMESTAMPTZ DEFAULT NOW();

-- Update source column to support mood_popup
ALTER TABLE emotion_logs 
DROP CONSTRAINT IF EXISTS emotion_logs_source_check;

ALTER TABLE emotion_logs 
ADD CONSTRAINT emotion_logs_source_check 
CHECK (source IN ('text', 'voice', 'manual', 'mood_popup', 'wearable'));

-- Create index for faster mood queries
CREATE INDEX IF NOT EXISTS idx_emotion_logs_mood ON emotion_logs(user_id, mood, logged_at DESC);

COMMENT ON COLUMN emotion_logs.mood IS 'User selected mood: joy, sadness, anger, fear, anxiety, stress, calm, neutral';
COMMENT ON COLUMN emotion_logs.intensity IS 'Mood intensity on scale of 1-10';
COMMENT ON COLUMN emotion_logs.energy IS 'Energy level on scale of 1-10';
COMMENT ON COLUMN emotion_logs.notes IS 'Optional user notes about their mood';
COMMENT ON COLUMN emotion_logs.logged_at IS 'When the mood was logged (may differ from created_at for backdated entries)';
COMMENT ON COLUMN emotion_logs.emotion_type IS 'Detected or mapped emotion type (nullable for mood-only logs)';
COMMENT ON COLUMN emotion_logs.confidence IS 'Confidence score 0-1 (nullable for mood-only logs)';
COMMENT ON COLUMN emotion_logs.all_scores IS 'Full emotion score breakdown (nullable for mood-only logs)';
