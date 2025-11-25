-- Fresh Wearable Health Data Schema
-- Drop old tables and create clean new structure

-- Drop old tables
DROP TABLE IF EXISTS wearable_daily_stats CASCADE;
DROP TABLE IF EXISTS wearable_snapshots CASCADE;

-- Create fresh wearable_snapshots table matching frontend fields exactly
CREATE TABLE wearable_snapshots (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    user_id UUID NOT NULL REFERENCES profiles(id) ON DELETE CASCADE,
    
    -- Metadata
    date DATE NOT NULL,                      -- Date of entry (YYYY-MM-DD)
    source VARCHAR(20) NOT NULL DEFAULT 'manual', -- 'manual' or 'watch'
    created_at TIMESTAMPTZ DEFAULT NOW(),
    
    -- Health Metrics (matching frontend exactly)
    sleep_hours NUMERIC(4,2),                -- Sleep hours (0-24)
    avg_heart_rate INTEGER,                   -- Average heart rate in bpm
    steps INTEGER,                            -- Steps walked
    stress_level INTEGER CHECK (stress_level BETWEEN 1 AND 10), -- Stress (1-10)
    calories_burned NUMERIC(6,2),            -- Calories burned
    
    -- Additional optional fields
    hrv_ms INTEGER,                          -- Heart rate variability
    
    -- Constraints
    CONSTRAINT unique_user_date_source UNIQUE(user_id, date, source)
);

-- Create indexes
CREATE INDEX idx_wearable_user_date ON wearable_snapshots(user_id, date DESC);
CREATE INDEX idx_wearable_source ON wearable_snapshots(user_id, source);

-- Enable RLS
ALTER TABLE wearable_snapshots ENABLE ROW LEVEL SECURITY;

-- RLS Policies
CREATE POLICY "Users can view own wearable data" ON wearable_snapshots
    FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Users can insert own wearable data" ON wearable_snapshots
    FOR INSERT WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update own wearable data" ON wearable_snapshots
    FOR UPDATE USING (auth.uid() = user_id);

CREATE POLICY "Users can delete own wearable data" ON wearable_snapshots
    FOR DELETE USING (auth.uid() = user_id);

-- Comments
COMMENT ON TABLE wearable_snapshots IS 'Health data from smartwatches or manual entry';
COMMENT ON COLUMN wearable_snapshots.source IS 'Data source: manual or watch';
COMMENT ON COLUMN wearable_snapshots.date IS 'Date of the health entry (not timestamp)';
COMMENT ON COLUMN wearable_snapshots.sleep_hours IS 'Hours of sleep (0-24)';
COMMENT ON COLUMN wearable_snapshots.avg_heart_rate IS 'Average heart rate in beats per minute';
COMMENT ON COLUMN wearable_snapshots.steps IS 'Number of steps walked';
COMMENT ON COLUMN wearable_snapshots.stress_level IS 'Self-reported stress level (1-10)';
COMMENT ON COLUMN wearable_snapshots.calories_burned IS 'Calories burned';
