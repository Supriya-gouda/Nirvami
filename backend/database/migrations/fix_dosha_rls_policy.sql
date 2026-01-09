-- Fix RLS policy for dosha_assessments to allow INSERT
-- Drop the existing overly permissive policy
DROP POLICY IF EXISTS "Users can view own assessments" ON dosha_assessments;

-- Create separate policies for different operations
CREATE POLICY "Users can insert own assessments" ON dosha_assessments
    FOR INSERT 
    WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can view own assessments" ON dosha_assessments
    FOR SELECT 
    USING (auth.uid() = user_id);

CREATE POLICY "Users can update own assessments" ON dosha_assessments
    FOR UPDATE 
    USING (auth.uid() = user_id)
    WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can delete own assessments" ON dosha_assessments
    FOR DELETE 
    USING (auth.uid() = user_id);
