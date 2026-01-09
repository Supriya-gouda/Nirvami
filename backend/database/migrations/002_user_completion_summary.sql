-- User Completion Summary Schema for Practice System
-- Tracks daily completions, streaks, and lifetime statistics

CREATE TABLE IF NOT EXISTS user_completion_summary (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    user_id UUID NOT NULL REFERENCES profiles(id) ON DELETE CASCADE UNIQUE,
    daily_completed_count INTEGER DEFAULT 0,
    last_completion_date DATE,
    current_streak INTEGER DEFAULT 0,
    longest_streak INTEGER DEFAULT 0,
    lifetime_total_completed INTEGER DEFAULT 0,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_user_completion_summary_user_id ON user_completion_summary(user_id);

-- Enable RLS
ALTER TABLE user_completion_summary ENABLE ROW LEVEL SECURITY;

-- Users can view and update their own completion summary
CREATE POLICY "Users can view own completion summary" ON user_completion_summary
    FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Users can insert own completion summary" ON user_completion_summary
    FOR INSERT WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update own completion summary" ON user_completion_summary
    FOR UPDATE USING (auth.uid() = user_id);

-- Trigger to update completion summary on practice completion
CREATE OR REPLACE FUNCTION update_completion_summary()
RETURNS TRIGGER AS $$
DECLARE
    today DATE := CURRENT_DATE;
    yesterday DATE := CURRENT_DATE - INTERVAL '1 day';
    summary_record RECORD;
BEGIN
    -- Get or create summary record
    SELECT * INTO summary_record 
    FROM user_completion_summary 
    WHERE user_id = NEW.user_id 
    FOR UPDATE;
    
    IF NOT FOUND THEN
        -- Create new summary record
        INSERT INTO user_completion_summary (
            user_id, 
            daily_completed_count, 
            last_completion_date, 
            current_streak, 
            longest_streak, 
            lifetime_total_completed
        ) VALUES (
            NEW.user_id, 
            1, 
            today, 
            1, 
            1, 
            1
        );
    ELSE
        -- Update existing summary
        IF summary_record.last_completion_date = today THEN
            -- Same day - just increment daily count
            UPDATE user_completion_summary 
            SET 
                daily_completed_count = summary_record.daily_completed_count + 1,
                lifetime_total_completed = summary_record.lifetime_total_completed + 1,
                updated_at = NOW()
            WHERE user_id = NEW.user_id;
        ELSIF summary_record.last_completion_date = yesterday THEN
            -- Consecutive day - increment streak and reset daily count
            UPDATE user_completion_summary 
            SET 
                daily_completed_count = 1,
                last_completion_date = today,
                current_streak = summary_record.current_streak + 1,
                longest_streak = GREATEST(summary_record.longest_streak, summary_record.current_streak + 1),
                lifetime_total_completed = summary_record.lifetime_total_completed + 1,
                updated_at = NOW()
            WHERE user_id = NEW.user_id;
        ELSE
            -- Streak broken - reset to 1
            UPDATE user_completion_summary 
            SET 
                daily_completed_count = 1,
                last_completion_date = today,
                current_streak = 1,
                longest_streak = GREATEST(summary_record.longest_streak, 1),
                lifetime_total_completed = summary_record.lifetime_total_completed + 1,
                updated_at = NOW()
            WHERE user_id = NEW.user_id;
        END IF;
    END IF;
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Attach trigger to practice_sessions
DROP TRIGGER IF EXISTS trigger_update_completion_summary ON practice_sessions;
CREATE TRIGGER trigger_update_completion_summary
    AFTER INSERT ON practice_sessions
    FOR EACH ROW
    WHEN (NEW.completion_status = 'completed')
    EXECUTE FUNCTION update_completion_summary();

COMMENT ON TABLE user_completion_summary IS 'Tracks daily practice completions, streaks, and lifetime statistics';
