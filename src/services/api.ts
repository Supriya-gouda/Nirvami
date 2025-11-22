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
  EmotionLog,
  LogEmotionRequest,
  EmotionAnalytics,
  AuraEntry,
  AuraHistory,
  WellnessScore,
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

  async getCurrentUser(): Promise<{ id: string; email: string; name?: string }> {
    const response = await this.api.get('/auth/user');
    return response.data;
  }

  async login(credentials: LoginRequest): Promise<AuthResponse> {
    try {
      // Use backend endpoint for login
      const response = await this.api.post<AuthResponse>('/auth/login', credentials);

      this.saveAuth(response.data.access_token);

      return response.data;
    } catch (error: any) {
      // Fallback to Supabase direct login
      console.log('Backend login failed, trying Supabase directly...');
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

      this.saveAuth(response.data.access_token);

      return response.data;
    } catch (error: any) {
      console.error('Backend registration failed:', error);

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

  async getChatSessions(): Promise<Array<{ session_id: string; message_count: number; last_message_at: string }>> {
    const response = await this.api.get('/chat/sessions');
    return response.data;
  }

  // ==================== Emotion Methods ====================

  async logEmotion(data: LogEmotionRequest): Promise<EmotionLog> {
    const response = await this.api.post<EmotionLog>('/emotions/log', data);
    return response.data;
  }

  async getEmotionLogs(params?: DateRangeParams): Promise<EmotionLog[]> {
    const response = await this.api.get<EmotionLog[]>('/emotions/history', { params });
    return response.data;
  }

  async getEmotionAnalytics(params?: DateRangeParams): Promise<EmotionAnalytics> {
    const response = await this.api.get<EmotionAnalytics>('/emotions/analytics', { params });
    return response.data;
  }

  async detectEmotionFromText(text: string): Promise<{ emotion: string; confidence: number }> {
    const response = await this.api.post('/emotions/detect', { text });
    return response.data;
  }

  // ==================== Aura Methods ====================

  async getTodayAura(): Promise<AuraEntry> {
    const response = await this.api.get<AuraEntry>('/aura/today');
    return response.data;
  }

  async getAuraHistory(params?: DateRangeParams): Promise<AuraHistory> {
    const response = await this.api.get<AuraHistory>('/aura/history', { params });
    return response.data;
  }

  async generateAura(): Promise<AuraEntry> {
    const response = await this.api.post<AuraEntry>('/aura/generate');
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

  async getTodayMeals(): Promise<Meal[]> {
    const today = new Date().toISOString().split('T')[0];
    return this.getMealHistory({ start_date: today, end_date: today });
  }

  // ==================== Wearable Methods ====================

  async syncWearableData(data: SyncWearableRequest): Promise<WearableSnapshot> {
    const response = await this.api.post<WearableSnapshot>('/wearable/push', data);
    return response.data;
  }

  async getWearableHistory(params?: DateRangeParams): Promise<WearableSnapshot[]> {
    const response = await this.api.get<WearableSnapshot[]>('/wearable/history', { params });
    return response.data;
  }

  async getLatestWearable(): Promise<WearableSnapshot> {
    const response = await this.api.get<WearableSnapshot>('/wearable/latest');
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
}

// Export singleton instance
export const api = new ApiService();
export default api;
