import axios, { AxiosInstance, AxiosError } from 'axios';
import { createClient, SupabaseClient } from '@supabase/supabase-js';
import type {
  ApiResponse,
  AuthResponse,
  LoginRequest,
  RegisterRequest,
  Profile,
  UpdateProfileRequest,
  SendMessageRequest,
  SendMessageResponse,
  ChatMessage,
  ChatSession,
  EmotionLog,
  LogEmotionRequest,
  EmotionAnalytics,
  EmotionAggregate,
  AuraEntry,
  AuraHistory,
  WellnessScore,
  JournalEntry,
  CreateJournalRequest,
  UpdateJournalRequest,
  Goal,
  CreateGoalRequest,
  UpdateGoalRequest,
  DoshaAssessment,
  DoshaRecommendations,
  SubmitDoshaRequest,
  Meal,
  LogMealRequest,
  MealMoodCorrelation,
  WearableSnapshot,
  SyncWearableRequest,
  AnalyticsData,
  DateRangeParams,
  Alert,
  CreateAlertRequest,
  SystemStats,
  AyurvedaResource,
} from '../types/api.types';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1';
const SUPABASE_URL = import.meta.env.VITE_SUPABASE_URL;
const SUPABASE_ANON_KEY = import.meta.env.VITE_SUPABASE_ANON_KEY;

class ApiService {
  private api: AxiosInstance;
  private supabase: SupabaseClient;
  private accessToken: string | null = null;

  constructor() {
    // Initialize axios
    this.api = axios.create({
      baseURL: API_BASE_URL,
      headers: {
        'Content-Type': 'application/json',
      },
      timeout: 30000, // 30 second timeout
    });

    // Initialize Supabase
    this.supabase = createClient(SUPABASE_URL, SUPABASE_ANON_KEY);

    // Add request interceptor to include auth token
    this.api.interceptors.request.use(
      (config) => {
        if (this.accessToken) {
          config.headers.Authorization = `Bearer ${this.accessToken}`;
        }
        return config;
      },
      (error) => Promise.reject(error)
    );

    // Add response interceptor for error handling
    this.api.interceptors.response.use(
      (response) => response,
      (error: AxiosError) => {
        if (error.response?.status === 401) {
          // Token expired, clear auth
          this.clearAuth();
          window.location.href = '/';
        }
        return Promise.reject(error);
      }
    );

    // Load token from localStorage
    this.loadAuth();
  }

  // ==================== Auth Methods ====================

  private saveAuth(token: string) {
    this.accessToken = token;
    localStorage.setItem('nirvami_auth_token', token);
  }

  private loadAuth() {
    const token = localStorage.getItem('nirvami_auth_token');
    if (token) {
      this.accessToken = token;
    }
  }

  private clearAuth() {
    this.accessToken = null;
    localStorage.removeItem('nirvami_auth_token');
    localStorage.removeItem('nirvami_user');
  }

  isAuthenticated(): boolean {
    return !!this.accessToken;
  }

  async getCurrentUser(): Promise<{ id: string; email: string; full_name?: string }> {
    const response = await this.api.get('/auth/me');
    return response.data;
  }

  async login(credentials: LoginRequest): Promise<AuthResponse> {
    try {
      // Use backend endpoint for login
      const response = await this.api.post<AuthResponse>('/auth/login', credentials);

      this.saveAuth(response.data.access_token);

      return response.data;
    } catch (error: any) {
      // If backend login failed, try to detect network issues and fallback to a dev-session
      console.warn('Backend login failed:', error?.message || error);

      const isNetworkError = (!error || !error.response) || error.code === 'ECONNABORTED' || (typeof navigator !== 'undefined' && !navigator.onLine);

      if (isNetworkError) {
        // Development fallback: create a local dev session so the UI remains functional offline.
        console.warn('Network/backend unreachable — creating local dev session (development only).');

        const devUserId = import.meta.env.VITE_DEV_TEST_USER_ID || '00000000-0000-0000-0000-000000000000';
        const fakeToken = `dev-token-${Date.now()}`;

        // Save fake token locally
        this.saveAuth(fakeToken);

        const devUser = {
          id: devUserId,
          email: credentials.email,
          full_name: credentials.email.split('@')[0]
        };

        // Also store a lightweight user object for UI usage
        try {
          localStorage.setItem('nirvami_user', JSON.stringify(devUser));
        } catch (e) {
          // ignore storage errors
        }

        return {
          access_token: fakeToken,
          token_type: 'bearer',
          user: devUser
        };
      }

      // Otherwise fall back to Supabase direct login (normal behavior)
      console.log('Backend reachable but login failed — trying Supabase directly...');
      const { data, error: supabaseError } = await this.supabase.auth.signInWithPassword({
        email: credentials.email,
        password: credentials.password,
      });

      if (supabaseError) throw new Error(supabaseError.message);
      if (!data.session) throw new Error('Login failed');

      this.saveAuth(data.session.access_token);

      return {
        access_token: data.session.access_token,
        token_type: 'bearer',
        user: {
          id: data.user.id,
          email: data.user.email!,
          created_at: data.user.created_at,
        },
      };
    }
  }

