import { useState, useEffect } from 'react';
import { motion } from 'motion/react';
import { TrendingUp, Download, Award, Calendar, Target } from 'lucide-react';
import { Navigation } from './Navigation';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { Button } from './ui/button';
import { Badge } from './ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from './ui/tabs';
import { Dialog, DialogContent, DialogHeader, DialogTitle } from './ui/dialog';
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

  // Analytics state (fetched from backend) with fallbacks to mock data
  const [analytics, setAnalytics] = useState<AnalyticsData | null>(null);
  const [loadingAnalytics, setLoadingAnalytics] = useState<boolean>(false);

  // Mock fallback data for quick visualization when analytics not yet available
  const weeklyMoodFallback = [
    { date: 'Mon', mood: 7, stress: 4, energy: 6, balance: 7 },
    { date: 'Tue', mood: 6, stress: 5, energy: 5, balance: 6 },
    { date: 'Wed', mood: 8, stress: 3, energy: 8, balance: 8 },
    { date: 'Thu', mood: 5, stress: 6, energy: 4, balance: 5 },
    { date: 'Fri', mood: 9, stress: 2, energy: 9, balance: 9 },
    { date: 'Sat', mood: 8, stress: 3, energy: 7, balance: 8 },
    { date: 'Sun', mood: 7, stress: 4, energy: 6, balance: 7 },
  ];

  const monthlyMoodFallback = [
    { date: 'Week 1', mood: 6.5, stress: 4.5, energy: 6, balance: 6.5 },
    { date: 'Week 2', mood: 7, stress: 4, energy: 6.5, balance: 7 },
    { date: 'Week 3', mood: 7.5, stress: 3.5, energy: 7, balance: 7.5 },
    { date: 'Week 4', mood: 8, stress: 3, energy: 7.5, balance: 8 },
  ];

  useEffect(() => {
    const loadAnalytics = async () => {
      try {
        setLoadingAnalytics(true);
        const data = await api.getAnalytics();
        setAnalytics(data);
      } catch (err) {
        console.warn('Failed to load analytics, using fallback data', err);
        setAnalytics(null);
      } finally {
        setLoadingAnalytics(false);
      }
    };

    loadAnalytics();
  }, []);

  // Transform analytics data for charts
  const getMoodTrendsData = () => {
    if (!analytics?.emotions?.emotions_over_time) {
      return timeframe === 'week' ? weeklyMoodFallback : monthlyMoodFallback;
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

  // Get key metrics from analytics
  const getKeyMetrics = () => {
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

  const wellnessData = analytics?.wearable_insights
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