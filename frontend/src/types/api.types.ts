// API Response Types
export interface ApiResponse<T = any> {
  data?: T;
  error?: string;
  message?: string;
}

// Auth Types
export interface User {
  id: string;
  email: string;
  name?: string; // From AuthContext
  full_name?: string; // From backend profile
  age?: number;
  gender?: string;
  created_at: string;
}

export interface LoginRequest {
  email: string;
  password: string;
}

export interface RegisterRequest {
  email: string;
  password: string;
  full_name?: string;
  age?: number;
  gender?: string;
}

export interface AuthResponse {
  access_token: string;
  token_type: string;
  user: User;
}

// Profile Types
export interface Profile {
  user_id: string;
  full_name?: string;
  age?: number;
  gender?: string;
  height_cm?: number;
  weight_kg?: number;
  location?: string;
  timezone?: string;
  preferences?: {
    notifications: boolean;
    dark_mode: boolean;
    language: string;
  };
  emergency_contact?: {
    name: string;
    phone: string;
    relationship: string;
  };
  created_at: string;
  updated_at: string;
}

export interface UpdateProfileRequest {
  full_name?: string;
  age?: number;
  gender?: string;
  height_cm?: number;
  weight_kg?: number;
  location?: string;
  timezone?: string;
  preferences?: any;
  emergency_contact?: any;
}

// Chat Types
export interface ChatMessage {
  id: string;
  session_id: string;
  user_id: string;
  role: 'user' | 'assistant' | 'system';
  content: string;
  emotion_detected?: string;
  crisis_detected: boolean;
  created_at: string;
}

export interface SendMessageRequest {
  content: string;
  session_id?: string;
}

export interface SendMessageResponse {
  message: ChatMessage;
  response: string;
  session_id: string;
  crisis_detected: boolean;
  emotion_detected?: string;
}

export interface ChatSession {
  id: string;
  user_id: string;
  title: string;
  started_at: string;
  last_message_at: string;
  metadata?: Record<string, any>;
}

// Emotion Types
export interface EmotionLog {
  id: string;
  user_id: string;
  emotion?: string; // Legacy field
  emotion_type?: string; // New field from backend
  intensity?: number;
  confidence?: number; // From backend
  all_scores?: Record<string, number>;
  trigger?: string;
  notes?: string;
  detected_from?: 'text' | 'voice' | 'manual';
  source?: 'text' | 'voice' | 'manual'; // New field from backend
  created_at: string;
}

export interface LogEmotionRequest {
  emotion: string;
  intensity: number;
  trigger?: string;
  notes?: string;
  detected_from?: 'text' | 'voice' | 'manual';
}

export interface EmotionAnalytics {
  dominant_emotions: Array<{ emotion: string; count: number; percentage: number }>;
  average_intensity: number;
  average_valence?: number;
  total_logs: number;
  emotions_over_time: Array<{ date: string; emotions: Record<string, number> }>;
}

export interface EmotionAggregate {
  id: string;
  user_id: string;
  date: string;
  dominant_emotion: string;
  emotion_distribution: Record<string, number>;
  average_valence?: number;
  total_entries: number;
  created_at: string;
}

// Aura Types
export interface AuraEntry {
  id: string;
  user_id: string;
  date: string;
  color_code: string;
  intensity: number;
  glow_level?: number;
  aura_type?: string;
  emotion_basis: Record<string, number>;
  created_at: string;
}

export interface AuraHistory {
  entries: AuraEntry[];
  trends: {
    dominant_color: string;
    average_intensity: number;
    chakra_insights: Record<string, any>;
  };
}

// Wellness Types
export interface WellnessScore {
  id: string;
  user_id: string;
  date: string;
  overall_score: number;
  emotion_score: number;
  wearable_score: number;
  engagement_score: number;
  score_components: Record<string, any>;
  insights: string[];
  recommendations: string[];
  created_at: string;
}

// Journal Types
export interface JournalEntry {
  id: string;
  user_id: string;
  date: string;
  content: string;
  mood_tag?: string;
  created_at: string;
}

export interface CreateJournalRequest {
  date: string;
  content: string;
  mood_tag?: string;
}

export interface UpdateJournalRequest {
  content?: string;
  mood_tag?: string;
}

// Goal Types
export interface Goal {
  id: string;
  user_id: string;
  title: string;
  description?: string;
  status: 'active' | 'completed' | 'archived';
  completion_percent: number;
  target_date?: string;
  is_completed: boolean;
  created_at: string;
  completed_at?: string;
}

export interface CreateGoalRequest {
  title: string;
  description?: string;
  target_date?: string;
}

export interface UpdateGoalRequest {
  title?: string;
  description?: string;
  status?: 'active' | 'completed' | 'archived';
  completion_percent?: number;
  target_date?: string;
  is_completed?: boolean;
}

// Dosha Types
export type DoshaType = 'vata' | 'pitta' | 'kapha';

