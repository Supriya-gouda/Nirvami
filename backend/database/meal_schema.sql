-- Meals table for storing user meal logs
CREATE TABLE IF NOT EXISTS public.meals (
  id UUID NOT NULL DEFAULT gen_random_uuid(),
  user_id UUID NULL,
  meal_time TIMESTAMP WITH TIME ZONE NOT NULL,
  meal_type TEXT NULL,
  meal_text TEXT NOT NULL,
  ingredients TEXT[] NULL,
  dosha_impact_tags JSONB NULL,
  calories INTEGER NULL,
  embedding DOUBLE PRECISION[] NULL,
  created_at TIMESTAMP WITH TIME ZONE NULL DEFAULT NOW(),
  CONSTRAINT meals_pkey PRIMARY KEY (id),
  CONSTRAINT meals_user_id_fkey FOREIGN KEY (user_id) REFERENCES profiles (id) ON DELETE CASCADE,
  CONSTRAINT meal_embed_len CHECK (
    (embedding IS NULL) OR (array_length(embedding, 1) = 384)
  ),
  CONSTRAINT meals_meal_type_check CHECK (
    meal_type = ANY(ARRAY['breakfast','lunch','dinner','snack'])
  )
);

-- Index for efficient queries by user and time
CREATE INDEX IF NOT EXISTS idx_meals_user_time
ON public.meals (user_id, meal_time DESC);

-- Meal-emotion correlations table
CREATE TABLE IF NOT EXISTS public.meal_emotion_correlations (
  id UUID NOT NULL DEFAULT gen_random_uuid(),
  user_id UUID NULL,
  meal_id UUID NULL,
  emotion_log_id UUID NULL,
  emotion_type TEXT NULL,
  emotion_intensity DOUBLE PRECISION NULL,
  meal_type TEXT NULL,
  ingredients JSONB NULL,
  dosha_impact JSONB NULL,
  correlation_score DOUBLE PRECISION NOT NULL,
  time_delta_hours DOUBLE PRECISION NULL,
  created_at TIMESTAMP WITH TIME ZONE NULL DEFAULT NOW(),
  CONSTRAINT meal_emotion_correlations_pkey PRIMARY KEY (id),
  CONSTRAINT meal_emotion_correlations_emotion_log_id_fkey FOREIGN KEY (emotion_log_id) REFERENCES emotion_logs (id) ON DELETE CASCADE,
  CONSTRAINT meal_emotion_correlations_meal_id_fkey FOREIGN KEY (meal_id) REFERENCES meals (id) ON DELETE CASCADE,
  CONSTRAINT meal_emotion_correlations_user_id_fkey FOREIGN KEY (user_id) REFERENCES profiles (id) ON DELETE CASCADE
);

-- Meal-based Ayurvedic guidelines table (separate from main recommendations)
CREATE TABLE IF NOT EXISTS public.meal_ayurveda_guidelines (
  id UUID NOT NULL DEFAULT gen_random_uuid(),
  user_id UUID NULL,
  date DATE NOT NULL,
  meal_id UUID NULL,
  guideline_type TEXT NOT NULL, -- 'avoid', 'favor', 'balance'
  content TEXT NOT NULL,
  dosha_type TEXT NULL, -- 'vata', 'pitta', 'kapha'
  confidence_score DOUBLE PRECISION DEFAULT 0.8,
  created_at TIMESTAMP WITH TIME ZONE NULL DEFAULT NOW(),
  CONSTRAINT meal_ayurveda_guidelines_pkey PRIMARY KEY (id),
  CONSTRAINT meal_ayurveda_guidelines_user_id_fkey FOREIGN KEY (user_id) REFERENCES profiles (id) ON DELETE CASCADE,
  CONSTRAINT meal_ayurveda_guidelines_meal_id_fkey FOREIGN KEY (meal_id) REFERENCES meals (id) ON DELETE CASCADE,
  CONSTRAINT guideline_type_check CHECK (
    guideline_type = ANY(ARRAY['avoid', 'favor', 'balance', 'health', 'dosha', 'mood', 'general'])
  )
);

-- Index for efficient daily guidelines retrieval
CREATE INDEX IF NOT EXISTS idx_meal_guidelines_user_date
ON public.meal_ayurveda_guidelines (user_id, date DESC);

