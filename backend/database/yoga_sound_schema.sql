-- ============================================
-- YOGA POSES TABLE
-- ============================================
CREATE TABLE IF NOT EXISTS yoga_poses (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    name TEXT NOT NULL,
    sanskrit_name TEXT,
    duration_min INTEGER NOT NULL,  -- Duration in seconds
    duration_max INTEGER NOT NULL,
    difficulty TEXT CHECK (difficulty IN ('beginner', 'intermediate', 'advanced')),
    dosha_tags TEXT[] NOT NULL,  -- ['vata', 'pitta', 'kapha']
    emotion_tags TEXT[] NOT NULL,  -- ['anxious', 'calm', 'energized', etc.]
    benefits TEXT[] NOT NULL,
    instructions TEXT,
    icon TEXT,
    category TEXT,  -- 'standing', 'balancing', 'restorative', etc.
    video_url TEXT,
    thumbnail_url TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Index for faster queries
CREATE INDEX IF NOT EXISTS idx_yoga_poses_dosha ON yoga_poses USING GIN (dosha_tags);
CREATE INDEX IF NOT EXISTS idx_yoga_poses_emotion ON yoga_poses USING GIN (emotion_tags);
CREATE INDEX IF NOT EXISTS idx_yoga_poses_difficulty ON yoga_poses (difficulty);

-- ============================================
-- SOUND THERAPY TRACKS TABLE
-- ============================================
CREATE TABLE IF NOT EXISTS sound_tracks (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    title TEXT NOT NULL,
    duration_minutes INTEGER NOT NULL,
    dosha_tags TEXT[] NOT NULL,  -- ['vata', 'pitta', 'kapha']
    emotion_tags TEXT[] NOT NULL,  -- ['anxious', 'calm', 'energized', etc.]
    frequency_hz INTEGER,  -- Healing frequency (e.g., 432, 528)
    description TEXT,
    mood_category TEXT,  -- 'calming', 'energizing', 'meditative', etc.
    icon TEXT,
    audio_url TEXT,
    thumbnail_gradient TEXT,  -- Tailwind gradient classes
    play_count INTEGER DEFAULT 0,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Index for faster queries
CREATE INDEX IF NOT EXISTS idx_sound_tracks_dosha ON sound_tracks USING GIN (dosha_tags);
CREATE INDEX IF NOT EXISTS idx_sound_tracks_emotion ON sound_tracks USING GIN (emotion_tags);
CREATE INDEX IF NOT EXISTS idx_sound_tracks_mood ON sound_tracks (mood_category);

-- ============================================
-- USER YOGA PRACTICE LOG (Optional - for future)
-- ============================================
CREATE TABLE IF NOT EXISTS yoga_practice_logs (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    user_id UUID REFERENCES profiles(id) ON DELETE CASCADE,
    pose_id UUID REFERENCES yoga_poses(id) ON DELETE SET NULL,
    duration_seconds INTEGER,
    feedback_quality INTEGER CHECK (feedback_quality BETWEEN 1 AND 5),
    notes TEXT,
    practiced_at TIMESTAMPTZ DEFAULT NOW(),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_yoga_logs_user ON yoga_practice_logs (user_id);
CREATE INDEX IF NOT EXISTS idx_yoga_logs_date ON yoga_practice_logs (practiced_at);

-- ============================================
-- USER SOUND THERAPY LOG (Optional - for future)
-- ============================================
CREATE TABLE IF NOT EXISTS sound_therapy_logs (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    user_id UUID REFERENCES profiles(id) ON DELETE CASCADE,
    track_id UUID REFERENCES sound_tracks(id) ON DELETE SET NULL,
    duration_listened INTEGER,  -- seconds
    completed BOOLEAN DEFAULT false,
    mood_before TEXT,
    mood_after TEXT,
    listened_at TIMESTAMPTZ DEFAULT NOW(),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_sound_logs_user ON sound_therapy_logs (user_id);
CREATE INDEX IF NOT EXISTS idx_sound_logs_date ON sound_therapy_logs (listened_at);

-- ============================================
-- ROW LEVEL SECURITY
-- ============================================

-- Yoga poses and sound tracks are public (everyone can read)
ALTER TABLE yoga_poses ENABLE ROW LEVEL SECURITY;
ALTER TABLE sound_tracks ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Anyone can view yoga poses" ON yoga_poses
    FOR SELECT USING (true);

CREATE POLICY "Anyone can view sound tracks" ON sound_tracks
    FOR SELECT USING (true);

-- Practice logs are private (users can only see their own)
ALTER TABLE yoga_practice_logs ENABLE ROW LEVEL SECURITY;
ALTER TABLE sound_therapy_logs ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can view own practice logs" ON yoga_practice_logs
    FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Users can insert own practice logs" ON yoga_practice_logs
    FOR INSERT WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can view own sound logs" ON sound_therapy_logs
    FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Users can insert own sound logs" ON sound_therapy_logs
    FOR INSERT WITH CHECK (auth.uid() = user_id);

-- ============================================
-- COMMENTS
-- ============================================

COMMENT ON TABLE yoga_poses IS 'Ayurvedic yoga poses personalized by dosha and emotion';
COMMENT ON TABLE sound_tracks IS 'Sound therapy tracks with healing frequencies';
COMMENT ON TABLE yoga_practice_logs IS 'User practice history for analytics';
COMMENT ON TABLE sound_therapy_logs IS 'User listening history for analytics';