export interface DoshaAssessment {
  id: string;
  user_id: string;
  vata_score: number;
  pitta_score: number;
  kapha_score: number;
  dominant_dosha: DoshaType;
  secondary_dosha?: DoshaType;
  assessment_data: Record<string, any>;
  created_at: string;
}

export interface DoshaRecommendations {
  dosha: DoshaType;
  diet: string[];
  lifestyle: string[];
  yoga: string[];
  meditation: string[];
}

export interface DoshaAnswer {
  question_id: number;
  answer_value: number;
}

export interface SubmitDoshaRequest {
  answers: DoshaAnswer[];
}

// Meal Types
export interface Meal {
  id: string;
  user_id: string;
  meal_time: string;
  meal_type: 'breakfast' | 'lunch' | 'dinner' | 'snack';
  meal_text: string;
  ingredients: string[];
  dosha_impact_tags: any;
  calories?: number;
  embedding?: number[];
  created_at: string;
}

export interface TodaysMeals {
  breakfast: Meal[];
  lunch: Meal[];
  dinner: Meal[];
  snack: Meal[];
}

export interface LogMealRequest {
  meal_text: string;
  meal_type: 'breakfast' | 'lunch' | 'dinner' | 'snack';
  meal_time: string;
  notes?: string;
}

export interface MealMoodCorrelation {
  food_item: string;
  positive_mood_count: number;
  negative_mood_count: number;
  correlation_score: number;
  recommendations: string[];
}

// Wearable Types
export interface WearableSnapshot {
  id: string;
  user_id: string;
  device_type: string;
  heart_rate?: number;
  hrv?: number;
  steps?: number;
  sleep_hours?: number;
  sleep_quality?: string;  // Changed from number to string
  stress_level?: string;   // Changed from number to string
  active_calories?: number;  // Added field
  recorded_at: string;
  created_at: string;
}

export interface SyncWearableRequest {
  device_type?: string;
  heart_rate?: number;
  hrv?: number;
  steps?: number;
  sleep_hours?: number;
  sleep_quality?: string;  // Changed from number to string
  stress_level?: string;   // Changed from number to string
  active_calories?: number;  // Added field
  recorded_at?: string;
}

// Analytics Types
export interface DateRangeParams {
  start_date?: string;
  end_date?: string;
}

export interface AnalyticsData {
  emotions: EmotionAnalytics;
  wellness_trend: Array<{ date: string; score: number }>;
  aura_progression: Array<{ date: string; color: string; intensity: number }>;
  meal_patterns: {
    meals_logged: number;
    average_calories: number;
    mood_correlations: MealMoodCorrelation[];
  };
  wearable_insights: {
    average_heart_rate: number;
    average_hrv: number;
    total_steps: number;
    average_sleep: number;
    stress_trend: Array<{ date: string; level: number }>;
  };
}

// Alert Types
export interface Alert {
  id: string;
  user_id: string;
  alert_type: 'crisis' | 'reminder' | 'insight' | 'achievement';
  severity: 'low' | 'medium' | 'high' | 'critical';
  title: string;
  message: string;
  action_url?: string;
  read: boolean;
  created_at: string;
}

export interface CreateAlertRequest {
  alert_type: 'crisis' | 'reminder' | 'insight' | 'achievement';
  severity: 'low' | 'medium' | 'high' | 'critical';
  title: string;
  message: string;
  action_url?: string;
}

// Admin Types
export interface SystemStats {
  total_users: number;
  active_users_today: number;
  total_messages: number;
  total_emotions_logged: number;
  crisis_alerts_count: number;
  average_wellness_score: number;
}

export interface AyurvedaResource {
  id: string;
  title: string;
  content: string;
  category: string;
  dosha_relevance?: DoshaType[];
  tags?: string[];
  created_at: string;
}

// Recommendation Types
export enum RecommendationSource {
  CHAT = 'chat',
  DEVICE = 'device',
  SYSTEM = 'system'
}

export enum RecommendationCategory {
  YOGA = 'yoga',
  AYURVEDA = 'ayurveda',
  LIFESTYLE = 'lifestyle',
  SLEEP = 'sleep',
  BREATHING = 'breathing',
  MEDITATION = 'meditation',
  DIET = 'diet'
}

export interface Recommendation {
  id: string;
  user_id: string;
  date: string; // ISO date string
  source: RecommendationSource;
  category: RecommendationCategory;
  title: string;
  content: string;
  created_at: string; // ISO datetime string
  meta?: Record<string, any>;
}

export interface DailyRecommendationsResponse {
  date: string; // ISO date string
  yoga: Recommendation[];
  ayurveda: Recommendation[];
  lifestyle: Recommendation[];
  sleep: Recommendation[];
  breathing: Recommendation[];
  meditation: Recommendation[];
  diet: Recommendation[];
}

export interface RecommendationsBySource {
  chat: Recommendation[];
  device: Recommendation[];
  system: Recommendation[];
}