  async loginWithSupabase(credentials: LoginRequest): Promise<AuthResponse> {
    // Direct Supabase login - bypass backend for speed
    const { data, error: supabaseError } = await this.supabase.auth.signInWithPassword({
      email: credentials.email,
      password: credentials.password,
    });

    if (supabaseError) throw new Error(supabaseError.message);
    if (!data.session) throw new Error('Login failed');

    this.saveAuth(data.session.access_token);

    // Fetch user profile from users table
    let fullName = data.user.email!.split('@')[0];
    try {
      const { data: userData, error: userError } = await this.supabase
        .from('users')
        .select('full_name')
        .eq('id', data.user.id)
        .single();
      
      if (!userError && userData?.full_name) {
        fullName = userData.full_name;
      }
    } catch (e) {
      console.log('Could not fetch user profile, using email as name');
    }

    return {
      access_token: data.session.access_token,
      token_type: 'bearer',
      user: {
        id: data.user.id,
        email: data.user.email!,
        full_name: fullName,
        created_at: data.user.created_at,
      },
    };
  }

  async register(data: RegisterRequest): Promise<AuthResponse> {
    try {
      // Use backend endpoint for registration (auto-confirms users)
      const response = await this.api.post<AuthResponse>('/auth/register', {
        email: data.email,
        password: data.password,
        full_name: data.full_name,
        age: data.age,
        gender: data.gender,
      });

      console.log('API register response:', response.data);

      this.saveAuth(response.data.access_token);

      return response.data;
    } catch (error: any) {
      console.error('Backend registration failed:', error);
      console.error('Error response:', error.response?.data);

      // If backend fails, throw a user-friendly error
      if (error.response?.data?.detail) {
        throw new Error(error.response.data.detail);
      }

      throw new Error(error.message || 'Registration failed. Please try again.');
    }
  }

  async logout(): Promise<void> {
    await this.supabase.auth.signOut();
    this.clearAuth();
  }

  // ==================== Profile Methods ====================

  async getProfile(): Promise<Profile> {
    const response = await this.api.get<Profile>('/profile');
    return response.data;
  }

  async updateProfile(data: UpdateProfileRequest): Promise<Profile> {
    const response = await this.api.put<Profile>('/profile', data);
    return response.data;
  }

  async exportUserData(): Promise<any> {
    const response = await this.api.get('/profile/export-data');
    return response.data;
  }

  async deleteAccount(): Promise<void> {
    await this.api.delete('/profile');
  }

  async getPreferences(): Promise<any> {
    const response = await this.api.get('/profile/preferences');
    return response.data;
  }

  async updatePreferences(preferences: any): Promise<any> {
    const response = await this.api.put('/profile/preferences', preferences);
    return response.data;
  }

  // ==================== Chat Methods ====================

  async sendMessage(data: SendMessageRequest): Promise<SendMessageResponse> {
    const response = await this.api.post<SendMessageResponse>('/chat/message', data);
    return response.data;
  }

  async getChatHistory(sessionId?: string): Promise<ChatMessage[]> {
    const params = sessionId ? { session_id: sessionId } : {};
    const response = await this.api.get<ChatMessage[]>('/chat/history', { params });
    return response.data;
  }

  async getChatSessions(): Promise<ChatSession[]> {
    const response = await this.api.get<ChatSession[]>('/chat/sessions');
    return response.data;
  }

  async getSessionMessages(sessionId: string): Promise<ChatMessage[]> {
    const response = await this.api.get<ChatMessage[]>(`/chat/sessions/${sessionId}/messages`);
    return response.data;
  }

  // ==================== Emotion Methods ====================

  async logEmotion(data: LogEmotionRequest): Promise<EmotionLog> {
    const response = await this.api.post<EmotionLog>('/emotions/log', data);
    return response.data;
  }

