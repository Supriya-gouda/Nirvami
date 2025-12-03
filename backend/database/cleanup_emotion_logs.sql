-- ============================================
-- CLEANUP REDUNDANT COLUMNS FROM emotion_logs
-- ============================================
-- 
-- This script removes duplicate/redundant columns from emotion_logs table.
-- All data is already stored in the required core columns:
--   - emotion_type (stores the mood)
--   - all_scores (JSON containing mood, intensity, energy, notes)
--   - created_at (timestamp)
--
-- REDUNDANT COLUMNS TO REMOVE:
--   - mood: Duplicates emotion_type
--   - intensity: Duplicates all_scores.intensity
--   - energy: Duplicates all_scores.energy
--   - notes: Duplicates all_scores.notes
--   - logged_at: Duplicates created_at
--
-- KEEPING message_id for potential future chat integration
-- ============================================

-- Drop redundant columns
ALTER TABLE emotion_logs DROP COLUMN IF EXISTS mood;
ALTER TABLE emotion_logs DROP COLUMN IF EXISTS intensity;
ALTER TABLE emotion_logs DROP COLUMN IF EXISTS energy;
ALTER TABLE emotion_logs DROP COLUMN IF EXISTS notes;
ALTER TABLE emotion_logs DROP COLUMN IF EXISTS logged_at;

-- Verify the final schema
-- The table should now have only these essential columns:
--   id, user_id, message_id, emotion_type, confidence, all_scores, source, created_at

COMMENT ON TABLE emotion_logs IS 'Stores user emotion/mood logs with all data in JSON format';
COMMENT ON COLUMN emotion_logs.emotion_type IS 'The primary mood/emotion (e.g., happy, sad, anxious)';
COMMENT ON COLUMN emotion_logs.confidence IS 'Confidence score (0-1), derived from intensity/10';
COMMENT ON COLUMN emotion_logs.all_scores IS 'JSON containing mood, intensity (1-10), optional energy (1-10) and notes';
COMMENT ON COLUMN emotion_logs.source IS 'Source of the log: text, voice, or manual';
