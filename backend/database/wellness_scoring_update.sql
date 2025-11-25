-- ============================================
-- WELLNESS SCORING SCHEMA UPDATE
-- Adds journal_entries and goals tables
-- Run this in Supabase SQL Editor
-- ============================================

-- Journal entries for user reflection
CREATE TABLE IF NOT EXISTS journal_entries (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    user_id UUID REFERENCES profiles(id) ON DELETE CASCADE,
    date DATE NOT NULL,
    content TEXT NOT NULL,
    mood_tag TEXT, -- e.g., 'happy', 'stressed', 'calm', 'anxious'
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_journal_user_date ON journal_entries(user_id, date DESC);

-- Goals tracking
CREATE TABLE IF NOT EXISTS goals (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    user_id UUID REFERENCES profiles(id) ON DELETE CASCADE,
    title TEXT NOT NULL,
    description TEXT,
    status TEXT DEFAULT 'active' CHECK (status IN ('active', 'completed', 'archived')),
    completion_percent INTEGER DEFAULT 0 CHECK (completion_percent >= 0 AND completion_percent <= 100),
    target_date DATE,
    is_completed BOOLEAN DEFAULT false,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    completed_at TIMESTAMPTZ
);

CREATE INDEX IF NOT EXISTS idx_goals_user_status ON goals(user_id, status, target_date);

-- Enable Row Level Security
ALTER TABLE journal_entries ENABLE ROW LEVEL SECURITY;
ALTER TABLE goals ENABLE ROW LEVEL SECURITY;

-- Create RLS Policies for journal_entries
DROP POLICY IF EXISTS "Users can manage own journals" ON journal_entries;
CREATE POLICY "Users can manage own journals" ON journal_entries
    FOR ALL USING (auth.uid() = user_id);

-- Create RLS Policies for goals
DROP POLICY IF EXISTS "Users can manage own goals" ON goals;
CREATE POLICY "Users can manage own goals" ON goals
    FOR ALL USING (auth.uid() = user_id);

-- Verify tables were created
SELECT 'journal_entries table created' as status 
WHERE EXISTS (
    SELECT FROM information_schema.tables 
    WHERE table_name = 'journal_entries'
);

SELECT 'goals table created' as status 
WHERE EXISTS (
    SELECT FROM information_schema.tables 
    WHERE table_name = 'goals'
);
