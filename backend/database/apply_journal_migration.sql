-- ====================================
-- Journal Feature Migration
-- Run this in Supabase SQL Editor
-- ====================================

-- 1. Ensure journal_entries table exists with base structure
CREATE TABLE IF NOT EXISTS journal_entries (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES profiles(id) ON DELETE CASCADE,
    date DATE NOT NULL,
    content TEXT NOT NULL,
    mood_tag TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 2. Add emotion columns to journal_entries (if not exists)
DO $$ 
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'journal_entries' AND column_name = 'emotion'
    ) THEN
        ALTER TABLE journal_entries ADD COLUMN emotion TEXT;
    END IF;

    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'journal_entries' AND column_name = 'emotion_confidence'
    ) THEN
        ALTER TABLE journal_entries ADD COLUMN emotion_confidence DOUBLE PRECISION;
    END IF;
END $$;

-- 3. Create journal_insights table for Gemini-generated summaries
CREATE TABLE IF NOT EXISTS journal_insights (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES profiles(id) ON DELETE CASCADE,
    date DATE NOT NULL,
    summary JSONB NOT NULL, -- {summary, dominant_emotions, patterns, positive_signals, gentle_suggestion}
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(user_id, date)
);

-- 4. Create indexes for faster queries
CREATE INDEX IF NOT EXISTS idx_journal_user_date ON journal_entries(user_id, date DESC);
CREATE INDEX IF NOT EXISTS idx_journal_entries_emotion ON journal_entries(emotion);
CREATE INDEX IF NOT EXISTS idx_journal_insights_user_date ON journal_insights(user_id, date);
CREATE INDEX IF NOT EXISTS idx_journal_insights_date ON journal_insights(date);

-- 5. Enable RLS on both tables
ALTER TABLE journal_entries ENABLE ROW LEVEL SECURITY;
ALTER TABLE journal_insights ENABLE ROW LEVEL SECURITY;

-- 6. Drop ALL existing policies on both tables (to avoid conflicts)
DO $$ 
DECLARE
    r RECORD;
BEGIN
    -- Drop all policies on journal_entries
    FOR r IN (SELECT policyname FROM pg_policies WHERE tablename = 'journal_entries') LOOP
        EXECUTE 'DROP POLICY IF EXISTS "' || r.policyname || '" ON journal_entries';
    END LOOP;
    
    -- Drop all policies on journal_insights
    FOR r IN (SELECT policyname FROM pg_policies WHERE tablename = 'journal_insights') LOOP
        EXECUTE 'DROP POLICY IF EXISTS "' || r.policyname || '" ON journal_insights';
    END LOOP;
END $$;

-- 7. Create RLS policies for journal_entries
CREATE POLICY "Users can view own journals" ON journal_entries
    FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Users can insert own journals" ON journal_entries
    FOR INSERT WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update own journals" ON journal_entries
    FOR UPDATE USING (auth.uid() = user_id);

CREATE POLICY "Users can delete own journals" ON journal_entries
    FOR DELETE USING (auth.uid() = user_id);

-- 8. Create RLS policies for journal_insights  
CREATE POLICY "Users can view their own insights" ON journal_insights
    FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Users can insert their own insights" ON journal_insights
    FOR INSERT WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update their own insights" ON journal_insights
    FOR UPDATE USING (auth.uid() = user_id);

CREATE POLICY "Users can delete their own insights" ON journal_insights
    FOR DELETE USING (auth.uid() = user_id);

-- 9. Verify tables exist
SELECT 
    'journal_entries' as table_name,
    COUNT(*) as column_count
FROM information_schema.columns 
WHERE table_name = 'journal_entries'
UNION ALL
SELECT 
    'journal_insights' as table_name,
    COUNT(*) as column_count
FROM information_schema.columns 
WHERE table_name = 'journal_insights';

-- Done! Journal feature is now ready to use.