  async logMoodFromPopup(data: {
    mood: string;
    intensity: number;
    energy?: number;
    notes?: string;
    source: string;
  }): Promise<{ ok: boolean; emotion_log_id?: string; detail?: string }> {
    try {
      // Get current user from Supabase session
      const { data: sessionData } = await this.supabase.auth.getSession();
      if (!sessionData.session) {
        throw new Error('Not authenticated');
      }

      // Map mood to emotion_type and create all_scores
      // Mood options: joy, sadness, anger, fear, anxiety, stress, calm, neutral
      const moodToEmotion: Record<string, string> = {
        'joy': 'joy',
        'sadness': 'sadness',
        'anger': 'anger',
        'fear': 'fear',
        'anxiety': 'fear', // anxiety maps to fear
        'stress': 'anger', // stress maps to anger
        'calm': 'joy', // calm maps to joy
        'neutral': 'neutral'
      };

      const emotion_type = moodToEmotion[data.mood] || data.mood;
      const confidence = data.intensity / 10; // Convert 1-10 scale to 0-1 confidence

      // Create all_scores object with the selected mood having highest score
      const all_scores: Record<string, number> = {
        'joy': 0.0,
        'sadness': 0.0,
        'anger': 0.0,
        'fear': 0.0,
        'surprise': 0.0,
        'neutral': 0.0
      };
      all_scores[emotion_type] = confidence;

      // Insert directly into Supabase emotion_logs table
      const { data: insertData, error } = await this.supabase
        .from('emotion_logs')
        .insert({
          user_id: sessionData.session.user.id,
          emotion_type: emotion_type,
          confidence: confidence,
          all_scores: all_scores,
          mood: data.mood,
          intensity: data.intensity,
          energy: data.energy,
          notes: data.notes,
          source: data.source,
          logged_at: new Date().toISOString(),
        })
        .select('id')
        .single();

      if (error) {
        console.error('Supabase insert error:', error);
        throw new Error(error.message);
      }

      return {
        ok: true,
        emotion_log_id: insertData.id,
      };
    } catch (error: any) {
      console.error('Failed to log mood:', error);
      return {
        ok: false,
        detail: error.message || 'Failed to save mood',
      };
    }
  }

  async getEmotionLogs(params?: DateRangeParams): Promise<EmotionLog[]> {
    const response = await this.api.get<EmotionLog[]>('/emotions/history', { params });
    return response.data;
  }

  async getEmotionAnalytics(params?: DateRangeParams): Promise<EmotionAnalytics> {
    const response = await this.api.get<EmotionAnalytics>('/emotions/analytics', { params });
    return response.data;
  }

  async getEmotionAggregates(days: number = 30): Promise<EmotionAggregate[]> {
    const response = await this.api.get<EmotionAggregate[]>('/emotions/aggregates', { params: { days } });
    return response.data;
  }

  async detectEmotionFromText(text: string): Promise<{ emotion: string; confidence: number }> {
    const response = await this.api.post('/emotions/detect', { text });
    return response.data;
  }

  // ==================== Aura Methods ====================

  async getTodayAura(): Promise<AuraEntry> {
    try {
      // Use Supabase directly for faster loading
      const { data: sessionData } = await this.supabase.auth.getSession();
      if (!sessionData.session) {
        throw new Error('Not authenticated');
      }

      const today = new Date().toISOString().split('T')[0];
      
      const { data, error } = await this.supabase
        .from('aura_entries')
        .select('*')
        .eq('user_id', sessionData.session.user.id)
        .gte('generated_at', `${today}T00:00:00Z`)
        .lte('generated_at', `${today}T23:59:59Z`)
        .order('generated_at', { ascending: false })
        .limit(1)
        .single();

      if (error) {
        // If no aura exists for today, generate one via backend
        console.log('No aura found for today, generating...');
        return await this.generateAura();
      }

      return data as AuraEntry;
    } catch (error: any) {
      console.error('Error fetching today aura:', error);
      // Fallback to backend API
      const response = await this.api.get<AuraEntry>('/aura/today');
      return response.data;
    }
  }

