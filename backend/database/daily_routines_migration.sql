-- ============================================
-- DAILY ROUTINES (Dinacharya) TABLE MIGRATION
-- ============================================
-- This migration adds support for tracking daily routine activities
-- Allows multiple routine entries per day for better Ayurvedic dinacharya tracking

-- Create daily_routines table
CREATE TABLE IF NOT EXISTS daily_routines (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    user_id UUID REFERENCES profiles(id) ON DELETE CASCADE,
    date DATE NOT NULL,
    time TIME NOT NULL,
    activity TEXT NOT NULL,
    notes TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Create indexes for efficient queries
CREATE INDEX idx_daily_routines_user_date ON daily_routines(user_id, date DESC);
CREATE INDEX idx_daily_routines_user_time ON daily_routines(user_id, date DESC, time);

-- Enable Row Level Security
ALTER TABLE daily_routines ENABLE ROW LEVEL SECURITY;

-- Create RLS policy (users can only manage their own routines)
CREATE POLICY "Users can manage own routines" ON daily_routines
    FOR ALL USING (auth.uid() = user_id);

-- Verify table was created
SELECT 
    table_name, 
    column_name, 
    data_type 
FROM information_schema.columns 
WHERE table_name = 'daily_routines' 
ORDER BY ordinal_position;
