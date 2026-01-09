import { useState, useEffect } from 'react';
import { motion } from 'motion/react';
import { TrendingUp, RefreshCw, Activity, Heart, Target, Award, Zap, Wind, Flame, Droplet, RotateCcw } from 'lucide-react';
import { Navigation } from './Navigation';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { Badge } from './ui/badge';
import { Button } from './ui/button';
import {
  LineChart,
  Line,
  AreaChart,
  Area,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  RadarChart,
  PolarGrid,
  PolarAngleAxis,
  PolarRadiusAxis,
  Radar,
} from 'recharts';
import type { PageType } from '../App';
import type { User, DoshaAssessment } from '../types/api.types';
import api from '../services/api';

interface ProgressAnalyticsPageProps {
  user: User | null;
  onNavigate: (page: PageType) => void;
  onLogout?: () => void;
  onOpenNotifications?: () => void;
}

interface DashboardMetrics {
  avg_mood_today: number | null;
  stress_level_today: number | null;
  total_recommendations_today: number;
  completed_recommendations_today: number;
  adherence_value_today: number | null;
  consistency_score: number;
  wellness_score: number | null;
  last_updated: string;
}

export function ProgressAnalyticsPage({ user, onNavigate, onLogout, onOpenNotifications }: ProgressAnalyticsPageProps) {
  const [metrics, setMetrics] = useState<DashboardMetrics | null>(null);
  const [emotionTrends, setEmotionTrends] = useState<any[]>([]);
  const [wellnessTrend, setWellnessTrend] = useState<any[]>([]);
  const [adherenceTrend, setAdherenceTrend] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [doshaAssessment, setDoshaAssessment] = useState<DoshaAssessment | null>(null);

  // Wellness dimensions for radar chart (preserved from original)
  const [wellnessData, setWellnessData] = useState<any[]>([
    { dimension: 'Sleep', score: 75 },
    { dimension: 'Nutrition', score: 68 },
    { dimension: 'Exercise', score: 82 },
    { dimension: 'Mindfulness', score: 71 },
    { dimension: 'Social', score: 65 },
    { dimension: 'Purpose', score: 78 },
  ]);

  // Dosha data (preserved from original)
  const [doshaData, setDoshaData] = useState<any[]>([
    { aspect: 'Vata', current: 65, optimal: 80 },
    { aspect: 'Pitta', current: 85, optimal: 70 },
    { aspect: 'Kapha', current: 70, optimal: 75 },
  ]);

  useEffect(() => {
    // Load real data immediately
    loadAllData(false);
    
    // Set up auto-refresh every 5 minutes
    const refreshInterval = setInterval(() => {
      loadAllData(true);
    }, 5 * 60 * 1000);
    
    return () => clearInterval(refreshInterval);
  }, []);

  const loadAllData = async (silent = false) => {
    try {
      if (!silent) setLoading(true);
      setRefreshing(true);

      // Load all data in parallel
      const [
        dashboardMetricsData,
        emotionTrendsData,
        wellnessTrendData,
        adherenceTrendData,
        doshaData,
      ] = await Promise.all([
        api.getDashboardMetrics(),
        api.getEmotionTrendsGraph(30),
        api.getWellnessTrendGraph(30),
        api.getAdherenceTrendGraph(30),
        api.getCurrentDosha().catch(() => null),
      ]);

      setMetrics(dashboardMetricsData);
      setEmotionTrends(emotionTrendsData.trends || []);
      setWellnessTrend(wellnessTrendData.wellness_trend || []);
      setAdherenceTrend(adherenceTrendData.adherence_trend || []);
      setDoshaAssessment(doshaData);

      console.log('📊 [Progress] Loaded progress analytics data');
      console.log('[Progress] Avg Mood computed:', dashboardMetricsData.avg_mood_today);
      console.log('[Progress] Stress Level:', dashboardMetricsData.stress_level_today);
      console.log('[Progress] Total Recommendations Today:', dashboardMetricsData.total_recommendations_today);
      console.log('[Progress] Completed Recommendations Today:', dashboardMetricsData.completed_recommendations_today);
      console.log('[Progress] Adherence updated:', dashboardMetricsData.adherence_value_today);
      console.log('[Progress] Consistency score recalculated:', dashboardMetricsData.consistency_score);
      console.log('[Progress] Wellness Score:', dashboardMetricsData.wellness_score);
      console.log('[Progress] Emotion trends data points:', emotionTrendsData.trends?.length || 0);
      console.log('[Progress] Wellness trend data points:', wellnessTrendData.wellness_trend?.length || 0);
      console.log('[Progress] Adherence trend data points:', adherenceTrendData.adherence_trend?.length || 0);
      console.log('[Progress] Avg Mood computed:', dashboardMetricsData.avg_mood_today);
      console.log('[Progress] Stress Level:', dashboardMetricsData.stress_level_today);
      console.log('[Progress] Total Recommendations Today:', dashboardMetricsData.total_recommendations_today);
      console.log('[Progress] Completed Recommendations Today:', dashboardMetricsData.completed_recommendations_today);
      console.log('[Progress] Adherence updated:', dashboardMetricsData.adherence_value_today);
      console.log('[Progress] Consistency score recalculated:', dashboardMetricsData.consistency_score);
      console.log('[Progress] Wellness Score:', dashboardMetricsData.wellness_score);
      console.log('[Progress] Emotion trends data points:', emotionTrendsData.trends?.length || 0);
      console.log('[Progress] Wellness trend data points:', wellnessTrendData.wellness_trend?.length || 0);
      console.log('[Progress] Adherence trend data points:', adherenceTrendData.adherence_trend?.length || 0);
    } catch (error) {
      console.error('Error loading progress analytics:', error);
      // Set empty state on error to prevent crashes
      setMetrics({
        avg_mood_today: null,
        stress_level_today: null,
        total_recommendations_today: 0,
        completed_recommendations_today: 0,
        adherence_value_today: null,
        consistency_score: 0,
        wellness_score: null,
        last_updated: new Date().toISOString()
      });
      setEmotionTrends([]);
      setWellnessTrend([]);
      setAdherenceTrend([]);
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  };

  const handleRefresh = () => {
    loadAllData();
  };

  // Format data for charts
  const formatEmotionTrendsData = () => {
    return emotionTrends.map((item) => ({
      date: new Date(item.date).toLocaleDateString('en-US', { month: 'short', day: 'numeric' }),
      positive: item.positive,
      negative: item.negative,
      neutral: item.neutral,
    }));
  };

  const formatWellnessTrendData = () => {
    return wellnessTrend.map((item) => ({
      date: new Date(item.date).toLocaleDateString('en-US', { month: 'short', day: 'numeric' }),
      score: item.wellness_score,
    }));
  };

  const formatAdherenceTrendData = () => {
    return adherenceTrend
      .filter((item) => item.adherence_percentage !== null)
      .map((item) => ({
        date: new Date(item.date).toLocaleDateString('en-US', { month: 'short', day: 'numeric' }),
        adherence: item.adherence_percentage,
        completed: item.completed_recommendations,
        total: item.total_recommendations,
      }));
  };

  if (loading && !metrics) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <RefreshCw className="w-12 h-12 animate-spin text-purple-500 mx-auto mb-4" />
          <p className="text-gray-600">Loading analytics...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-purple-50 via-white to-blue-50">
      <Navigation currentPage="progress" onNavigate={onNavigate} onLogout={onLogout} user={user} onOpenNotifications={onOpenNotifications} />

      <div className="max-w-7xl mx-auto p-8">
        {/* Header */}
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          className="mb-8"
        >
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-4xl font-bold text-gray-800 mb-2">Progress & Analytics</h1>
              <p className="text-gray-600">Track your wellness journey with real-time insights</p>
              {metrics?.last_updated && (
                <p className="text-xs text-gray-500 mt-1">
                  Last updated: {new Date(metrics.last_updated).toLocaleTimeString()}
                </p>
              )}
            </div>
            <Button
              onClick={handleRefresh}
              disabled={refreshing}
              className="bg-gradient-to-r from-purple-500 to-blue-500"
            >
              <RefreshCw className={`w-4 h-4 mr-2 ${refreshing ? 'animate-spin' : ''}`} />
              Refresh
            </Button>
          </div>
        </motion.div>

        {/* 7 Dashboard Summary Cards */}
        <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-7 gap-4 mb-8">
          {/* 1. Avg Mood Today */}
          <motion.div
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ delay: 0.1 }}
            whileHover={{ scale: 1.05 }}
          >
            <Card>
              <CardContent className="p-4">
                <div className="flex flex-col items-center text-center">
                  <Heart className="w-8 h-8 text-pink-500 mb-2" />
                  <p className="text-xs text-gray-600 mb-1">Avg Mood</p>
                  <p className="text-2xl font-bold text-gray-800">
                    {metrics?.avg_mood_today !== null ? metrics.avg_mood_today.toFixed(1) : '—'}
                  </p>
                  <p className="text-xs text-gray-500">Today</p>
                </div>
              </CardContent>
            </Card>
          </motion.div>

          {/* 2. Stress Level Today */}
          <motion.div
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ delay: 0.15 }}
            whileHover={{ scale: 1.05 }}
          >
            <Card>
              <CardContent className="p-4">
                <div className="flex flex-col items-center text-center">
                  <Activity className="w-8 h-8 text-orange-500 mb-2" />
                  <p className="text-xs text-gray-600 mb-1">Stress</p>
                  <p className="text-2xl font-bold text-gray-800">
                    {metrics?.stress_level_today !== null ? metrics.stress_level_today.toFixed(1) : '—'}
                  </p>
                  <p className="text-xs text-gray-500">Today</p>
                </div>
              </CardContent>
            </Card>
          </motion.div>

          {/* 3. Total Recommendations Today */}
          <motion.div
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ delay: 0.2 }}
            whileHover={{ scale: 1.05 }}
          >
            <Card>
              <CardContent className="p-4">
                <div className="flex flex-col items-center text-center">
                  <Target className="w-8 h-8 text-blue-500 mb-2" />
                  <p className="text-xs text-gray-600 mb-1">Total Recs</p>
                  <p className="text-2xl font-bold text-gray-800">
                    {metrics?.total_recommendations_today || 0}
                  </p>
                  <p className="text-xs text-gray-500">Today</p>
                </div>
              </CardContent>
            </Card>
          </motion.div>

          {/* 4. Completed Recommendations Today */}
          <motion.div
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ delay: 0.25 }}
            whileHover={{ scale: 1.05 }}
          >
            <Card>
              <CardContent className="p-4">
                <div className="flex flex-col items-center text-center">
                  <Award className="w-8 h-8 text-green-500 mb-2" />
                  <p className="text-xs text-gray-600 mb-1">Completed</p>
                  <p className="text-2xl font-bold text-gray-800">
                    {metrics?.completed_recommendations_today || 0}
                  </p>
                  <p className="text-xs text-gray-500">Today</p>
                </div>
              </CardContent>
            </Card>
          </motion.div>

          {/* 5. Adherence Value Today */}
          <motion.div
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ delay: 0.3 }}
            whileHover={{ scale: 1.05 }}
          >
            <Card>
              <CardContent className="p-4">
                <div className="flex flex-col items-center text-center">
                  <TrendingUp className="w-8 h-8 text-purple-500 mb-2" />
                  <p className="text-xs text-gray-600 mb-1">Adherence</p>
                  <p className="text-2xl font-bold text-gray-800">
                    {metrics?.adherence_value_today !== null ? `${metrics.adherence_value_today.toFixed(0)}%` : '—'}
                  </p>
                  <p className="text-xs text-gray-500">Today</p>
                </div>
              </CardContent>
            </Card>
          </motion.div>

          {/* 6. Consistency Score */}
          <motion.div
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ delay: 0.35 }}
            whileHover={{ scale: 1.05 }}
          >
            <Card>
              <CardContent className="p-4">
                <div className="flex flex-col items-center text-center">
                  <Zap className="w-8 h-8 text-yellow-500 mb-2" />
                  <p className="text-xs text-gray-600 mb-1">Consistency</p>
                  <p className="text-2xl font-bold text-gray-800">
                    {metrics?.consistency_score.toFixed(1) || '0.0'}
                  </p>
                  <p className="text-xs text-gray-500">/10</p>
                </div>
              </CardContent>
            </Card>
          </motion.div>

          {/* 7. Wellness Score */}
          <motion.div
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ delay: 0.4 }}
            whileHover={{ scale: 1.05 }}
          >
            <Card className="border-2 border-purple-200 bg-gradient-to-br from-purple-50 to-white">
              <CardContent className="p-4">
                <div className="flex flex-col items-center text-center">
                  <div className="w-8 h-8 rounded-full bg-gradient-to-br from-purple-400 to-blue-500 flex items-center justify-center mb-2">
                    <span className="text-white text-xs font-bold">★</span>
                  </div>
                  <p className="text-xs text-gray-600 mb-1">Wellness</p>
                  <p className="text-2xl font-bold text-purple-700">
                    {metrics?.wellness_score !== null ? metrics.wellness_score.toFixed(1) : '—'}
                  </p>
                  <p className="text-xs text-gray-500">/10</p>
                </div>
              </CardContent>
            </Card>
          </motion.div>
        </div>

        {/* Graph 1: Emotion Trends Over Time */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.5 }}
          className="mb-6"
        >
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Heart className="w-5 h-5 text-pink-500" />
                Emotion Trends Over Time
              </CardTitle>
              <p className="text-sm text-gray-600">
                Positive, negative, and neutral emotions tracked daily
              </p>
            </CardHeader>
            <CardContent>
              {emotionTrends.length > 0 ? (
                <ResponsiveContainer width="100%" height={300}>
                  <AreaChart data={formatEmotionTrendsData()}>
                    <defs>
                      <linearGradient id="colorPositive" x1="0" y1="0" x2="0" y2="1">
                        <stop offset="5%" stopColor="#10b981" stopOpacity={0.8} />
                        <stop offset="95%" stopColor="#10b981" stopOpacity={0} />
                      </linearGradient>
                      <linearGradient id="colorNegative" x1="0" y1="0" x2="0" y2="1">
                        <stop offset="5%" stopColor="#ef4444" stopOpacity={0.8} />
                        <stop offset="95%" stopColor="#ef4444" stopOpacity={0} />
                      </linearGradient>
                      <linearGradient id="colorNeutral" x1="0" y1="0" x2="0" y2="1">
                        <stop offset="5%" stopColor="#6b7280" stopOpacity={0.8} />
                        <stop offset="95%" stopColor="#6b7280" stopOpacity={0} />
                      </linearGradient>
                    </defs>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="date" />
                    <YAxis />
                    <Tooltip />
                    <Legend />
                    <Area
                      type="monotone"
                      dataKey="positive"
                      stroke="#10b981"
                      fillOpacity={1}
                      fill="url(#colorPositive)"
                      name="Positive"
                    />
                    <Area
                      type="monotone"
                      dataKey="negative"
                      stroke="#ef4444"
                      fillOpacity={1}
                      fill="url(#colorNegative)"
                      name="Negative"
                    />
                    <Area
                      type="monotone"
                      dataKey="neutral"
                      stroke="#6b7280"
                      fillOpacity={1}
                      fill="url(#colorNeutral)"
                      name="Neutral"
                    />
                  </AreaChart>
                </ResponsiveContainer>
              ) : (
                <div className="flex items-center justify-center h-[300px] text-gray-500">
                  <div className="text-center">
                    <Heart className="w-12 h-12 mx-auto mb-2 opacity-30" />
                    <p>No emotion data available yet</p>
                    <p className="text-sm mt-1">Start chatting to track your emotions</p>
                  </div>
                </div>
              )}
            </CardContent>
          </Card>
        </motion.div>

        {/* Graph 2: Wellness Score Over Time */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.6 }}
          className="mb-6"
        >
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <TrendingUp className="w-5 h-5 text-purple-500" />
                Wellness Score Over Time
              </CardTitle>
              <p className="text-sm text-gray-600">
                Comprehensive wellness score calculated daily from mood, stress, adherence, and consistency
              </p>
            </CardHeader>
            <CardContent>
              {wellnessTrend.length > 0 ? (
                <ResponsiveContainer width="100%" height={300}>
                  <LineChart data={formatWellnessTrendData()}>
                    <defs>
                      <linearGradient id="colorWellness" x1="0" y1="0" x2="0" y2="1">
                        <stop offset="5%" stopColor="#8b5cf6" stopOpacity={0.8} />
                        <stop offset="95%" stopColor="#8b5cf6" stopOpacity={0.2} />
                      </linearGradient>
                    </defs>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="date" />
                    <YAxis domain={[0, 10]} />
                    <Tooltip />
                    <Legend />
                    <Line
                      type="monotone"
                      dataKey="score"
                      stroke="#8b5cf6"
                      strokeWidth={3}
                      dot={{ fill: '#8b5cf6', r: 4 }}
                      name="Wellness Score"
                    />
                  </LineChart>
                </ResponsiveContainer>
              ) : (
                <div className="flex items-center justify-center h-[300px] text-gray-500">
                  <div className="text-center">
                    <TrendingUp className="w-12 h-12 mx-auto mb-2 opacity-30" />
                    <p>No wellness data available yet</p>
                    <p className="text-sm mt-1">Data will appear as you use the app</p>
                  </div>
                </div>
              )}
            </CardContent>
          </Card>
        </motion.div>

        {/* Graph 3: Recommendation Adherence Over Time */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.7 }}
          className="mb-6"
        >
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Target className="w-5 h-5 text-blue-500" />
                Recommendation Adherence Over Time
              </CardTitle>
              <p className="text-sm text-gray-600">
                Percentage of daily recommendations completed
              </p>
            </CardHeader>
            <CardContent>
              {adherenceTrend.length > 0 && adherenceTrend.some(item => item.adherence_percentage !== null) ? (
                <ResponsiveContainer width="100%" height={300}>
                  <BarChart data={formatAdherenceTrendData()}>
                    <defs>
                      <linearGradient id="colorAdherence" x1="0" y1="0" x2="0" y2="1">
                        <stop offset="5%" stopColor="#3b82f6" stopOpacity={0.9} />
                        <stop offset="95%" stopColor="#3b82f6" stopOpacity={0.6} />
                      </linearGradient>
                    </defs>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="date" />
                    <YAxis domain={[0, 100]} />
                    <Tooltip
                      formatter={(value: any, name: string) => {
                        if (name === 'adherence') return [`${value}%`, 'Adherence'];
                        return [value, name];
                      }}
                    />
                    <Legend />
                    <Bar dataKey="adherence" fill="url(#colorAdherence)" name="Adherence %" radius={[8, 8, 0, 0]} />
                  </BarChart>
                </ResponsiveContainer>
              ) : (
                <div className="flex items-center justify-center h-[300px] text-gray-500">
                  <div className="text-center">
                    <Target className="w-12 h-12 mx-auto mb-2 opacity-30" />
                    <p>No recommendation data available yet</p>
                    <p className="text-sm mt-1">Complete recommendations to see your adherence trend</p>
                  </div>
                </div>
              )}
            </CardContent>
          </Card>
        </motion.div>

        {/* Preserved Sections */}
        <div className="grid md:grid-cols-2 gap-6 mb-6">
          {/* Dosha Assessment & Retake */}
          <motion.div
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: 0.8 }}
          >
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center justify-between">
                  <span>Dosha Balance</span>
                  <Button
                    size="sm"
                    variant="outline"
                    onClick={() => onNavigate('dosha')}
                    className="flex items-center gap-2"
                  >
                    <RotateCcw className="w-4 h-4" />
                    Retake Quiz
                  </Button>
                </CardTitle>
              </CardHeader>
              <CardContent>
                {doshaAssessment ? (
                  <div className="space-y-4">
                    {/* Vata */}
                    <div className="space-y-2">
                      <div className="flex items-center justify-between">
                        <div className="flex items-center gap-2">
                          <div className="p-2 bg-gradient-to-br from-blue-400 via-cyan-400 to-blue-500 rounded-lg">
                            <Wind className="w-4 h-4 text-white" />
                          </div>
                          <span className="text-sm font-medium text-gray-700">Vata (Air + Space)</span>
                        </div>
                        <span className="text-lg font-bold text-blue-600">
                          {Math.round(doshaAssessment.vata_score)}%
                        </span>
                      </div>
                      <div className="w-full bg-gray-200 rounded-full h-2">
                        <motion.div
                          initial={{ width: 0 }}
                          animate={{ width: `${doshaAssessment.vata_score}%` }}
                          transition={{ duration: 1, delay: 0.9 }}
                          className="h-2 rounded-full bg-gradient-to-r from-blue-400 via-cyan-400 to-blue-500"
                        />
                      </div>
                    </div>

                    {/* Pitta */}
                    <div className="space-y-2">
                      <div className="flex items-center justify-between">
                        <div className="flex items-center gap-2">
                          <div className="p-2 bg-gradient-to-br from-orange-400 via-red-400 to-pink-500 rounded-lg">
                            <Flame className="w-4 h-4 text-white" />
                          </div>
                          <span className="text-sm font-medium text-gray-700">Pitta (Fire + Water)</span>
                        </div>
                        <span className="text-lg font-bold text-orange-600">
                          {Math.round(doshaAssessment.pitta_score)}%
                        </span>
                      </div>
                      <div className="w-full bg-gray-200 rounded-full h-2">
                        <motion.div
                          initial={{ width: 0 }}
                          animate={{ width: `${doshaAssessment.pitta_score}%` }}
                          transition={{ duration: 1, delay: 1.0 }}
                          className="h-2 rounded-full bg-gradient-to-r from-orange-400 via-red-400 to-pink-500"
                        />
                      </div>
                    </div>

                    {/* Kapha */}
                    <div className="space-y-2">
                      <div className="flex items-center justify-between">
                        <div className="flex items-center gap-2">
                          <div className="p-2 bg-gradient-to-br from-green-400 via-emerald-400 to-teal-500 rounded-lg">
                            <Droplet className="w-4 h-4 text-white" />
                          </div>
                          <span className="text-sm font-medium text-gray-700">Kapha (Earth + Water)</span>
                        </div>
                        <span className="text-lg font-bold text-green-600">
                          {Math.round(doshaAssessment.kapha_score)}%
                        </span>
                      </div>
                      <div className="w-full bg-gray-200 rounded-full h-2">
                        <motion.div
                          initial={{ width: 0 }}
                          animate={{ width: `${doshaAssessment.kapha_score}%` }}
                          transition={{ duration: 1, delay: 1.1 }}
                          className="h-2 rounded-full bg-gradient-to-r from-green-400 via-emerald-400 to-teal-500"
                        />
                      </div>
                    </div>

                    <div className="mt-4 pt-4 border-t border-gray-200">
                      <p className="text-sm text-gray-600 text-center">
                        Your dominant dosha is{' '}
                        <span className="font-semibold text-purple-600">
                          {doshaAssessment.dominant_dosha.charAt(0).toUpperCase()}{doshaAssessment.dominant_dosha.slice(1)}
                        </span>
                      </p>
                      {doshaAssessment.assessment_date && (
                        <p className="text-xs text-gray-500 text-center mt-1">
                          Last assessed: {new Date(doshaAssessment.assessment_date).toLocaleDateString()}
                        </p>
                      )}
                    </div>
                  </div>
                ) : (
                  <div className="text-center py-8">
                    <p className="text-gray-600 mb-4">No dosha assessment found</p>
                    <Button onClick={() => onNavigate('dosha')}>
                      Take Dosha Quiz
                    </Button>
                  </div>
                )}
              </CardContent>
            </Card>
          </motion.div>

          {/* Wellness Dimensions (Preserved) */}
          <motion.div
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: 0.9 }}
          >
            <Card>
              <CardHeader>
                <CardTitle>Wellness Dimensions</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                {wellnessData.map((item, index) => (
                  <motion.div
                    key={item.dimension}
                    initial={{ opacity: 0, x: -20 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ delay: 1.0 + index * 0.05 }}
                  >
                    <div className="flex items-center justify-between mb-2">
                      <span className="text-sm text-gray-700">{item.dimension}</span>
                      <span className="text-sm text-purple-700">{item.score}%</span>
                    </div>
                    <div className="h-2 bg-gray-200 rounded-full overflow-hidden">
                      <motion.div
                        className="h-full bg-gradient-to-r from-purple-500 to-blue-500"
                        initial={{ width: 0 }}
                        animate={{ width: `${item.score}%` }}
                        transition={{ duration: 1, delay: 1.1 + index * 0.05 }}
                      />
                    </div>
                  </motion.div>
                ))}
              </CardContent>
            </Card>
          </motion.div>
        </div>
      </div>
    </div>
  );
}