  async getAuraHistory(params?: DateRangeParams): Promise<AuraHistory> {
    try {
      // Use Supabase directly for faster loading
      const { data: sessionData } = await this.supabase.auth.getSession();
      if (!sessionData.session) {
        throw new Error('Not authenticated');
      }

      let query = this.supabase
        .from('aura_entries')
        .select('*')
        .eq('user_id', sessionData.session.user.id)
        .order('generated_at', { ascending: false });

      if (params?.start_date) {
        query = query.gte('generated_at', params.start_date);
      }
      if (params?.end_date) {
        query = query.lte('generated_at', params.end_date);
      }

      const { data, error } = await query;

      if (error) throw error;

      return {
        entries: data || [],
        total_count: data?.length || 0,
        average_intensity: data && data.length > 0 
          ? data.reduce((sum, e) => sum + (e.intensity || 50), 0) / data.length 
          : 0
      };
    } catch (error: any) {
      console.error('Error fetching aura history:', error);
      // Fallback to backend API
      const response = await this.api.get<AuraHistory>('/aura/history', { params });
      return response.data;
    }
  }

  async generateAura(): Promise<AuraEntry> {
    const response = await this.api.post<AuraEntry>('/aura/generate');
    return response.data;
  }

  async getAuraTimeline(days: number = 30): Promise<AuraEntry[]> {
    const response = await this.api.get<AuraEntry[]>('/aura/timeline', { params: { days } });
    return response.data;
  }

  // ==================== Wellness Methods ====================

  async getTodayWellness(): Promise<WellnessScore> {
    const response = await this.api.get<WellnessScore>('/wellness/today');
    return response.data;
  }

  async getWellnessHistory(params?: DateRangeParams): Promise<WellnessScore[]> {
    const response = await this.api.get<WellnessScore[]>('/wellness/history', { params });
    return response.data;
  }

  async computeWellness(): Promise<WellnessScore> {
    const response = await this.api.post<WellnessScore>('/wellness/compute');
    return response.data;
  }

  // ==================== Journal Methods ====================

  async createJournal(data: CreateJournalRequest): Promise<JournalEntry> {
    const response = await this.api.post<JournalEntry>('/journal', data);
    return response.data;
  }

  async getJournalEntries(days: number = 30): Promise<JournalEntry[]> {
    const response = await this.api.get<JournalEntry[]>('/journal', { params: { days } });
    return response.data;
  }

  async getJournalEntry(id: string): Promise<JournalEntry> {
    const response = await this.api.get<JournalEntry>(`/journal/${id}`);
    return response.data;
  }

  async updateJournal(id: string, data: UpdateJournalRequest): Promise<JournalEntry> {
    const response = await this.api.put<JournalEntry>(`/journal/${id}`, data);
    return response.data;
  }

  async deleteJournal(id: string): Promise<void> {
    await this.api.delete(`/journal/${id}`);
  }

  // ==================== Goal Methods ====================

  async createGoal(data: CreateGoalRequest): Promise<Goal> {
    const response = await this.api.post<Goal>('/goals', data);
    return response.data;
  }

  async getGoals(status?: 'active' | 'completed' | 'archived'): Promise<Goal[]> {
    const params = status ? { status } : {};
    const response = await this.api.get<Goal[]>('/goals', { params });
    return response.data;
  }

  async getGoal(id: string): Promise<Goal> {
    const response = await this.api.get<Goal>(`/goals/${id}`);
    return response.data;
  }

  async updateGoal(id: string, data: UpdateGoalRequest): Promise<Goal> {
    const response = await this.api.put<Goal>(`/goals/${id}`, data);
    return response.data;
  }

  async deleteGoal(id: string): Promise<void> {
    await this.api.delete(`/goals/${id}`);
  }

  async completeGoal(id: string): Promise<Goal> {
    const response = await this.api.post<Goal>(`/goals/${id}/complete`);
    return response.data;
  }

  // ==================== Dosha Methods ====================

  async getLatestDosha(): Promise<DoshaAssessment> {
    const response = await this.api.get<DoshaAssessment>('/dosha/latest');
    return response.data;
  }

  async getDoshaHistory(): Promise<DoshaAssessment[]> {
    const response = await this.api.get<DoshaAssessment[]>('/dosha/history');
    return response.data;
  }

  async submitDoshaAssessment(data: SubmitDoshaRequest): Promise<DoshaAssessment> {
    const response = await this.api.post<DoshaAssessment>('/dosha/assess', data);
    return response.data;
  }

  async getDoshaRecommendations(dosha?: string): Promise<DoshaRecommendations> {
    const params = dosha ? { dosha } : {};
    const response = await this.api.get<DoshaRecommendations>('/dosha/recommendations', { params });
    return response.data;
  }

