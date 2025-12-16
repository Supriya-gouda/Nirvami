-- Add emotion columns to journal_entries table
ALTER TABLE journal_entries 
ADD COLUMN IF NOT EXISTS emotion TEXT,
ADD COLUMN IF NOT EXISTS emotion_confidence FLOAT;

-- Create journal_insights table for Gemini-generated summaries
CREATE TABLE IF NOT EXISTS journal_insights (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES profiles(id) ON DELETE CASCADE,
    date DATE NOT NULL,
    summary JSONB NOT NULL, -- {summary, dominant_emotions, patterns, positive_signals, gentle_suggestion}
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(user_id, date)
);

-- Index for faster queries
CREATE INDEX IF NOT EXISTS idx_journal_insights_user_date ON journal_insights(user_id, date);
CREATE INDEX IF NOT EXISTS idx_journal_insights_date ON journal_insights(date);
CREATE INDEX IF NOT EXISTS idx_journal_entries_emotion ON journal_entries(emotion);

-- Enable RLS
ALTER TABLE journal_insights ENABLE ROW LEVEL SECURITY;

-- RLS policies for journal_insights
CREATE POLICY "Users can view their own insights" ON journal_insights
    FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Users can insert their own insights" ON journal_insights
    FOR INSERT WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update their own insights" ON journal_insights
    FOR UPDATE USING (auth.uid() = user_id);

CREATE POLICY "Users can delete their own insights" ON journal_insights
    FOR DELETE USING (auth.uid() = user_id);
