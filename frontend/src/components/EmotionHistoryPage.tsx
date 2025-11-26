import { useEffect, useState } from 'react';
import { motion } from 'motion/react';
import { 
  Calendar as CalendarIcon, 
  TrendingUp, 
  BarChart3, 
  Heart,
  Smile,
  Frown,
  Meh,
  Sun,
  Cloud,
  CloudRain,
  Filter
} from 'lucide-react';
import { Navigation } from './Navigation';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from './ui/card';
import { Button } from './ui/button';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from './ui/select';
import {
  BarChart,
  Bar,
  AreaChart,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  Cell,
} from 'recharts';
import api from '../services/api';
import type { PageType } from '../App';
import type { User, EmotionAggregate, EmotionLog } from '../types/api.types';

interface EmotionHistoryPageProps {
  user: User | null;
  onNavigate: (page: PageType) => void;
  onLogout?: () => void;
  onOpenNotifications?: () => void;
}

// Emotion color mapping
const EMOTION_COLORS: Record<string, string> = {
  joy: '#10b981',      // green
  happiness: '#10b981',
  calm: '#3b82f6',     // blue
  neutral: '#6b7280',  // gray
  sadness: '#8b5cf6',  // purple
  anxiety: '#f59e0b',  // amber
  stress: '#ef4444',   // red
  anger: '#dc2626',    // dark red
  fear: '#a855f7',     // violet
};

const getEmotionIcon = (emotion: string) => {
  const icons: Record<string, any> = {
    joy: Smile,
    happiness: Smile,
    calm: Sun,
    neutral: Meh,
    sadness: Frown,
    anxiety: Cloud,
    stress: CloudRain,
    anger: CloudRain,
    fear: CloudRain,
  };
  return icons[emotion.toLowerCase()] || Meh;
};

const getEmotionColor = (emotion: string) => {
  return EMOTION_COLORS[emotion.toLowerCase()] || '#6b7280';
};