  async getCurrentDosha(): Promise<DoshaAssessment | null> {
    try {
      const response = await this.api.get<any>('/dosha/latest');
      return response.data;
    } catch (error: any) {
      if (error.response?.status === 404) {
        return null; // No assessment found
      }
      throw error;
    }
  }

  // ==================== Meal Methods ====================

  async logMeal(data: LogMealRequest): Promise<Meal> {
    const response = await this.api.post<Meal>('/meals/log', data);
    return response.data;
  }

  async getMealHistory(params?: DateRangeParams): Promise<Meal[]> {
    const response = await this.api.get<Meal[]>('/meals/history', { params });
    return response.data;
  }

  async getMealMoodCorrelations(): Promise<MealMoodCorrelation[]> {
    const response = await this.api.get<MealMoodCorrelation[]>('/meals/mood-correlations');
    return response.data;
  }

  async getMealCorrelations(): Promise<{
    mood_boosting_foods: Array<{ food: string; impact_score: number; occurrences: number }>;
    foods_to_watch: Array<{ food: string; impact_score: number; occurrences: number }>;
    total_foods_analyzed: number;
  }> {
    const response = await this.api.get('/meals/correlations');
    return response.data;
  }

  async analyzeMealCorrelations(): Promise<{
    success: boolean;
    correlations_calculated: number;
    correlations_stored: number;
    message: string;
  }> {
    const response = await this.api.post('/meals/analyze-correlations');
    return response.data;
  }

  async getTodayMeals(): Promise<Meal[]> {
    const today = new Date().toISOString().split('T')[0];
    return this.getMealHistory({ start_date: today, end_date: today });
  }

  // ==================== Wearable Methods ====================

  async syncWearableData(data: SyncWearableRequest): Promise<WearableSnapshot> {
    const response = await this.api.post<WearableSnapshot>('/wearable/push', data);
    return response.data;
  }

  async submitManualHealthEntry(data: {
    date: string;
    sleep_hours?: number;
    avg_heart_rate?: number;
    steps?: number;
    stress_level?: number;
    calories_burned?: number;
  }): Promise<any> {
    const response = await this.api.post('/wearable-v2/manual-entry', data);
    return response.data;
  }

  async analyzeWearableHealth(): Promise<any> {
    const response = await this.api.post('/wearable-v2/analyze');
    return response.data;
  }

  async getLatestWearableData(): Promise<any> {
    const response = await this.api.get('/wearable-v2/latest');
    return response.data;
  }

  async getWearableHistory(limit: number = 30): Promise<any> {
    const response = await this.api.get('/wearable-v2/history', { params: { limit } });
    return response.data;
  }

  async submitWatchData(data: {
    provider: string;
    captured_at?: string;
    heart_rate?: number;
    hrv_ms?: number;
    steps?: number;
    sleep_hours?: number;
    stress_level?: number;
    calories_burned?: number;
  }): Promise<any> {
    const response = await this.api.post('/wearable/intake', data);
    return response.data;
  }

  async aggregateDailyWearableStats(date?: string): Promise<any> {
    const response = await this.api.post('/wearable/aggregate-daily', null, {
      params: { target_date: date }
    });
    return response.data;
  }

  async getWearableSummary(date?: string): Promise<any> {
    const response = await this.api.get('/wellness/today-wearable-summary', {
      params: { target_date: date }
    });
    return response.data;
  }

  async getLatestWearable(): Promise<WearableSnapshot> {
    const response = await this.api.get<WearableSnapshot>('/wearable/latest');
    return response.data;
  }

  async getLatestWearableSummary(): Promise<any> {
    const response = await this.api.get('/wearable/latest-summary');
    return response.data;
  }

