-- Practice Sessions Schema for Nirvami
-- Tracks user practice completions for recommendations (yoga, breathing, meditation, etc.)

-- Practice sessions table - tracks individual practice completions
CREATE TABLE IF NOT EXISTS practice_sessions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES profiles(id) ON DELETE CASCADE,
    recommendation_id UUID REFERENCES recommendations(id) ON DELETE SET NULL,
    practice_type TEXT NOT NULL, -- 'yoga', 'breathing', 'meditation', 'lifestyle'
    practice_name TEXT NOT NULL, -- e.g., "Child's Pose", "4-7-8 Breathing"
    duration_minutes INTEGER NOT NULL DEFAULT 0,
    completed_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    completion_status TEXT DEFAULT 'completed', -- 'completed', 'partially_completed', 'skipped'
    notes TEXT,
    difficulty_rating INTEGER CHECK (difficulty_rating >= 1 AND difficulty_rating <= 5),
    satisfaction_rating INTEGER CHECK (satisfaction_rating >= 1 AND satisfaction_rating <= 5),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Practice content library - extended details for each practice with YouTube videos and steps
CREATE TABLE IF NOT EXISTS practice_content (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    practice_type TEXT NOT NULL, -- 'yoga', 'breathing', 'meditation', 'lifestyle'
    practice_name TEXT NOT NULL UNIQUE, -- e.g., "Child's Pose"
    sanskrit_name TEXT,
    description TEXT,
    benefits TEXT[],
    difficulty TEXT, -- 'beginner', 'intermediate', 'advanced'
    duration_min INTEGER DEFAULT 1,
    duration_max INTEGER DEFAULT 5,
    youtube_video_id TEXT, -- YouTube video ID for Learn section
    youtube_title TEXT,
    avatar_animation_steps JSONB, -- Step-by-step animation instructions
    tts_instructions TEXT[], -- Array of instructions for text-to-speech
    dosha_tags TEXT[],
    emotion_tags TEXT[],
    category TEXT,
    icon TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- User practice streaks - gamification
CREATE TABLE IF NOT EXISTS practice_streaks (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES profiles(id) ON DELETE CASCADE,
    current_streak INTEGER DEFAULT 0,
    longest_streak INTEGER DEFAULT 0,
    total_sessions INTEGER DEFAULT 0,
    last_practice_date DATE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(user_id)
);

-- User practice goals
CREATE TABLE IF NOT EXISTS practice_goals (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES profiles(id) ON DELETE CASCADE,
    goal_type TEXT NOT NULL, -- 'daily_minutes', 'weekly_sessions', 'specific_practice'
    target_value INTEGER NOT NULL,
    current_progress INTEGER DEFAULT 0,
    start_date DATE NOT NULL DEFAULT CURRENT_DATE,
    end_date DATE,
    status TEXT DEFAULT 'active', -- 'active', 'completed', 'abandoned'
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_practice_sessions_user_id ON practice_sessions(user_id);
CREATE INDEX IF NOT EXISTS idx_practice_sessions_completed_at ON practice_sessions(completed_at DESC);
CREATE INDEX IF NOT EXISTS idx_practice_sessions_type ON practice_sessions(practice_type);
CREATE INDEX IF NOT EXISTS idx_practice_content_type ON practice_content(practice_type);
CREATE INDEX IF NOT EXISTS idx_practice_content_name ON practice_content(practice_name);
CREATE INDEX IF NOT EXISTS idx_practice_streaks_user_id ON practice_streaks(user_id);
CREATE INDEX IF NOT EXISTS idx_practice_goals_user_id ON practice_goals(user_id);

-- Row-Level Security (RLS) Policies
ALTER TABLE practice_sessions ENABLE ROW LEVEL SECURITY;
ALTER TABLE practice_streaks ENABLE ROW LEVEL SECURITY;
ALTER TABLE practice_goals ENABLE ROW LEVEL SECURITY;

-- Users can only see their own practice sessions
CREATE POLICY "Users can view own practice sessions"
    ON practice_sessions FOR SELECT
    USING (auth.uid() = user_id);

CREATE POLICY "Users can insert own practice sessions"
    ON practice_sessions FOR INSERT
    WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update own practice sessions"
    ON practice_sessions FOR UPDATE
    USING (auth.uid() = user_id);

-- Users can view their own streaks
CREATE POLICY "Users can view own practice streaks"
    ON practice_streaks FOR SELECT
    USING (auth.uid() = user_id);

CREATE POLICY "Users can insert own practice streaks"
    ON practice_streaks FOR INSERT
    WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update own practice streaks"
    ON practice_streaks FOR UPDATE
    USING (auth.uid() = user_id);

-- Users can view their own goals
CREATE POLICY "Users can view own practice goals"
    ON practice_goals FOR SELECT
    USING (auth.uid() = user_id);

CREATE POLICY "Users can insert own practice goals"
    ON practice_goals FOR INSERT
    WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update own practice goals"
    ON practice_goals FOR UPDATE
    USING (auth.uid() = user_id);

-- Practice content is publicly readable
ALTER TABLE practice_content ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Practice content is publicly readable"
    ON practice_content FOR SELECT
    TO authenticated
    USING (true);

-- Trigger to update practice streaks
CREATE OR REPLACE FUNCTION update_practice_streak()
RETURNS TRIGGER AS $$
BEGIN
    INSERT INTO practice_streaks (user_id, current_streak, longest_streak, total_sessions, last_practice_date)
    VALUES (
        NEW.user_id,
        1,
        1,
        1,
        CURRENT_DATE
    )
    ON CONFLICT (user_id) DO UPDATE SET
        total_sessions = practice_streaks.total_sessions + 1,
        current_streak = CASE
            WHEN practice_streaks.last_practice_date = CURRENT_DATE THEN practice_streaks.current_streak
            WHEN practice_streaks.last_practice_date = CURRENT_DATE - INTERVAL '1 day' THEN practice_streaks.current_streak + 1
            ELSE 1
        END,
        longest_streak = GREATEST(
            practice_streaks.longest_streak,
            CASE
                WHEN practice_streaks.last_practice_date = CURRENT_DATE THEN practice_streaks.current_streak
                WHEN practice_streaks.last_practice_date = CURRENT_DATE - INTERVAL '1 day' THEN practice_streaks.current_streak + 1
                ELSE 1
            END
        ),
        last_practice_date = CURRENT_DATE,
        updated_at = NOW();
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Attach trigger to practice_sessions
DROP TRIGGER IF EXISTS trigger_update_practice_streak ON practice_sessions;
CREATE TRIGGER trigger_update_practice_streak
    AFTER INSERT ON practice_sessions
    FOR EACH ROW
    EXECUTE FUNCTION update_practice_streak();

COMMENT ON TABLE practice_sessions IS 'Tracks individual practice session completions';
COMMENT ON TABLE practice_content IS 'Extended practice details with YouTube videos and animation steps';
COMMENT ON TABLE practice_streaks IS 'User practice streaks and statistics';
COMMENT ON TABLE practice_goals IS 'User-defined practice goals';
