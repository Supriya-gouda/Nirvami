-- ============================================
-- RLS Policy Fix for dosha_assessments Table
-- ============================================
-- This fixes the "new row violates row-level security policy" error
-- by adding explicit INSERT, UPDATE, DELETE policies

-- Drop all existing policies if they exist
DROP POLICY IF EXISTS "Users can insert own assessments" ON public.dosha_assessments;
DROP POLICY IF EXISTS "Users can view own assessments" ON public.dosha_assessments;
DROP POLICY IF EXISTS "Users can update own assessments" ON public.dosha_assessments;
DROP POLICY IF EXISTS "Users can delete own assessments" ON public.dosha_assessments;

-- Create separate policies for each operation
-- 1. Allow users to INSERT their own assessments
CREATE POLICY "Users can insert own assessments" 
ON public.dosha_assessments
FOR INSERT 
TO authenticated
WITH CHECK (auth.uid() = user_id);

-- 2. Allow users to SELECT/VIEW their own assessments
CREATE POLICY "Users can view own assessments" 
ON public.dosha_assessments
FOR SELECT 
TO authenticated
USING (auth.uid() = user_id);

-- 3. Allow users to UPDATE their own assessments
CREATE POLICY "Users can update own assessments" 
ON public.dosha_assessments
FOR UPDATE 
TO authenticated
USING (auth.uid() = user_id)
WITH CHECK (auth.uid() = user_id);

-- 4. Allow users to DELETE their own assessments
CREATE POLICY "Users can delete own assessments" 
ON public.dosha_assessments
FOR DELETE 
TO authenticated
USING (auth.uid() = user_id);

-- Verify the policies were created
SELECT 
    schemaname,
    tablename,
    policyname,
    permissive,
    roles,
    cmd,
    qual,
    with_check
FROM pg_policies 
WHERE tablename = 'dosha_assessments'
ORDER BY policyname;