  async uploadWatchXML(formData: FormData): Promise<any> {
    const response = await this.api.post('/wearable/upload-xml', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  }

  // ==================== Analytics Methods ====================

  async getAnalytics(params?: DateRangeParams): Promise<AnalyticsData> {
    const response = await this.api.get<AnalyticsData>('/analytics/comprehensive', { params });
    return response.data;
  }

  async getEmotionTrends(params?: DateRangeParams): Promise<any> {
    const response = await this.api.get('/analytics/emotion-trends', { params });
    return response.data;
  }

  async getWellnessTrends(params?: DateRangeParams): Promise<any> {
    const response = await this.api.get('/analytics/wellness-trends', { params });
    return response.data;
  }

  // ==================== Alert Methods ====================

  async getAlerts(params?: { unread_only?: boolean }): Promise<Alert[]> {
    const response = await this.api.get<Alert[]>('/alerts', { params });
    return response.data;
  }

  async markAlertRead(alertId: string): Promise<Alert> {
    const response = await this.api.put<Alert>(`/alerts/${alertId}/read`);
    return response.data;
  }

  async createAlert(data: CreateAlertRequest): Promise<Alert> {
    const response = await this.api.post<Alert>('/alerts', data);
    return response.data;
  }

  async getUnreadCount(): Promise<number> {
    const response = await this.api.get<{ count: number }>('/alerts/unread-count');
    return response.data.count;
  }

  // ==================== Admin Methods ====================

  async getSystemStats(): Promise<SystemStats> {
    const response = await this.api.get<SystemStats>('/admin/analytics');
    return response.data;
  }

  async searchAyurvedaResources(query: string): Promise<AyurvedaResource[]> {
    const response = await this.api.get<AyurvedaResource[]>('/admin/ayurveda/search', {
      params: { q: query },
    });
    return response.data;
  }

  // ==================== Watch Methods ====================

  async getTodayWatchData(): Promise<any> {
    const response = await this.api.get('/watch/today');
    return response.data;
  }

  async postWatchData(data: any): Promise<any> {
    const response = await this.api.post('/watch/data', data);
    return response.data;
  }

  // ==================== Yoga & Sound Therapy Methods ====================

  async getYogaPoses(params?: { dosha?: string; emotion?: string }): Promise<any> {
    const response = await this.api.get('/yoga/poses', { params });
    return response.data;
  }

  async getSoundTracks(params?: { dosha?: string; mood?: string }): Promise<any> {
    const response = await this.api.get('/yoga/sound-tracks', { params });
    return response.data;
  }

  async logYogaPractice(poseId: string, durationMinutes: number, notes?: string): Promise<any> {
    const response = await this.api.post('/yoga/practice-log', {
      pose_id: poseId,
      duration_minutes: durationMinutes,
      notes,
    });
    return response.data;
  }

  async logSoundTherapy(trackId: string, durationMinutes: number, notes?: string): Promise<any> {
    const response = await this.api.post('/yoga/sound-therapy-log', {
      track_id: trackId,
      duration_minutes: durationMinutes,
      notes,
    });
    return response.data;
  }

  async getAyurvedaResources(params?: { dosha?: string; category?: string; limit?: number }): Promise<any> {
    const response = await this.api.get('/yoga/ayurveda-resources', { params });
    return response.data;
  }

  // ==================== Daily Routines Methods ====================

  async getRoutines(days?: number): Promise<any> {
    const response = await this.api.get('/routines/entries', {
      params: days ? { days } : undefined,
    });
    return response.data;
  }

  async addRoutine(data: {
    date: string;
    time: string;
    activity: string;
    notes?: string;
  }): Promise<any> {
    const response = await this.api.post('/routines/entry', data);
    return response.data;
  }

  async deleteRoutine(entryId: string): Promise<any> {
    const response = await this.api.delete(`/routines/entry/${entryId}`);
    return response.data;
  }

  // ==================== Streak & User Preferences Methods ====================

  async getCurrentStreak(): Promise<any> {
    const response = await this.api.get('/profile/streak/current');
    return response.data;
  }

  async recordVisit(): Promise<any> {
    const response = await this.api.post('/profile/streak/record-visit');
    return response.data;
  }

  async checkMoodLoggedToday(): Promise<{ logged_today: boolean; date: string }> {
    const response = await this.api.get('/emotions/today/logged');
    return response.data;
  }

  // ==================== Alerts & Notifications Methods ====================

  async getAlerts(status: string = 'active'): Promise<Alert[]> {
    const response = await this.api.get<Alert[]>('/alerts/', { params: { status } });
    return response.data;
  }

  async getNotifications(unreadOnly: boolean = false): Promise<any[]> {
    const response = await this.api.get('/alerts/notifications', { params: { unread_only: unreadOnly } });
    return response.data;
  }

  async getUnreadNotificationCount(): Promise<number> {
    const response = await this.api.get<{ count: number }>('/alerts/unread-count');
    return response.data.count;
  }

  async acknowledgeAlert(alertId: string): Promise<any> {
    const response = await this.api.put(`/alerts/${alertId}/acknowledge`);
    return response.data;
  }

  async markNotificationRead(notificationId: string): Promise<any> {
    const response = await this.api.put(`/alerts/notifications/${notificationId}/read`);
    return response.data;
  }
}

// Export singleton instance
export const api = new ApiService();
export default api;