export function EmotionHistoryPage({
  user,
  onNavigate,
  onLogout,
  onOpenNotifications,
}: EmotionHistoryPageProps) {
  const [aggregates, setAggregates] = useState<EmotionAggregate[]>([]);
  const [_emotionLogs, _setEmotionLogs] = useState<EmotionLog[]>([]);
  const [loading, setLoading] = useState(true);
  const [timeRange, setTimeRange] = useState<'7' | '30' | '90'>('30');
  const [selectedMonth, setSelectedMonth] = useState(new Date());

  useEffect(() => {
    loadData();
  }, [timeRange]);

  const loadData = async () => {
    try {
      setLoading(true);
      const days = parseInt(timeRange);
      const startDate = new Date();
      startDate.setDate(startDate.getDate() - days);
      
      // Load aggregates and individual logs
      const [aggregatesData, logsData] = await Promise.all([
        api.getEmotionAggregates(days),
        api.getEmotionLogs({ start_date: startDate.toISOString().split('T')[0] })
      ]);

      setAggregates(aggregatesData);
      _setEmotionLogs(logsData);
    } catch (err) {
      console.error('Failed to load emotion data:', err);
    } finally {
      setLoading(false);
    }
  };

  // Transform aggregates for line chart
  const getMoodTrendData = () => {
    if (!aggregates || aggregates.length === 0) return [];

    return aggregates
      .slice()
      .reverse()
      .map((agg) => {
        const date = new Date(agg.date);
        const emotionDist = agg.emotion_distribution || {};
        
        // Calculate positivity score (0-100)
        const positiveEmotions = (emotionDist.joy || 0) + (emotionDist.calm || 0) + (emotionDist.happiness || 0);
        const negativeEmotions = (emotionDist.sadness || 0) + (emotionDist.anxiety || 0) + (emotionDist.stress || 0) + (emotionDist.anger || 0);
        const neutralEmotions = emotionDist.neutral || 0;
        
        const total = positiveEmotions + negativeEmotions + neutralEmotions || 1;
        const moodScore = ((positiveEmotions - negativeEmotions) / total) * 50 + 50; // Scale to 0-100

        return {
          date: date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' }),
          mood: Math.round(moodScore),
          positive: Math.round(positiveEmotions * 100),
          negative: Math.round(negativeEmotions * 100),
          entries: agg.total_entries,
        };
      });
  };

  // Get emotion distribution for bar chart
  const getEmotionDistribution = () => {
    if (!aggregates || aggregates.length === 0) return [];

    const emotionTotals: Record<string, number> = {};
    
    aggregates.forEach((agg) => {
      const dist = agg.emotion_distribution || {};
      Object.entries(dist).forEach(([emotion, percentage]) => {
        emotionTotals[emotion] = (emotionTotals[emotion] || 0) + (percentage as number);
      });
    });

    return Object.entries(emotionTotals)
      .map(([emotion, total]) => ({
        emotion: emotion.charAt(0).toUpperCase() + emotion.slice(1),
        count: Math.round(total * 100),
        fill: getEmotionColor(emotion),
      }))
      .sort((a, b) => b.count - a.count)
      .slice(0, 8); // Top 8 emotions
  };

  // Calendar view data
  const getCalendarData = () => {
    const startOfMonth = new Date(selectedMonth.getFullYear(), selectedMonth.getMonth(), 1);
    const endOfMonth = new Date(selectedMonth.getFullYear(), selectedMonth.getMonth() + 1, 0);
    
    const days: any[] = [];
    
    // Add empty days for padding
    const startDay = startOfMonth.getDay();
    for (let i = 0; i < startDay; i++) {
      days.push({ empty: true });
    }
    
    // Add days with emotion data
    for (let day = 1; day <= endOfMonth.getDate(); day++) {
      const currentDate = new Date(selectedMonth.getFullYear(), selectedMonth.getMonth(), day);
      const dateStr = currentDate.toISOString().split('T')[0];
      
      const aggregate = aggregates.find(agg => agg.date === dateStr);
      
      days.push({
        day,
        date: currentDate,
        emotion: aggregate?.dominant_emotion,
        entries: aggregate?.total_entries || 0,
        color: aggregate ? getEmotionColor(aggregate.dominant_emotion) : undefined,
      });
    }
    
    return days;
  };

  // Summary stats
  const getSummaryStats = () => {
    if (!aggregates || aggregates.length === 0) {
      return {
        totalDays: 0,
        dominantEmotion: 'neutral',
        avgEntriesPerDay: 0,
        moodTrend: 'stable',
      };
    }

    const emotionCounts: Record<string, number> = {};
    let totalEntries = 0;

    aggregates.forEach((agg) => {
      const emotion = agg.dominant_emotion;
      emotionCounts[emotion] = (emotionCounts[emotion] || 0) + 1;
      totalEntries += agg.total_entries;
    });

    const dominantEmotion = Object.entries(emotionCounts)
      .sort((a, b) => b[1] - a[1])[0]?.[0] || 'neutral';

    // Calculate trend (comparing first half vs second half)
    const mid = Math.floor(aggregates.length / 2);
    const firstHalf = aggregates.slice(0, mid);
    const secondHalf = aggregates.slice(mid);

    const calcPositivity = (aggs: EmotionAggregate[]) => {
      let positive = 0, negative = 0;
      aggs.forEach(agg => {
        const dist = agg.emotion_distribution || {};
        positive += (dist.joy || 0) + (dist.calm || 0) + (dist.happiness || 0);
        negative += (dist.sadness || 0) + (dist.anxiety || 0) + (dist.stress || 0);
      });
      return positive - negative;
    };

    const firstPositivity = calcPositivity(firstHalf);
    const secondPositivity = calcPositivity(secondHalf);
    const moodTrend = secondPositivity > firstPositivity ? 'improving' : 
                      secondPositivity < firstPositivity ? 'declining' : 'stable';

    return {
      totalDays: aggregates.length,
      dominantEmotion,
      avgEntriesPerDay: Math.round(totalEntries / aggregates.length),
      moodTrend,
    };
  };

  const stats = getSummaryStats();
  const moodTrendData = getMoodTrendData();
  const emotionDistData = getEmotionDistribution();
  const calendarData = getCalendarData();

  const DominantEmotionIcon = getEmotionIcon(stats.dominantEmotion);

  return (
    <div className="min-h-screen bg-gradient-to-br from-purple-50 via-white to-pink-50">
      <Navigation
        currentPage="progress"
        onNavigate={onNavigate}
        onLogout={onLogout}
        onOpenNotifications={onOpenNotifications}
        user={user}
      />

      <div className="container max-w-7xl mx-auto px-4 py-8 mt-16">
        {/* Header */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="mb-8"
        >
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center gap-3">
              <Heart className="w-8 h-8 text-pink-600" />
              <div>
                <h1 className="text-3xl font-bold text-gray-900">Emotion Timeline</h1>
                <p className="text-gray-600">Track your emotional journey over time</p>
              </div>
            </div>

            <div className="flex items-center gap-3">
              <Select value={timeRange} onValueChange={(val: any) => setTimeRange(val)}>
                <SelectTrigger className="w-40">
                  <Filter className="w-4 h-4 mr-2" />
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="7">Last 7 Days</SelectItem>
                  <SelectItem value="30">Last 30 Days</SelectItem>
                  <SelectItem value="90">Last 90 Days</SelectItem>
                </SelectContent>
              </Select>
            </div>
          </div>
        </motion.div>

        {loading ? (
          <div className="text-center py-12">
            <p className="text-gray-500">Loading emotion data...</p>
          </div>
        ) : aggregates.length === 0 ? (
          <Card className="text-center py-12">
            <CardContent>
              <Heart className="w-16 h-16 text-gray-300 mx-auto mb-4" />
              <h3 className="text-lg font-semibold text-gray-700 mb-2">No Emotion Data Yet</h3>
              <p className="text-gray-500 mb-4">
                Start logging your emotions through chat or manual entry to see your emotional journey
              </p>
              <Button onClick={() => onNavigate('chatbot')}>
                Start Chatting
              </Button>
            </CardContent>
          </Card>
        ) : (
          <>
            {/* Summary Cards */}
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-8">
              <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.1 }}>
                <Card>
                  <CardContent className="pt-6">
                    <div className="flex items-center justify-between">
                      <div>
                        <p className="text-sm text-gray-600">Days Tracked</p>
                        <p className="text-3xl font-bold text-gray-900">{stats.totalDays}</p>
                      </div>
                      <CalendarIcon className="w-8 h-8 text-purple-600" />
                    </div>
                  </CardContent>
                </Card>
              </motion.div>

              <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.2 }}>
                <Card>
                  <CardContent className="pt-6">
                    <div className="flex items-center justify-between">
                      <div>
                        <p className="text-sm text-gray-600">Dominant Emotion</p>
                        <div className="flex items-center gap-2 mt-1">
                          <DominantEmotionIcon 
                            className="w-6 h-6" 
                            style={{ color: getEmotionColor(stats.dominantEmotion) }}
                          />
                          <p className="text-xl font-bold capitalize" style={{ color: getEmotionColor(stats.dominantEmotion) }}>
                            {stats.dominantEmotion}
                          </p>
                        </div>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              </motion.div>

              <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.3 }}>
                <Card>
                  <CardContent className="pt-6">
                    <div className="flex items-center justify-between">
                      <div>
                        <p className="text-sm text-gray-600">Avg Entries/Day</p>
                        <p className="text-3xl font-bold text-gray-900">{stats.avgEntriesPerDay}</p>
                      </div>
                      <BarChart3 className="w-8 h-8 text-blue-600" />
                    </div>
                  </CardContent>
                </Card>
              </motion.div>

              <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.4 }}>
                <Card>
                  <CardContent className="pt-6">
                    <div className="flex items-center justify-between">
                      <div>
                        <p className="text-sm text-gray-600">Mood Trend</p>
                        <div className="flex items-center gap-2 mt-1">
                          <TrendingUp 
                            className={`w-6 h-6 ${
                              stats.moodTrend === 'improving' ? 'text-green-600' : 
                              stats.moodTrend === 'declining' ? 'text-red-600 rotate-180' : 
                              'text-gray-600'
                            }`}
                          />
                          <p className="text-xl font-bold capitalize">
                            {stats.moodTrend}
                          </p>
                        </div>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              </motion.div>
            </div>

            {/* Charts Row */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
              {/* Mood Trend Line Chart */}
              <motion.div initial={{ opacity: 0, x: -20 }} animate={{ opacity: 1, x: 0 }} transition={{ delay: 0.5 }}>
                <Card>
                  <CardHeader>
                    <CardTitle className="flex items-center gap-2">
                      <TrendingUp className="w-5 h-5" />
                      Mood Trend Over Time
                    </CardTitle>
                    <CardDescription>Your emotional journey visualized</CardDescription>
                  </CardHeader>
                  <CardContent>
                    <ResponsiveContainer width="100%" height={300}>
                      <AreaChart data={moodTrendData}>
                        <CartesianGrid strokeDasharray="3 3" />
                        <XAxis dataKey="date" style={{ fontSize: '12px' }} />
                        <YAxis domain={[0, 100]} />
                        <Tooltip />
                        <Legend />
                        <Area 
                          type="monotone" 
                          dataKey="mood" 
                          stroke="#8b5cf6" 
                          fill="#8b5cf6" 
                          fillOpacity={0.3} 
                          name="Mood Score"
                        />
                      </AreaChart>
                    </ResponsiveContainer>
                  </CardContent>
                </Card>
              </motion.div>

              {/* Emotion Distribution Bar Chart */}
              <motion.div initial={{ opacity: 0, x: 20 }} animate={{ opacity: 1, x: 0 }} transition={{ delay: 0.6 }}>
                <Card>
                  <CardHeader>
                    <CardTitle className="flex items-center gap-2">
                      <BarChart3 className="w-5 h-5" />
                      Emotion Distribution
                    </CardTitle>
                    <CardDescription>Your most common emotional states</CardDescription>
                  </CardHeader>
                  <CardContent>
                    <ResponsiveContainer width="100%" height={300}>
                      <BarChart data={emotionDistData}>
                        <CartesianGrid strokeDasharray="3 3" />
                        <XAxis dataKey="emotion" style={{ fontSize: '12px' }} />
                        <YAxis />
                        <Tooltip />
                        <Bar dataKey="count" fill="#8b5cf6" radius={[8, 8, 0, 0]}>
                          {emotionDistData.map((entry, index) => (
                            <Cell key={`cell-${index}`} fill={entry.fill} />
                          ))}
                        </Bar>
                      </BarChart>
                    </ResponsiveContainer>
                  </CardContent>
                </Card>
              </motion.div>
            </div>

            {/* Calendar View */}
            <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.7 }}>
              <Card>
                <CardHeader>
                  <div className="flex items-center justify-between">
                    <div>
                      <CardTitle className="flex items-center gap-2">
                        <CalendarIcon className="w-5 h-5" />
                        Emotion Calendar
                      </CardTitle>
                      <CardDescription>Daily emotional patterns at a glance</CardDescription>
                    </div>
                    <div className="flex gap-2">
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => setSelectedMonth(new Date(selectedMonth.getFullYear(), selectedMonth.getMonth() - 1))}
                      >
                        ←
                      </Button>
                      <div className="px-4 py-2 font-semibold">
                        {selectedMonth.toLocaleDateString('en-US', { month: 'long', year: 'numeric' })}
                      </div>
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => setSelectedMonth(new Date(selectedMonth.getFullYear(), selectedMonth.getMonth() + 1))}
                        disabled={selectedMonth >= new Date()}
                      >
                        →
                      </Button>
                    </div>
                  </div>
                </CardHeader>
                <CardContent>
                  <div className="grid grid-cols-7 gap-2">
                    {['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'].map((day) => (
                      <div key={day} className="text-center text-sm font-semibold text-gray-600 py-2">
                        {day}
                      </div>
                    ))}
                    {calendarData.map((day, index) => (
                      <div
                        key={index}
                        className={`aspect-square flex items-center justify-center rounded-lg text-sm font-medium ${
                          day.empty
                            ? ''
                            : day.color
                            ? 'cursor-pointer hover:scale-110 transition-transform'
                            : 'bg-gray-50 text-gray-400'
                        }`}
                        style={day.color ? { 
                          backgroundColor: day.color + '30', 
                          border: `2px solid ${day.color}`,
                          color: day.color
                        } : {}}
                        title={day.emotion ? `${day.emotion} (${day.entries} entries)` : undefined}
                      >
                        {!day.empty && day.day}
                      </div>
                    ))}
                  </div>
                  
                  {/* Legend */}
                  <div className="mt-6 flex flex-wrap gap-3 justify-center">
                    {Object.entries(EMOTION_COLORS).slice(0, 6).map(([emotion, color]) => (
                      <div key={emotion} className="flex items-center gap-2">
                        <div className="w-4 h-4 rounded" style={{ backgroundColor: color }} />
                        <span className="text-sm text-gray-600 capitalize">{emotion}</span>
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>
            </motion.div>
          </>
        )}
      </div>
    </div>
  );
}
