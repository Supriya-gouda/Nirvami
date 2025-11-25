-- ============================================
-- WEARABLE HEALTH ALERTS - PHONE NUMBER MIGRATION
-- ============================================
-- Add phone_number field to profiles table for SMS notifications

-- Add phone_number column to profiles table
ALTER TABLE profiles ADD COLUMN IF NOT EXISTS phone_number TEXT;

-- Verify column was added
SELECT column_name, data_type, is_nullable 
FROM information_schema.columns 
WHERE table_name = 'profiles' AND column_name = 'phone_number';