-- Ayurvedic recipe suggestions table
CREATE TABLE IF NOT EXISTS public.meal_recipe_suggestions (
  id UUID NOT NULL DEFAULT gen_random_uuid(),
  user_id UUID NULL,
  date DATE NOT NULL,
  recipe_name TEXT NOT NULL,
  recipe_description TEXT NOT NULL,
  prep_time_minutes INTEGER NULL,
  ingredients TEXT[] NOT NULL,
  dosha_balance_tags JSONB NULL,
  benefits TEXT[] NULL,
  created_at TIMESTAMP WITH TIME ZONE NULL DEFAULT NOW(),
  CONSTRAINT meal_recipe_suggestions_pkey PRIMARY KEY (id),
  CONSTRAINT meal_recipe_suggestions_user_id_fkey FOREIGN KEY (user_id) REFERENCES profiles (id) ON DELETE CASCADE
);

-- Index for efficient daily recipe suggestions
CREATE INDEX IF NOT EXISTS idx_recipe_suggestions_user_date
ON public.meal_recipe_suggestions (user_id, date DESC);

-- Enable Row Level Security (RLS) for all meal tables
ALTER TABLE public.meals ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.meal_emotion_correlations ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.meal_ayurveda_guidelines ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.meal_recipe_suggestions ENABLE ROW LEVEL SECURITY;

-- Create RLS policies for meals table
CREATE POLICY "Users can view own meals" ON public.meals
  FOR SELECT USING (auth.uid() = user_id OR user_id = '00000000-0000-0000-0000-000000000000'::uuid);

CREATE POLICY "Users can insert own meals" ON public.meals
  FOR INSERT WITH CHECK (auth.uid() = user_id OR user_id = '00000000-0000-0000-0000-000000000000'::uuid);

CREATE POLICY "Users can update own meals" ON public.meals
  FOR UPDATE USING (auth.uid() = user_id OR user_id = '00000000-0000-0000-0000-000000000000'::uuid);

CREATE POLICY "Users can delete own meals" ON public.meals
  FOR DELETE USING (auth.uid() = user_id OR user_id = '00000000-0000-0000-0000-000000000000'::uuid);

-- Create RLS policies for meal_emotion_correlations table
CREATE POLICY "Users can view own meal correlations" ON public.meal_emotion_correlations
  FOR SELECT USING (auth.uid() = user_id OR user_id = '00000000-0000-0000-0000-000000000000'::uuid);

CREATE POLICY "Users can insert own meal correlations" ON public.meal_emotion_correlations
  FOR INSERT WITH CHECK (auth.uid() = user_id OR user_id = '00000000-0000-0000-0000-000000000000'::uuid);

CREATE POLICY "Users can update own meal correlations" ON public.meal_emotion_correlations
  FOR UPDATE USING (auth.uid() = user_id OR user_id = '00000000-0000-0000-0000-000000000000'::uuid);

CREATE POLICY "Users can delete own meal correlations" ON public.meal_emotion_correlations
  FOR DELETE USING (auth.uid() = user_id OR user_id = '00000000-0000-0000-0000-000000000000'::uuid);

-- Create RLS policies for meal_ayurveda_guidelines table
CREATE POLICY "Users can view own meal guidelines" ON public.meal_ayurveda_guidelines
  FOR SELECT USING (auth.uid() = user_id OR user_id = '00000000-0000-0000-0000-000000000000'::uuid);

CREATE POLICY "Users can insert own meal guidelines" ON public.meal_ayurveda_guidelines
  FOR INSERT WITH CHECK (auth.uid() = user_id OR user_id = '00000000-0000-0000-0000-000000000000'::uuid);

CREATE POLICY "Users can update own meal guidelines" ON public.meal_ayurveda_guidelines
  FOR UPDATE USING (auth.uid() = user_id OR user_id = '00000000-0000-0000-0000-000000000000'::uuid);

CREATE POLICY "Users can delete own meal guidelines" ON public.meal_ayurveda_guidelines
  FOR DELETE USING (auth.uid() = user_id OR user_id = '00000000-0000-0000-0000-000000000000'::uuid);

-- Create RLS policies for meal_recipe_suggestions table
CREATE POLICY "Users can view own meal recipes" ON public.meal_recipe_suggestions
  FOR SELECT USING (auth.uid() = user_id OR user_id = '00000000-0000-0000-0000-000000000000'::uuid);

CREATE POLICY "Users can insert own meal recipes" ON public.meal_recipe_suggestions
  FOR INSERT WITH CHECK (auth.uid() = user_id OR user_id = '00000000-0000-0000-0000-000000000000'::uuid);

CREATE POLICY "Users can update own meal recipes" ON public.meal_recipe_suggestions
  FOR UPDATE USING (auth.uid() = user_id OR user_id = '00000000-0000-0000-0000-000000000000'::uuid);

CREATE POLICY "Users can delete own meal recipes" ON public.meal_recipe_suggestions
  FOR DELETE USING (auth.uid() = user_id OR user_id = '00000000-0000-0000-0000-000000000000'::uuid);