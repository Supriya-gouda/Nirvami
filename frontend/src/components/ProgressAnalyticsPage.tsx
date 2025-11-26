import { useState, useEffect } from 'react';
import { motion } from 'motion/react';
import { TrendingUp, Download, Award, Calendar, Target } from 'lucide-react';
import { Navigation } from './Navigation';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { Button } from './ui/button';
import { Badge } from './ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from './ui/tabs';
import { Dialog, DialogContent, DialogHeader, DialogTitle } from './ui/dialog';
import { AuraHistory } from './AuraHistory';
import {
  LineChart,
  Line,
  AreaChart,
  Area,
  RadarChart,
  PolarGrid,
  PolarAngleAxis,
  PolarRadiusAxis,
  Radar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from 'recharts';
import type { PageType } from '../App';
import type { User } from '../types/api.types';
import api from '../services/api';
import type { AnalyticsData } from '../types/api.types';

interface ProgressAnalyticsPageProps {
  user: User | null;
  onNavigate: (page: PageType) => void;
  onLogout?: () => void;
  onOpenNotifications?: () => void;
}

export function ProgressAnalyticsPage({ user, onNavigate, onLogout, onOpenNotifications }: ProgressAnalyticsPageProps) {
  const [showAchievement, setShowAchievement] = useState(false);
  const [timeframe, setTimeframe] = useState<'week' | 'month'>('week');

  // Analytics state (fetched from backend)
  const [analytics, setAnalytics] = useState<AnalyticsData | null>(null);
  const [loadingAnalytics, setLoadingAnalytics] = useState<boolean>(false);
  
  // Wellness scores state
  const [wellnessHistory, setWellnessHistory] = useState<any[]>([]);
  const [loadingWellness, setLoadingWellness] = useState<boolean>(false);
  
  // Meal correlations state
  const [mealCorrelations, setMealCorrelations] = useState<{
    mood_boosting_foods: Array<{ food: string; impact_score: number; occurrences: number }>;
    foods_to_watch: Array<{ food: string; impact_score: number; occurrences: number }>;
    total_foods_analyzed: number;
  } | null>(null);
  const [loadingMealCorrelations, setLoadingMealCorrelations] = useState<boolean>(false);
  const [analyzingCorrelations, setAnalyzingCorrelations] = useState<boolean>(false);

  useEffect(() => {
    const loadAnalytics = async () => {
      try {
        setLoadingAnalytics(true);
        const data = await api.getAnalytics();
        setAnalytics(data);
      } catch (err) {
        console.warn('Failed to load analytics', err);
        setAnalytics(null);
      } finally {
        setLoadingAnalytics(false);
      }
    };

    const loadWellnessData = async () => {
      try {
        setLoadingWellness(true);
        const history = await api.getWellnessHistory({ days: 30 });
        setWellnessHistory(history || []);
      } catch (err) {
        console.warn('Failed to load wellness history', err);
        setWellnessHistory([]);
      } finally {
        setLoadingWellness(false);
      }
    };
    
    const loadMealCorrelations = async () => {
      try {
        setLoadingMealCorrelations(true);
        const correlations = await api.getMealCorrelations();
        setMealCorrelations(correlations);
      } catch (err) {
        console.warn('Failed to load meal correlations', err);
        setMealCorrelations(null);
      } finally {
        setLoadingMealCorrelations(false);
      }
    };

    const handleAnalyzeCorrelations = async () => {
      try {
        setAnalyzingCorrelations(true);
        await api.analyzeMealCorrelations();
        // Reload correlations after analysis
        await loadMealCorrelations();
      } catch (err) {
        console.error('Failed to analyze correlations', err);
      } finally {
        setAnalyzingCorrelations(false);
      }
    };

    loadAnalytics();
    loadWellnessData();
    loadMealCorrelations();
  }, []);

  // Transform analytics data for charts
  const getMoodTrendsData = () => {
    if (!analytics?.emotions?.emotions_over_time || analytics.emotions.emotions_over_time.length === 0) {
      return [];
    }

    const emotionsData = analytics.emotions.emotions_over_time;
    const recentData = timeframe === 'week'
      ? emotionsData.slice(-7)
      : emotionsData.slice(-30);

    return recentData.map((entry: any) => {
      const emotions = entry.emotions || {};
      const moodScore = Object.values(emotions).reduce((sum: number, val: any) => sum + (val || 0), 0) / Math.max(Object.keys(emotions).length, 1);
      const stressScore = (emotions.anxiety || 0) + (emotions.fear || 0) + (emotions.anger || 0);

      return {
        date: new Date(entry.date).toLocaleDateString('en-US', { weekday: 'short' }),
        mood: Number(moodScore.toFixed(1)),
        stress: Number(stressScore.toFixed(1)),
        energy: entry.valence || 5,
        balance: entry.arousal || 5
      };
    });
  };

  // Get key metrics from analytics and wellness scores
  const getKeyMetrics = () => {
    // Try to use real wellness scores first
    if (wellnessHistory && wellnessHistory.length > 0) {
      const recent = wellnessHistory.slice(0, 7);
      const previous = wellnessHistory.slice(7, 14);
      
      const avgScore = (scores: any[]) => {
        if (!scores.length) return 0;
        return scores.reduce((sum, s) => sum + (s.overall_score || 0), 0) / scores.length;
      };
      
      const recentOverall = avgScore(recent);
      const previousOverall = avgScore(previous);
      const overallChange = previousOverall ? ((recentOverall - previousOverall) / previousOverall) * 100 : 0;
      
      const recentEmotion = recent.length > 0 ? recent[0].emotion_score || 0 : 0;
      const recentEnergy = recent.length > 0 ? recent[0].wearable_score || 0 : 0;
      const recentBalance = recent.length > 0 ? recent[0].engagement_score || 0 : 0;
      
      return {
        avgMood: Number(recentEmotion.toFixed(1)),
        moodChange: Number(overallChange.toFixed(0)),
        stressLevel: Number((100 - recentEmotion).toFixed(1)) / 10,
        stressChange: -Number(overallChange.toFixed(0)),
        energy: Number((recentEnergy / 10).toFixed(1)),
        energyChange: 18,
        balance: Number((recentBalance / 10).toFixed(1)),
        balanceChange: Number(overallChange.toFixed(0))
      };
    }
    
    // Fallback to analytics-based calculation
    if (!analytics) {
      return {
        avgMood: 7.4,
        moodChange: 12,
        stressLevel: 3.6,
        stressChange: -23,
        energy: 7.1,
        energyChange: 18,
        balance: 7.5,
        balanceChange: 15
      };
    }

    const emotions = analytics.emotions?.emotions_over_time || [];
    const recent = emotions.slice(-7);
    const previous = emotions.slice(-14, -7);

    const calcAvg = (data: any[], key: string) => {
      if (!data.length) return 0;
      return data.reduce((sum, item) => sum + (item[key] || 0), 0) / data.length;
    };

    const recentAvgMood = calcAvg(recent, 'valence') * 10;
    const previousAvgMood = calcAvg(previous, 'valence') * 10;
    const moodChange = previousAvgMood ? ((recentAvgMood - previousAvgMood) / previousAvgMood) * 100 : 0;

    const recentStress = calcAvg(recent, 'arousal');
    const previousStress = calcAvg(previous, 'arousal');
    const stressChange = previousStress ? ((recentStress - previousStress) / previousStress) * 100 : 0;

    return {
      avgMood: Number(recentAvgMood.toFixed(1)),
      moodChange: Number(moodChange.toFixed(0)),
      stressLevel: Number(recentStress.toFixed(1)),
      stressChange: Number(stressChange.toFixed(0)),
      energy: Number((calcAvg(recent, 'valence') * 10).toFixed(1)),
      energyChange: 18,
      balance: Number((analytics.wellness_trend?.[0]?.score || 75) / 10).toFixed(1),
      balanceChange: 15
    };
  };

  // Dosha and wellness data - attempt to read from analytics, fallback to static
  const doshaData = analytics?.wellness_trend && analytics.wellness_trend.length >= 3
    ? [
      { aspect: 'Vata', current: analytics.wellness_trend[0]?.score ?? 60, optimal: 80 },
      { aspect: 'Pitta', current: analytics.wellness_trend[1]?.score ?? 50, optimal: 70 },
      { aspect: 'Kapha', current: analytics.wellness_trend[2]?.score ?? 55, optimal: 75 },
    ]
    : [
      { aspect: 'Vata', current: 65, optimal: 80 },
      { aspect: 'Pitta', current: 85, optimal: 70 },
      { aspect: 'Kapha', current: 70, optimal: 75 },
    ];

  // Use wellness scores for wellness radar chart data
  const wellnessData = wellnessHistory && wellnessHistory.length > 0 && wellnessHistory[0]
    ? [
      { dimension: 'Sleep', score: wellnessHistory[0].wearable_score || 70 },
      { dimension: 'Nutrition', score: analytics?.meal_patterns?.meals_logged ? Math.min(100, analytics.meal_patterns.meals_logged * 3) : 75 },
      { dimension: 'Exercise', score: wellnessHistory[0].wearable_score || 70 },
      { dimension: 'Mindfulness', score: wellnessHistory[0].emotion_score || 85 },
      { dimension: 'Social', score: 65 },
      { dimension: 'Purpose', score: wellnessHistory[0].engagement_score || 78 },
    ]
    : analytics?.wearable_insights
    ? [
      { dimension: 'Sleep', score: Math.min(100, (analytics.wearable_insights.average_sleep || 7) * 12.5) },
      { dimension: 'Nutrition', score: analytics.meal_patterns?.meals_logged ? Math.min(100, analytics.meal_patterns.meals_logged * 3) : 75 },
      { dimension: 'Exercise', score: analytics.wearable_insights.total_steps ? Math.min(100, (analytics.wearable_insights.total_steps / 10000) * 100) : 70 },
      { dimension: 'Mindfulness', score: analytics.emotions?.average_valence ? analytics.emotions.average_valence * 100 : 85 },
      { dimension: 'Social', score: 65 },
      { dimension: 'Purpose', score: analytics.wellness_trend?.[0]?.score || 78 },
    ]
    : [
      { dimension: 'Sleep', score: 80 },
      { dimension: 'Nutrition', score: 75 },
      { dimension: 'Exercise', score: 70 },
      { dimension: 'Mindfulness', score: 85 },
      { dimension: 'Social', score: 65 },
      { dimension: 'Purpose', score: 78 },
    ];

  // TODO: Create achievements table and fetch from backend
  // For now, using static data as achievements system not yet implemented in DB
  const achievements = [
    { id: 1, title: '7-Day Streak', desc: 'Logged daily for a week', emoji: '🔥', unlocked: true },
    { id: 2, title: 'Yoga Master', desc: 'Completed 20 yoga sessions', emoji: '🧘', unlocked: true },
    { id: 3, title: 'Balanced Mind', desc: 'Maintained low stress for 5 days', emoji: '🧠', unlocked: true },
    { id: 4, title: 'Early Bird', desc: 'Morning routine 10 times', emoji: '🌅', unlocked: false },
    { id: 5, title: 'Nutrition Pro', desc: 'Logged 30 balanced meals', emoji: '🥗', unlocked: false },
    { id: 6, title: 'Zen Master', desc: '100 meditation minutes', emoji: '☮️', unlocked: false },
  ];

  const metrics = getKeyMetrics();
  const moodTrendsData = getMoodTrendsData();

  const handleDownloadReport = () => {
    // Simulate PDF download
    alert('Your wellness report is being generated and will download shortly!');
  };

  return (
    <div className="min-h-screen">
      <Navigation currentPage="progress" onNavigate={onNavigate} onLogout={onLogout} user={user} onOpenNotifications={onOpenNotifications} />

      <div className="max-w-7xl mx-auto p-8">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="mb-8"
        >
          <div className="flex items-center justify-between">
            <div>
              <h1 className="mb-2">Progress & Analytics</h1>
              <p className="text-gray-600">Track your wellness journey</p>
            </div>
            <Button onClick={handleDownloadReport} className="bg-gradient-to-r from-purple-500 to-blue-500">
              <Download className="w-4 h-4 mr-2" />
              Download Report
            </Button>
          </div>
        </motion.div>

        {/* Key Metrics */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1 }}
          className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6"
        >
          {[
            { label: 'Avg Mood', value: metrics.avgMood, change: `${metrics.moodChange > 0 ? '+' : ''}${metrics.moodChange}%`, icon: '😊', color: 'from-yellow-400 to-orange-400', positive: metrics.moodChange > 0 },
            { label: 'Stress Level', value: metrics.stressLevel, change: `${metrics.stressChange > 0 ? '+' : ''}${metrics.stressChange}%`, icon: '🧘', color: 'from-green-400 to-teal-400', positive: metrics.stressChange < 0 },
            { label: 'Energy', value: metrics.energy, change: `${metrics.energyChange > 0 ? '+' : ''}${metrics.energyChange}%`, icon: '⚡', color: 'from-blue-400 to-purple-400', positive: metrics.energyChange > 0 },
            { label: 'Balance', value: metrics.balance, change: `${metrics.balanceChange > 0 ? '+' : ''}${metrics.balanceChange}%`, icon: '☯️', color: 'from-pink-400 to-purple-400', positive: metrics.balanceChange > 0 },
          ].map((metric, index) => (
            <motion.div
              key={metric.label}
              initial={{ opacity: 0, scale: 0.9 }}
              animate={{ opacity: 1, scale: 1 }}
              transition={{ delay: 0.2 + index * 0.1 }}
              whileHover={{ scale: 1.05 }}
            >
              <Card>
                <CardContent className="p-6">
                  <div className={`w-12 h-12 rounded-full bg-gradient-to-br ${metric.color} flex items-center justify-center text-2xl mb-3`}>
                    {metric.icon}
                  </div>
                  <p className="text-sm text-gray-600 mb-1">{metric.label}</p>
                  <div className="flex items-end justify-between">
                    <p className="text-2xl">{metric.value}</p>
                    <Badge variant="outline" className={metric.positive ? "text-green-600 border-green-600" : "text-red-600 border-red-600"}>
                      {metric.change}
                    </Badge>
                  </div>
                </CardContent>
              </Card>
            </motion.div>
          ))}
        </motion.div>

        {/* Mood Trends */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.3 }}
          className="mb-6"
        >
          <Card>
            <CardHeader>
              <div className="flex items-center justify-between">
                <CardTitle className="flex items-center gap-2">
                  <TrendingUp className="w-5 h-5 text-purple-600" />
                  Mood Trends
                </CardTitle>
                <Tabs value={timeframe} onValueChange={(v) => setTimeframe(v as 'week' | 'month')}>
                  <TabsList>
                    <TabsTrigger value="week">Week</TabsTrigger>
                    <TabsTrigger value="month">Month</TabsTrigger>
                  </TabsList>
                </Tabs>
              </div>
            </CardHeader>
            <CardContent>
              <ResponsiveContainer width="100%" height={300}>
                <AreaChart data={moodTrendsData}>
                  <defs>
                    <linearGradient id="colorMood" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor="#8b5cf6" stopOpacity={0.8} />
                      <stop offset="95%" stopColor="#8b5cf6" stopOpacity={0} />
                    </linearGradient>
                    <linearGradient id="colorStress" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor="#ef4444" stopOpacity={0.8} />
                      <stop offset="95%" stopColor="#ef4444" stopOpacity={0} />
                    </linearGradient>
                  </defs>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="date" />
                  <YAxis />
                  <Tooltip />
                  <Legend />
                  <Area type="monotone" dataKey="mood" stroke="#8b5cf6" fillOpacity={1} fill="url(#colorMood)" name="Mood" />
                  <Area type="monotone" dataKey="stress" stroke="#ef4444" fillOpacity={1} fill="url(#colorStress)" name="Stress" />
                </AreaChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>
        </motion.div>

        <div className="grid md:grid-cols-2 gap-6 mb-6">
          {/* Dosha Balance */}
          <motion.div
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: 0.4 }}
          >
            <Card>
              <CardHeader>
                <CardTitle>Aura & Dosha Balance</CardTitle>
              </CardHeader>
              <CardContent>
                <ResponsiveContainer width="100%" height={300}>
                  <RadarChart data={doshaData}>
                    <PolarGrid />
                    <PolarAngleAxis dataKey="aspect" />
                    <PolarRadiusAxis angle={90} domain={[0, 100]} />
                    <Radar name="Current" dataKey="current" stroke="#8b5cf6" fill="#8b5cf6" fillOpacity={0.6} />
                    <Radar name="Optimal" dataKey="optimal" stroke="#3b82f6" fill="#3b82f6" fillOpacity={0.3} />
                    <Legend />
                  </RadarChart>
                </ResponsiveContainer>
                <p className="text-sm text-gray-600 mt-4 text-center">
                  Your Pitta is slightly elevated. Consider cooling foods and calming practices.
                </p>
              </CardContent>
            </Card>
          </motion.div>

          {/* Wellness Dimensions */}
          <motion.div
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: 0.5 }}
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
                    transition={{ delay: 0.6 + index * 0.05 }}
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
                        transition={{ duration: 1, delay: 0.7 + index * 0.05 }}
                      />
                    </div>
                  </motion.div>
                ))}
              </CardContent>
            </Card>
          </motion.div>
        </div>

        {/* Meal-Mood Correlations */}
        {mealCorrelations && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.55 }}
            className="mb-6"
          >
            <Card className="border-2 border-purple-200 bg-gradient-to-br from-purple-50 to-blue-50">
              <CardHeader>
                <div className="flex items-center justify-between">
                  <div>
                    <CardTitle className="flex items-center gap-2">
                      <span className="text-2xl">🍽️</span>
                      AI Health Insight: Food-Mood Connections
                    </CardTitle>
                    <p className="text-sm text-gray-600 mt-2">
                      {mealCorrelations.total_foods_analyzed > 0 
                        ? `Based on ${mealCorrelations.total_foods_analyzed} foods analyzed from your meal and emotion logs`
                        : 'Start logging meals and emotions to see personalized food-mood insights'
                      }
                    </p>
                  </div>
                  <Button 
                    onClick={handleAnalyzeCorrelations} 
                    disabled={analyzingCorrelations}
                    className="bg-purple-600 hover:bg-purple-700"
                  >
                    {analyzingCorrelations ? 'Analyzing...' : 'Refresh Analysis'}
                  </Button>
                </div>
              </CardHeader>
              <CardContent>
                {mealCorrelations.total_foods_analyzed === 0 ? (
                  <div className="text-center py-8 space-y-4">
                    <div className="text-6xl">🍽️💭</div>
                    <h3 className="text-lg font-semibold text-gray-700">No Correlation Data Yet</h3>
                    <p className="text-gray-600 max-w-md mx-auto">
                      Start logging your meals and tracking your emotions to discover which foods positively 
                      or negatively affect your mood. We analyze patterns between what you eat and how you feel 
                      1-4 hours after meals.
                    </p>
                    <Button 
                      onClick={handleAnalyzeCorrelations} 
                      disabled={analyzingCorrelations}
                      className="bg-purple-600 hover:bg-purple-700"
                    >
                      {analyzingCorrelations ? 'Analyzing...' : 'Run Analysis Now'}
                    </Button>
                  </div>
                ) : (
                  <div>
                    <div className="grid md:grid-cols-2 gap-6">
                  {/* Mood Boosting Foods */}
                  <div className="space-y-3">
                    <h3 className="text-lg font-semibold text-green-700 flex items-center gap-2">
                      <span className="text-2xl">✨</span>
                      Top Foods That Boost Your Mood
                    </h3>
                    {mealCorrelations.mood_boosting_foods.length > 0 ? (
                      <div className="space-y-2">
                        {mealCorrelations.mood_boosting_foods.map((food, index) => (
                          <motion.div
                            key={food.food}
                            initial={{ opacity: 0, x: -20 }}
                            animate={{ opacity: 1, x: 0 }}
                            transition={{ delay: 0.6 + index * 0.1 }}
                            className="p-3 bg-white rounded-lg border border-green-200 hover:shadow-md transition-shadow"
                          >
                            <div className="flex items-center justify-between">
                              <div className="flex-1">
                                <p className="font-medium text-gray-800">{food.food}</p>
                                <p className="text-xs text-gray-500">
                                  {food.occurrences} meal{food.occurrences !== 1 ? 's' : ''} logged
                                </p>
                              </div>
                              <div className="flex items-center gap-2">
                                <Badge className="bg-green-100 text-green-700 border-green-300">
                                  +{(food.impact_score * 100).toFixed(0)}%
                                </Badge>
                                {index === 0 && <span className="text-2xl">👑</span>}
                              </div>
                            </div>
                          </motion.div>
                        ))}
                      </div>
                    ) : (
                      <p className="text-sm text-gray-500 italic">
                        Log more meals to discover mood-boosting foods
                      </p>
                    )}
                  </div>

                  {/* Foods to Watch */}
                  <div className="space-y-3">
                    <h3 className="text-lg font-semibold text-orange-700 flex items-center gap-2">
                      <span className="text-2xl">⚠️</span>
                      Foods to Watch
                    </h3>
                    {mealCorrelations.foods_to_watch.length > 0 ? (
                      <div className="space-y-2">
                        {mealCorrelations.foods_to_watch.map((food, index) => (
                          <motion.div
                            key={food.food}
                            initial={{ opacity: 0, x: 20 }}
                            animate={{ opacity: 1, x: 0 }}
                            transition={{ delay: 0.6 + index * 0.1 }}
                            className="p-3 bg-white rounded-lg border border-orange-200 hover:shadow-md transition-shadow"
                          >
                            <div className="flex items-center justify-between">
                              <div className="flex-1">
                                <p className="font-medium text-gray-800">{food.food}</p>
                                <p className="text-xs text-gray-500">
                                  {food.occurrences} meal{food.occurrences !== 1 ? 's' : ''} logged
                                </p>
                              </div>
                              <Badge className="bg-orange-100 text-orange-700 border-orange-300">
                                {(food.impact_score * 100).toFixed(0)}%
                              </Badge>
                            </div>
                          </motion.div>
                        ))}
                      </div>
                    ) : (
                      <p className="text-sm text-gray-500 italic">
                        No concerning patterns detected
                      </p>
                    )}
                  </div>
                </div>
                
                <div className="mt-4 p-3 bg-purple-100 rounded-lg border border-purple-200">
                  <p className="text-sm text-purple-800">
                    💡 <strong>Pro tip:</strong> These insights are based on the correlation between what you eat and how you feel 1-4 hours after meals. 
                    Keep logging meals and emotions to get more accurate personalized insights!
                  </p>
                </div>
                  </div>
                )}
              </CardContent>
            </Card>
          </motion.div>
        )}

        {/* Achievements */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.6 }}
          className="mb-6"
        >
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Award className="w-5 h-5 text-yellow-600" />
                Achievements
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-2 md:grid-cols-6 gap-4">
                {achievements.map((achievement, index) => (
                  <motion.div
                    key={achievement.id}
                    initial={{ opacity: 0, scale: 0.8 }}
                    animate={{ opacity: 1, scale: 1 }}
                    transition={{ delay: 0.7 + index * 0.05 }}
                    whileHover={{ scale: achievement.unlocked ? 1.1 : 1, rotate: achievement.unlocked ? 5 : 0 }}
                    onClick={() => achievement.unlocked && setShowAchievement(true)}
                    className={`p-4 rounded-xl text-center cursor-pointer ${achievement.unlocked
                        ? 'bg-gradient-to-br from-yellow-50 to-orange-50 border-2 border-yellow-400'
                        : 'bg-gray-100 opacity-50'
                      }`}
                  >
                    <div className="text-4xl mb-2">{achievement.emoji}</div>
                    <p className="text-xs text-gray-700">{achievement.title}</p>
                  </motion.div>
                ))}
              </div>
            </CardContent>
          </Card>
        </motion.div>

        {/* Aura History */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.7 }}
          className="mb-6"
        >
          <AuraHistory days={30} showTitle={true} compact={false} />
        </motion.div>
      </div>

      {/* Achievement Dialog */}
      <Dialog open={showAchievement} onOpenChange={setShowAchievement}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle className="text-center">Achievement Unlocked! 🎉</DialogTitle>
          </DialogHeader>
          <div className="flex flex-col items-center py-6">
            <motion.div
              className="text-8xl mb-4"
              initial={{ scale: 0, rotate: -180 }}
              animate={{ scale: 1, rotate: 0 }}
              transition={{ type: 'spring', duration: 0.8 }}
            >
              🔥
            </motion.div>
            <h3 className="text-purple-900 mb-2">7-Day Streak</h3>
            <p className="text-sm text-gray-600 text-center mb-4">
              You've successfully logged your wellness data for 7 consecutive days!
            </p>
            <Badge className="bg-gradient-to-r from-yellow-400 to-orange-400">
              +50 Wellness Points
            </Badge>
          </div>
        </DialogContent>
      </Dialog>
    </div>
  );
}