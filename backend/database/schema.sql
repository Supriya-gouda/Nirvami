"""Database schema for Nirvami application."""

-- Enable required extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgvector";

-- ============================================
-- 1. USER MANAGEMENT & PROFILES
-- ============================================

CREATE TABLE IF NOT EXISTS profiles (
    id UUID PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,
    email TEXT NOT NULL,
    full_name TEXT,
    avatar_url TEXT,
    phone_number TEXT,  -- For SMS notifications
    dosha_type TEXT CHECK (dosha_type IN ('vata', 'pitta', 'kapha', 'vata-pitta', 'pitta-kapha', 'vata-kapha', 'tridosha')),
    role TEXT DEFAULT 'user' CHECK (role IN ('user', 'admin')),
    consent_data_collection BOOLEAN DEFAULT false,
    consent_ai_processing BOOLEAN DEFAULT false,
    consent_notifications BOOLEAN DEFAULT true,
    timezone TEXT DEFAULT 'UTC',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- User preferences
CREATE TABLE IF NOT EXISTS user_preferences (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    user_id UUID REFERENCES profiles(id) ON DELETE CASCADE,
    notification_email BOOLEAN DEFAULT true,
    notification_sms BOOLEAN DEFAULT false,
    notification_push BOOLEAN DEFAULT true,
    crisis_alerts_enabled BOOLEAN DEFAULT true,
    data_retention_days INTEGER DEFAULT 365,
    preferences JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(user_id)
);

-- ============================================
-- 2. CONVERSATIONAL AI ASSISTANT
-- ============================================

CREATE TABLE IF NOT EXISTS chat_sessions (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    user_id UUID REFERENCES profiles(id) ON DELETE CASCADE,
    title TEXT,
    started_at TIMESTAMPTZ DEFAULT NOW(),
    last_message_at TIMESTAMPTZ DEFAULT NOW(),
    metadata JSONB DEFAULT '{}'
);

CREATE TABLE IF NOT EXISTS messages (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    session_id UUID REFERENCES chat_sessions(id) ON DELETE CASCADE,
    user_id UUID REFERENCES profiles(id) ON DELETE CASCADE,
    role TEXT NOT NULL CHECK (role IN ('user', 'assistant', 'system')),
    content TEXT NOT NULL,
    embedding vector(384), -- for all-MiniLM-L6-v2
    emotion_detected TEXT,
    emotion_scores JSONB,
    crisis_flag BOOLEAN DEFAULT false,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_messages_session ON messages(session_id);
CREATE INDEX idx_messages_user ON messages(user_id);
CREATE INDEX idx_messages_embedding ON messages USING ivfflat (embedding vector_cosine_ops);

-- ============================================
-- 3. EMOTION DETECTION & LOGS
-- ============================================

CREATE TABLE IF NOT EXISTS emotion_logs (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    user_id UUID REFERENCES profiles(id) ON DELETE CASCADE,
    message_id UUID REFERENCES messages(id) ON DELETE SET NULL,
    emotion_type TEXT NOT NULL,
    confidence FLOAT NOT NULL,
    all_scores JSONB NOT NULL,
    source TEXT DEFAULT 'text' CHECK (source IN ('text', 'voice', 'manual')),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_emotion_logs_user_date ON emotion_logs(user_id, created_at DESC);

-- Daily emotion aggregates
CREATE TABLE IF NOT EXISTS emotion_aggregates (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    user_id UUID REFERENCES profiles(id) ON DELETE CASCADE,
    date DATE NOT NULL,
    dominant_emotion TEXT,
    emotion_distribution JSONB NOT NULL, -- { "joy": 0.3, "sadness": 0.2, ... }
    average_valence FLOAT, -- -1 to 1 scale
    total_entries INTEGER DEFAULT 0,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(user_id, date)
);

-- ============================================
-- 4. AURA VISUALIZATION SYSTEM
-- ============================================

CREATE TABLE IF NOT EXISTS aura_entries (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    user_id UUID REFERENCES profiles(id) ON DELETE CASCADE,
    date DATE NOT NULL,
    color_code TEXT NOT NULL, -- hex color
    intensity FLOAT NOT NULL CHECK (intensity >= 0 AND intensity <= 100),
    glow_level FLOAT CHECK (glow_level >= 0 AND glow_level <= 100),
    aura_type TEXT, -- e.g., 'calm', 'energetic', 'turbulent'
    emotion_basis JSONB, -- emotion distribution used to compute aura
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(user_id, date)
);

-- ============================================
-- 5. WELLNESS SCORING & ENGAGEMENT
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

CREATE INDEX idx_journal_user_date ON journal_entries(user_id, date DESC);

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

CREATE INDEX idx_goals_user_status ON goals(user_id, status, target_date);

-- Wellness scores
CREATE TABLE IF NOT EXISTS wellness_scores (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    user_id UUID REFERENCES profiles(id) ON DELETE CASCADE,
    date DATE NOT NULL,
    overall_score FLOAT NOT NULL CHECK (overall_score >= 0 AND overall_score <= 100),
    emotion_score FLOAT,
    wearable_score FLOAT,
    engagement_score FLOAT,
    score_components JSONB NOT NULL,
    insights TEXT[],
    recommendations TEXT[],
    created_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(user_id, date)
);

-- ============================================
-- 6. DOSHA & AYURVEDIC INTELLIGENCE
-- ============================================

CREATE TABLE IF NOT EXISTS dosha_assessments (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    user_id UUID REFERENCES profiles(id) ON DELETE CASCADE,
    assessment_date TIMESTAMPTZ DEFAULT NOW(),
    quiz_responses JSONB NOT NULL,
    vata_score FLOAT NOT NULL,
    pitta_score FLOAT NOT NULL,
    kapha_score FLOAT NOT NULL,
    primary_dosha TEXT,
    secondary_dosha TEXT,
    assessment_type TEXT DEFAULT 'full' CHECK (assessment_type IN ('full', 'quick', 'periodic')),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS ayurveda_resources (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    title TEXT NOT NULL,
    content TEXT NOT NULL,
    category TEXT CHECK (category IN ('diet', 'yoga', 'meditation', 'lifestyle', 'remedies')),
    dosha_tags TEXT[], -- ['vata', 'pitta', 'kapha']
    keywords TEXT[],
    embedding vector(384),
    created_by UUID REFERENCES profiles(id),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_ayurveda_embedding ON ayurveda_resources USING ivfflat (embedding vector_cosine_ops);

-- ============================================
-- 7. MEAL TRACKING & CORRELATION
-- ============================================

CREATE TABLE IF NOT EXISTS meals (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    user_id UUID REFERENCES profiles(id) ON DELETE CASCADE,
    meal_time TIMESTAMPTZ NOT NULL,
    meal_type TEXT CHECK (meal_type IN ('breakfast', 'lunch', 'dinner', 'snack')),
    meal_text TEXT NOT NULL,
    ingredients TEXT[],
    dosha_impact_tags JSONB, -- { "vata": "balancing", "pitta": "aggravating", ... }
    calories INTEGER,
    embedding vector(384),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_meals_user_time ON meals(user_id, meal_time DESC);

CREATE TABLE IF NOT EXISTS meal_emotion_correlations (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    user_id UUID REFERENCES profiles(id) ON DELETE CASCADE,
    meal_id UUID REFERENCES meals(id) ON DELETE CASCADE,
    emotion_log_id UUID REFERENCES emotion_logs(id) ON DELETE CASCADE,
    correlation_score FLOAT NOT NULL, -- semantic similarity or temporal correlation
    time_delta_hours FLOAT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- ============================================
-- 8. WEARABLE DEVICE INTEGRATION
-- ============================================

-- Raw data from watch OR manual entry
CREATE TABLE IF NOT EXISTS wearable_snapshots (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    user_id UUID REFERENCES profiles(id) ON DELETE CASCADE,
    source VARCHAR(20) NOT NULL DEFAULT 'manual',        -- 'watch' or 'manual'
    provider VARCHAR(50),                                -- 'apple_watch', 'fitbit', 'manual_form'
    captured_at TIMESTAMPTZ NOT NULL,                    -- exact time of reading (use recorded_at as alias in queries)
    
    heart_rate INTEGER,                                  -- bpm
    hrv_ms INTEGER,                                      -- heart rate variability in ms
    steps INTEGER,
    sleep_hours NUMERIC(4,2),
    stress_level INTEGER,                                -- 1-10 scale
    calories_burned NUMERIC(6,2),
    
    -- Legacy fields for backward compatibility
    eda FLOAT,                                           -- Electrodermal Activity
    sleep_quality TEXT CHECK (sleep_quality IN ('poor', 'fair', 'good', 'excellent')),
    active_calories INTEGER,
    
    raw_payload JSONB,                                   -- optional, original data from device
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Support legacy recorded_at queries
CREATE INDEX idx_wearable_user_time ON wearable_snapshots(user_id, captured_at DESC);
CREATE INDEX idx_wearable_source ON wearable_snapshots(user_id, source);

-- Aggregated daily stats per user
CREATE TABLE IF NOT EXISTS wearable_daily_stats (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    user_id UUID REFERENCES profiles(id) ON DELETE CASCADE,
    date DATE NOT NULL,
    
    avg_heart_rate NUMERIC(5,2),
    min_heart_rate INTEGER,
    max_heart_rate INTEGER,
    avg_hrv_ms NUMERIC(6,2),
    total_steps INTEGER,
    sleep_hours NUMERIC(4,2),
    avg_stress_level NUMERIC(4,2),
    
    data_source VARCHAR(20),                             -- 'watch', 'manual', 'mixed'
    insights TEXT[],                                     -- computed insights
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(user_id, date)
);

-- ============================================
-- 8.5. DAILY ROUTINES (Dinacharya)
-- ============================================

-- User's daily routine activities (allows multiple entries per day)
CREATE TABLE IF NOT EXISTS daily_routines (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    user_id UUID REFERENCES profiles(id) ON DELETE CASCADE,
    date DATE NOT NULL,
    time TIME NOT NULL,
    activity TEXT NOT NULL,
    notes TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_daily_routines_user_date ON daily_routines(user_id, date DESC);
CREATE INDEX idx_daily_routines_user_time ON daily_routines(user_id, date DESC, time);

-- ============================================
-- 9. ALERTS & NOTIFICATIONS
-- ============================================

CREATE TABLE IF NOT EXISTS alerts (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    user_id UUID REFERENCES profiles(id) ON DELETE CASCADE,
    alert_type TEXT NOT NULL CHECK (alert_type IN ('crisis', 'wellness_low', 'reminder', 'achievement')),
    severity TEXT CHECK (severity IN ('low', 'medium', 'high', 'critical')),
    title TEXT NOT NULL,
    message TEXT NOT NULL,
    triggered_by TEXT, -- e.g., 'message_id', 'wellness_score', 'wearable'
    trigger_metadata JSONB,
    status TEXT DEFAULT 'active' CHECK (status IN ('active', 'acknowledged', 'resolved')),
    notified_channels TEXT[], -- ['email', 'sms', 'in_app']
    created_at TIMESTAMPTZ DEFAULT NOW(),
    acknowledged_at TIMESTAMPTZ
);

CREATE INDEX idx_alerts_user_status ON alerts(user_id, status, created_at DESC);

CREATE TABLE IF NOT EXISTS notifications (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    user_id UUID REFERENCES profiles(id) ON DELETE CASCADE,
    title TEXT NOT NULL,
    body TEXT NOT NULL,
    type TEXT CHECK (type IN ('info', 'success', 'warning', 'error')),
    read BOOLEAN DEFAULT false,
    action_url TEXT,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_notifications_user_read ON notifications(user_id, read, created_at DESC);

-- ============================================
-- 10. BACKGROUND JOBS & SCHEDULER
-- ============================================

CREATE TABLE IF NOT EXISTS job_logs (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    job_name TEXT NOT NULL,
    job_type TEXT CHECK (job_type IN ('wellness_score', 'emotion_aggregate', 'meal_correlation', 'embedding_index', 'wearable_sync')),
    status TEXT CHECK (status IN ('pending', 'running', 'completed', 'failed')),
    started_at TIMESTAMPTZ,
    completed_at TIMESTAMPTZ,
    error_message TEXT,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- ============================================
-- 11. ADMIN & AUDIT
-- ============================================

CREATE TABLE IF NOT EXISTS audit_logs (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    user_id UUID REFERENCES profiles(id) ON DELETE SET NULL,
    admin_id UUID REFERENCES profiles(id),
    action TEXT NOT NULL,
    entity_type TEXT,
    entity_id UUID,
    old_values JSONB,
    new_values JSONB,
    ip_address TEXT,
    user_agent TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_audit_logs_user ON audit_logs(user_id, created_at DESC);
CREATE INDEX idx_audit_logs_admin ON audit_logs(admin_id, created_at DESC);

-- ============================================
-- ROW LEVEL SECURITY (RLS) POLICIES
-- ============================================

-- Enable RLS on all user-facing tables
ALTER TABLE profiles ENABLE ROW LEVEL SECURITY;
ALTER TABLE user_preferences ENABLE ROW LEVEL SECURITY;
ALTER TABLE chat_sessions ENABLE ROW LEVEL SECURITY;
ALTER TABLE messages ENABLE ROW LEVEL SECURITY;
ALTER TABLE emotion_logs ENABLE ROW LEVEL SECURITY;
ALTER TABLE emotion_aggregates ENABLE ROW LEVEL SECURITY;
ALTER TABLE aura_entries ENABLE ROW LEVEL SECURITY;
ALTER TABLE journal_entries ENABLE ROW LEVEL SECURITY;
ALTER TABLE goals ENABLE ROW LEVEL SECURITY;
ALTER TABLE wellness_scores ENABLE ROW LEVEL SECURITY;
ALTER TABLE dosha_assessments ENABLE ROW LEVEL SECURITY;
ALTER TABLE meals ENABLE ROW LEVEL SECURITY;
ALTER TABLE meal_emotion_correlations ENABLE ROW LEVEL SECURITY;
ALTER TABLE wearable_snapshots ENABLE ROW LEVEL SECURITY;
ALTER TABLE wearable_daily_stats ENABLE ROW LEVEL SECURITY;
ALTER TABLE daily_routines ENABLE ROW LEVEL SECURITY;
ALTER TABLE alerts ENABLE ROW LEVEL SECURITY;
ALTER TABLE notifications ENABLE ROW LEVEL SECURITY;

-- Profiles: Users can view and update their own profile
CREATE POLICY "Users can view own profile" ON profiles
    FOR SELECT USING (auth.uid() = id);

CREATE POLICY "Users can update own profile" ON profiles
    FOR UPDATE USING (auth.uid() = id);

-- Generic user data policies (apply to most tables)
CREATE POLICY "Users can view own data" ON user_preferences
    FOR ALL USING (auth.uid() = user_id);

CREATE POLICY "Users can view own sessions" ON chat_sessions
    FOR ALL USING (auth.uid() = user_id);

CREATE POLICY "Users can view own messages" ON messages
    FOR ALL USING (auth.uid() = user_id);

CREATE POLICY "Users can view own emotions" ON emotion_logs
    FOR ALL USING (auth.uid() = user_id);

CREATE POLICY "Users can view own aggregates" ON emotion_aggregates
    FOR ALL USING (auth.uid() = user_id);

CREATE POLICY "Users can view own aura" ON aura_entries
    FOR ALL USING (auth.uid() = user_id);

CREATE POLICY "Users can manage own journals" ON journal_entries
    FOR ALL USING (auth.uid() = user_id);

CREATE POLICY "Users can manage own goals" ON goals
    FOR ALL USING (auth.uid() = user_id);

CREATE POLICY "Users can view own scores" ON wellness_scores
    FOR ALL USING (auth.uid() = user_id);

CREATE POLICY "Users can view own assessments" ON dosha_assessments
    FOR ALL USING (auth.uid() = user_id);

CREATE POLICY "Users can view own meals" ON meals
    FOR ALL USING (auth.uid() = user_id);

CREATE POLICY "Users can view own correlations" ON meal_emotion_correlations
    FOR ALL USING (auth.uid() = user_id);

CREATE POLICY "Users can view own wearable data" ON wearable_snapshots
    FOR ALL USING (auth.uid() = user_id);

CREATE POLICY "Users can view own wearable stats" ON wearable_daily_stats
    FOR ALL USING (auth.uid() = user_id);

CREATE POLICY "Users can manage own routines" ON daily_routines
    FOR ALL USING (auth.uid() = user_id);

CREATE POLICY "Users can view own alerts" ON alerts
    FOR ALL USING (auth.uid() = user_id);

CREATE POLICY "Users can view own notifications" ON notifications
    FOR ALL USING (auth.uid() = user_id);

-- Ayurveda resources: Public read access
CREATE POLICY "Anyone can view resources" ON ayurveda_resources
    FOR SELECT USING (true);

CREATE POLICY "Admins can manage resources" ON ayurveda_resources
    FOR ALL USING (
        EXISTS (
            SELECT 1 FROM profiles WHERE id = auth.uid() AND role = 'admin'
        )
    );

-- Admin access to audit logs
CREATE POLICY "Admins can view audit logs" ON audit_logs
    FOR SELECT USING (
        EXISTS (
            SELECT 1 FROM profiles WHERE id = auth.uid() AND role = 'admin'
        )
    );

-- ============================================
-- FUNCTIONS & TRIGGERS
-- ============================================

-- Update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER update_profiles_updated_at BEFORE UPDATE ON profiles
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_user_preferences_updated_at BEFORE UPDATE ON user_preferences
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_ayurveda_resources_updated_at BEFORE UPDATE ON ayurveda_resources
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Create default preferences on profile creation
CREATE OR REPLACE FUNCTION create_default_preferences()
RETURNS TRIGGER AS $$
BEGIN
    INSERT INTO user_preferences (user_id)
    VALUES (NEW.id)
    ON CONFLICT (user_id) DO NOTHING;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER create_user_preferences_on_signup
    AFTER INSERT ON profiles
    FOR EACH ROW
    EXECUTE FUNCTION create_default_preferences();
