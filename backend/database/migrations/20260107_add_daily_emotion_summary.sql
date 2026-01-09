-- Migration: Add daily_emotion_summary table
-- Created: 2026-01-07
-- Purpose: Store daily emotion trend percentages for efficient graph rendering

CREATE TABLE IF NOT EXISTS daily_emotion_summary (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    user_id UUID REFERENCES profiles(id) ON DELETE CASCADE,
    date DATE NOT NULL,
    positive_percent FLOAT NOT NULL CHECK (positive_percent >= 0 AND positive_percent <= 100),
    negative_percent FLOAT NOT NULL CHECK (negative_percent >= 0 AND negative_percent <= 100),
    neutral_percent FLOAT NOT NULL CHECK (neutral_percent >= 0 AND neutral_percent <= 100),
    total_weighted_count FLOAT NOT NULL DEFAULT 0,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(user_id, date)
);

-- Index for fast querying by user and date range
CREATE INDEX idx_daily_emotion_summary_user_date ON daily_emotion_summary(user_id, date DESC);

-- Add constraint to ensure percentages sum to 100
ALTER TABLE daily_emotion_summary 
ADD CONSTRAINT check_percentages_sum_100 
CHECK (ABS((positive_percent + negative_percent + neutral_percent) - 100.0) < 0.01);

-- Enable RLS
ALTER TABLE daily_emotion_summary ENABLE ROW LEVEL SECURITY;

-- Policy: Users can only access their own emotion summaries
CREATE POLICY daily_emotion_summary_user_policy ON daily_emotion_summary
    FOR ALL
    USING (auth.uid() = user_id);
