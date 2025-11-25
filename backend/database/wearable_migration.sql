-- Migration script to update wearable tables to new schema
-- Run this if you have existing wearable data

-- Add new columns to wearable_snapshots if they don't exist
ALTER TABLE wearable_snapshots 
  ADD COLUMN IF NOT EXISTS source VARCHAR(20) DEFAULT 'manual',
  ADD COLUMN IF NOT EXISTS provider VARCHAR(50),
  ADD COLUMN IF NOT EXISTS captured_at TIMESTAMPTZ,
  ADD COLUMN IF NOT EXISTS hrv_ms INTEGER,
  ADD COLUMN IF NOT EXISTS calories_burned NUMERIC(6,2),
  ADD COLUMN IF NOT EXISTS raw_payload JSONB;

-- Migrate data: copy recorded_at to captured_at if null
UPDATE wearable_snapshots 
SET captured_at = recorded_at 
WHERE captured_at IS NULL AND recorded_at IS NOT NULL;

-- Migrate data: convert hrv from float to ms (multiply by 1000)
UPDATE wearable_snapshots 
SET hrv_ms = (hrv * 1000)::INTEGER 
WHERE hrv_ms IS NULL AND hrv IS NOT NULL;

-- Migrate data: set provider from device_type
UPDATE wearable_snapshots 
SET provider = device_type,
    source = 'watch'
WHERE provider IS NULL AND device_type IS NOT NULL;

-- Migrate data: convert text stress_level to numeric
UPDATE wearable_snapshots 
SET stress_level = CASE 
  WHEN stress_level::TEXT = 'low' THEN 3
  WHEN stress_level::TEXT = 'moderate' THEN 6
  WHEN stress_level::TEXT = 'high' THEN 9
  ELSE 5
END::INTEGER
WHERE stress_level IS NOT NULL 
  AND stress_level::TEXT IN ('low', 'moderate', 'high');

-- Create new indexes if they don't exist
CREATE INDEX IF NOT EXISTS idx_wearable_captured_at ON wearable_snapshots(user_id, captured_at DESC);
CREATE INDEX IF NOT EXISTS idx_wearable_source ON wearable_snapshots(user_id, source);

-- Update wearable_daily_stats structure
ALTER TABLE wearable_daily_stats
  ADD COLUMN IF NOT EXISTS min_heart_rate INTEGER,
  ADD COLUMN IF NOT EXISTS max_heart_rate INTEGER,
  ADD COLUMN IF NOT EXISTS avg_hrv_ms NUMERIC(6,2),
  ADD COLUMN IF NOT EXISTS sleep_hours NUMERIC(4,2),
  ADD COLUMN IF NOT EXISTS avg_stress_level NUMERIC(4,2),
  ADD COLUMN IF NOT EXISTS data_source VARCHAR(20);

-- Migrate existing data in daily stats
UPDATE wearable_daily_stats
SET sleep_hours = total_sleep_hours
WHERE sleep_hours IS NULL AND total_sleep_hours IS NOT NULL;

UPDATE wearable_daily_stats
SET avg_hrv_ms = avg_hrv
WHERE avg_hrv_ms IS NULL AND avg_hrv IS NOT NULL;

-- Set data_source to 'watch' for existing records
UPDATE wearable_daily_stats
SET data_source = 'watch'
WHERE data_source IS NULL;

-- Make captured_at NOT NULL after migration (if all data is migrated)
-- ALTER TABLE wearable_snapshots ALTER COLUMN captured_at SET NOT NULL;

COMMENT ON TABLE wearable_snapshots IS 'Raw health data from smartwatches or manual entry';
COMMENT ON TABLE wearable_daily_stats IS 'Aggregated daily health statistics per user';
COMMENT ON COLUMN wearable_snapshots.source IS 'Data source: watch or manual';
COMMENT ON COLUMN wearable_snapshots.provider IS 'Device provider: apple_watch, fitbit, manual_form, etc.';
COMMENT ON COLUMN wearable_snapshots.captured_at IS 'Exact time of reading';
COMMENT ON COLUMN wearable_snapshots.hrv_ms IS 'Heart rate variability in milliseconds';
COMMENT ON COLUMN wearable_daily_stats.data_source IS 'Aggregation source: watch, manual, or mixed';
