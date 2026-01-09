-- Migration: Create dosha_assessments table
CREATE TABLE IF NOT EXISTS dosha_assessments (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL,
    vata_score NUMERIC(5,2) NOT NULL,
    pitta_score NUMERIC(5,2) NOT NULL,
    kapha_score NUMERIC(5,2) NOT NULL,
    primary_dosha TEXT NOT NULL,
    secondary_dosha TEXT,
    assessed_on TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    CONSTRAINT dosha_assessments_user_fk FOREIGN KEY (user_id) REFERENCES auth.users (id) ON DELETE CASCADE
);

-- Ensure only one active record per user by using upsert semantics in code.
CREATE INDEX IF NOT EXISTS idx_dosha_assessments_user_id ON dosha_assessments(user_id);
