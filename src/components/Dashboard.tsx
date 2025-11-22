import { useState, useEffect } from 'react';
import { motion } from 'motion/react';
import {
  MessageCircle,
  Mic,
  FileText,
  Palette,
  Bell,
  Flame,
  Wind,
  Droplet,
  Camera,
  TrendingUp,
  Heart,
  Activity,
  Target,
  Sparkles,
  ChevronLeft,
  ChevronRight,
  Loader2
} from 'lucide-react';
import { Navigation } from './Navigation';
import { Button } from './ui/button';
import { Badge } from './ui/badge';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogDescription } from './ui/dialog';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from './ui/select';
import api from '../services/api';
import type { PageType } from '../App';
import type { WellnessScore, AuraEntry, DoshaAssessment, EmotionLog, User } from '../types/api.types';

interface DashboardProps {
  user: User | null;
  onNavigate: (page: PageType) => void;
  onLogout?: () => void;
  onOpenNotifications?: () => void;
}

export function Dashboard({ user, onNavigate, onLogout, onOpenNotifications }: DashboardProps) {
  // UI State
  const [showNotification, setShowNotification] = useState(false);
  const [showStreakCalendar, setShowStreakCalendar] = useState(false);
  const [streakViewMonth, setStreakViewMonth] = useState(new Date().getMonth());
  const [streakViewYear, setStreakViewYear] = useState(new Date().getFullYear());
  const [currentDosha, setCurrentDosha] = useState<'vata' | 'pitta' | 'kapha'>('vata');

  // Backend Data State
  const [wellnessData, setWellnessData] = useState<WellnessScore | null>(null);
  const [auraData, setAuraData] = useState<AuraEntry | null>(null);
  const [doshaData, setDoshaData] = useState<DoshaAssessment | null>(null);
  const [recentEmotions, setRecentEmotions] = useState<EmotionLog[]>([]);
  const [loading, setLoading] = useState(true);
  const [mentalState, setMentalState] = useState<string>('balanced');
  const [generatingAura, setGeneratingAura] = useState(false);

  // Local State (fallback for streak tracking)
  const [streak, setStreak] = useState<number>(() => {
    const today = new Date();
    today.setHours(0, 0, 0, 0);
    const todayStr = today.toISOString().split('T')[0];

    const lastVisitStr = localStorage.getItem('nirvami_last_visit_date');
    const currentStreak = parseInt(localStorage.getItem('nirvami_streak') || '0', 10);

    const visitDatesStr = localStorage.getItem('nirvami_visit_dates');
    let visitDates = [];
    try {
      visitDates = visitDatesStr && visitDatesStr !== 'undefined' ? JSON.parse(visitDatesStr) : [];
    } catch (e) {
      console.error('Failed to parse visit dates:', e);
      visitDates = [];
    }

    if (!visitDates.includes(todayStr)) {
      visitDates.push(todayStr);
      localStorage.setItem('nirvami_visit_dates', JSON.stringify(visitDates));
    }

    if (!lastVisitStr) {
      localStorage.setItem('nirvami_last_visit_date', todayStr);
      localStorage.setItem('nirvami_streak', '1');
      return 1;
    }

    const lastVisit = new Date(lastVisitStr);
    lastVisit.setHours(0, 0, 0, 0);

    const yesterday = new Date(today);
    yesterday.setDate(yesterday.getDate() - 1);

    if (lastVisitStr === todayStr) {
      return currentStreak;
    }

    if (lastVisit.getTime() === yesterday.getTime()) {
      const newStreak = currentStreak + 1;
      localStorage.setItem('nirvami_last_visit_date', todayStr);
      localStorage.setItem('nirvami_streak', newStreak.toString());
      return newStreak;
    }

    localStorage.setItem('nirvami_last_visit_date', todayStr);
    localStorage.setItem('nirvami_streak', '1');
    return 1;
  });

  // Fetch dashboard data on mount
  useEffect(() => {
    const fetchDashboardData = async () => {
      if (!api.isAuthenticated()) {
        setLoading(false);
        return;
      }

      try {
        setLoading(true);

        // Fetch all data in parallel
        const [wellness, aura, dosha, emotions] = await Promise.all([
          api.getTodayWellness().catch(() => null),
          api.getTodayAura().catch(() => null),
          api.getLatestDosha().catch(() => null),
          api.getEmotionLogs({
            start_date: new Date(Date.now() - 24 * 60 * 60 * 1000).toISOString().split('T')[0],
            end_date: new Date().toISOString().split('T')[0]
          }).catch(() => []),
        ]);

        setWellnessData(wellness);
        setAuraData(aura);
        setDoshaData(dosha);
        setRecentEmotions(emotions);
      } catch (error) {
        console.error('Failed to fetch dashboard data:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchDashboardData();
  }, []);

  // Handle mental state change and regenerate aura
  const handleMentalStateChange = async (newState: string) => {
    setMentalState(newState);

    // Generate new aura based on mental state
    try {
      setGeneratingAura(true);
      const newAura = await api.generateAura();
      setAuraData(newAura);
    } catch (error) {
      console.error('Failed to generate aura:', error);
    } finally {
      setGeneratingAura(false);
    }
  };

  // Get visited dates for calendar
  const getVisitedDates = (): string[] => {
    const visitDatesStr = localStorage.getItem('nirvami_visit_dates');
    try {
      return visitDatesStr && visitDatesStr !== 'undefined' ? JSON.parse(visitDatesStr) : [];
    } catch (e) {
      console.error('Failed to parse visit dates:', e);
      return [];
    }
  };

  const isDateVisited = (dateStr: string): boolean => {
    const visitedDates = getVisitedDates();
    return visitedDates.includes(dateStr);
  };

  // Quick actions configuration
  const quickActions = [
    {
      id: 'chatbot' as PageType,
      icon: MessageCircle,
      label: 'AI Chat',
      gradient: 'from-purple-400 to-pink-400',
      bgGradient: 'from-purple-50 to-pink-50',
      description: 'Talk to AI'
    },
    {
      id: 'chatbot' as PageType,
      icon: Mic,
      label: 'Voice Mode',
      gradient: 'from-blue-400 to-cyan-400',
      bgGradient: 'from-blue-50 to-cyan-50',
      description: 'Speak naturally'
    },
    {
      id: 'manual' as PageType,
      icon: FileText,
      label: 'Manual Log',
      gradient: 'from-emerald-400 to-teal-400',
      bgGradient: 'from-emerald-50 to-teal-50',
      description: 'Track manually'
    },
    {
      id: 'aura' as PageType,
      icon: Sparkles,
      label: 'Aura Energy',
      gradient: 'from-violet-400 to-purple-400',
      bgGradient: 'from-violet-50 to-purple-50',
      description: 'View aura'
    },
    {
      id: 'moodboard' as PageType,
      icon: Palette,
      label: 'Mood Board',
      gradient: 'from-pink-400 to-rose-400',
      bgGradient: 'from-pink-50 to-rose-50',
      description: 'Express visually'
    },
    {
      id: 'yoga' as PageType,
      icon: Camera,
      label: 'Yoga Guide',
      gradient: 'from-indigo-400 to-blue-400',
      bgGradient: 'from-indigo-50 to-blue-50',
      description: 'AI posture check'
    },
    {
      id: 'diet' as PageType,
      icon: Heart,
      label: 'Diet Sync',
      gradient: 'from-orange-400 to-amber-400',
      bgGradient: 'from-orange-50 to-amber-50',
      description: 'Meal tracking'
    },
  ];

  // Dosha display configuration
  const doshaDisplay = {
    vata: {
      name: 'Vata',
      element: 'Air + Space',
      level: doshaData?.vata_score || 0,
      color: 'from-blue-400 via-cyan-400 to-blue-500',
      icon: Wind,
      bgColor: 'from-blue-100/50 to-cyan-100/50'
    },
    pitta: {
      name: 'Pitta',
      element: 'Fire + Water',
      level: doshaData?.pitta_score || 0,
      color: 'from-orange-400 via-red-400 to-pink-500',
      icon: Flame,
      bgColor: 'from-orange-100/50 to-pink-100/50'
    },
    kapha: {
      name: 'Kapha',
      element: 'Earth + Water',
      level: doshaData?.kapha_score || 0,
      color: 'from-green-400 via-emerald-400 to-teal-500',
      icon: Droplet,
      bgColor: 'from-green-100/50 to-teal-100/50'
    },
  };

  // Get current aura visualization
  const getAuraGradient = () => {
    if (!auraData) {
      return {
        gradient: 'from-gray-300 via-gray-400 to-gray-500',
        innerGlow: 'rgba(156, 163, 175, 0.4)',
        outerGlow: 'rgba(156, 163, 175, 0.2)',
        bgGradient: 'from-gray-50/50 to-gray-50/50',
        name: 'Neutral State',
        description: 'Building your energy profile',
        remedy: 'Continue logging your emotions and activities'
      };
    }

    // Map aura color to gradients
    const auraColorMap: Record<string, any> = {
      purple: {
        gradient: 'from-purple-300 via-violet-300 to-fuchsia-300',
        innerGlow: 'rgba(168, 85, 247, 0.4)',
        outerGlow: 'rgba(168, 85, 247, 0.2)',
        bgGradient: 'from-purple-50/50 to-violet-50/50',
        name: 'Crown Aura',
        description: 'Spiritual awareness and higher consciousness',
        remedy: 'Meditation and mindfulness practices'
      },
      blue: {
        gradient: 'from-blue-300 via-indigo-300 to-purple-300',
        innerGlow: 'rgba(59, 130, 246, 0.4)',
        outerGlow: 'rgba(59, 130, 246, 0.2)',
        bgGradient: 'from-blue-50/50 to-indigo-50/50',
        name: 'Throat Aura',
        description: 'Clear communication and self-expression',
        remedy: 'Deep breathing and vocal exercises'
      },
      green: {
        gradient: 'from-emerald-300 via-teal-300 to-cyan-300',
        innerGlow: 'rgba(34, 197, 94, 0.4)',
        outerGlow: 'rgba(34, 197, 94, 0.2)',
        bgGradient: 'from-emerald-50/50 to-teal-50/50',
        name: 'Heart Aura',
        description: 'Love, compassion, and emotional balance',
        remedy: 'Heart-opening yoga poses and gratitude practice'
      },
      yellow: {
        gradient: 'from-yellow-300 via-amber-300 to-orange-300',
        innerGlow: 'rgba(234, 179, 8, 0.4)',
        outerGlow: 'rgba(234, 179, 8, 0.2)',
        bgGradient: 'from-yellow-50/50 to-amber-50/50',
        name: 'Solar Plexus Aura',
        description: 'Personal power and confidence',
        remedy: 'Core strengthening and affirmations'
      },
      red: {
        gradient: 'from-red-300 via-rose-300 to-pink-300',
        innerGlow: 'rgba(239, 68, 68, 0.4)',
        outerGlow: 'rgba(239, 68, 68, 0.2)',
        bgGradient: 'from-red-50/50 to-rose-50/50',
        name: 'Root Aura',
        description: 'Grounded energy and vitality',
        remedy: 'Grounding exercises and physical activity'
      },
      indigo: {
        gradient: 'from-indigo-300 via-purple-300 to-violet-300',
        innerGlow: 'rgba(99, 102, 241, 0.4)',
        outerGlow: 'rgba(99, 102, 241, 0.2)',
        bgGradient: 'from-indigo-50/50 to-purple-50/50',
        name: 'Third Eye Aura',
        description: 'Intuition and inner wisdom',
        remedy: 'Visualization and intuitive development'
      },
      orange: {
        gradient: 'from-orange-300 via-amber-300 to-yellow-300',
        innerGlow: 'rgba(251, 146, 60, 0.4)',
        outerGlow: 'rgba(251, 146, 60, 0.2)',
        bgGradient: 'from-orange-50/50 to-amber-50/50',
        name: 'Sacral Aura',
        description: 'Creativity and emotional flow',
        remedy: 'Creative expression and hip-opening yoga'
      },
    };

    return auraColorMap[auraData.color_code] || auraColorMap.blue;
  };

  const currentAura = getAuraGradient();

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <Loader2 className="w-8 h-8 animate-spin text-purple-500" />
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-purple-100 via-blue-50 to-cyan-100 relative overflow-hidden">
      <Navigation currentPage="dashboard" onNavigate={onNavigate} onLogout={onLogout} user={user} onOpenNotifications={onOpenNotifications} />

      <div className="max-w-7xl mx-auto p-4 pb-24">
        {/* Welcome Header */}
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          className="mb-6"
        >
          <h1 className="text-4xl font-bold text-gray-800 mb-2">
            Welcome back, {user?.full_name || 'User'}! 🙏
          </h1>
          <p className="text-gray-600">Your holistic wellness journey continues</p>
        </motion.div>

        {/* Stats Grid */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
          {/* Wellness Score */}
          <motion.div
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            whileHover={{ scale: 1.02 }}
            className="bg-white/80 backdrop-blur-sm rounded-2xl p-6 shadow-lg border border-white/50"
          >
            <div className="flex items-center justify-between mb-4">
              <div className="flex items-center gap-3">
                <div className="p-3 bg-gradient-to-br from-purple-500 to-pink-500 rounded-xl">
                  <Activity className="w-6 h-6 text-white" />
                </div>
                <div>
                  <p className="text-sm text-gray-600">Wellness Score</p>
                  <p className="text-3xl font-bold text-gray-800">
                    {wellnessData ? Math.round(wellnessData.overall_score) : 0}
                  </p>
                </div>
              </div>
            </div>
            <div className="space-y-2">
              <div className="flex justify-between text-xs">
                <span className="text-gray-600">Emotional</span>
                <span className="font-medium">{wellnessData ? Math.round(wellnessData.emotion_score) : 0}%</span>
              </div>
              <div className="flex justify-between text-xs">
                <span className="text-gray-600">Physical</span>
                <span className="font-medium">{wellnessData ? Math.round(wellnessData.wearable_score) : 0}%</span>
              </div>
              <div className="flex justify-between text-xs">
                <span className="text-gray-600">Mental</span>
                <span className="font-medium">{wellnessData ? Math.round(wellnessData.engagement_score) : 0}%</span>
              </div>
            </div>
          </motion.div>

          {/* Streak Counter */}
          <motion.div
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ delay: 0.1 }}
            whileHover={{ scale: 1.02 }}
            onClick={() => setShowStreakCalendar(true)}
            className="bg-white/80 backdrop-blur-sm rounded-2xl p-6 shadow-lg border border-white/50 cursor-pointer"
          >
            <div className="flex items-center gap-3 mb-4">
              <div className="p-3 bg-gradient-to-br from-orange-400 to-red-400 rounded-xl">
                <Flame className="w-6 h-6 text-white" />
              </div>
              <div>
                <p className="text-sm text-gray-600">Daily Streak</p>
                <p className="text-3xl font-bold text-gray-800">{streak}</p>
              </div>
            </div>
            <p className="text-xs text-gray-600">Click to view calendar</p>
          </motion.div>

          {/* Aura Status */}
          <motion.div
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ delay: 0.2 }}
            whileHover={{ scale: 1.02 }}
            className={`bg-gradient-to-br ${currentAura.bgGradient} backdrop-blur-sm rounded-2xl p-6 shadow-lg border border-white/50`}
          >
            <div className="flex items-center gap-3 mb-4">
              <div className={`p-3 bg-gradient-to-br ${currentAura.innerGlow} rounded-xl`}>
                <Sparkles className="w-6 h-6 text-white" />
              </div>
              <div>
                <p className="text-sm text-gray-600">Aura Energy</p>
                <p className="text-3xl font-bold text-gray-800">
                  {auraData ? Math.round(auraData.intensity * 100) : 0}%
                </p>
              </div>
            </div>
            <p className="text-xs text-gray-600">
              {auraData?.color_code ? `${auraData.color_code.charAt(0).toUpperCase()}${auraData.color_code.slice(1)} aura detected` : 'No aura data'}
            </p>
          </motion.div>
        </div>

        {/* Aura Visualization Section */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.3 }}
          className="mb-6"
        >
          <h2 className="text-xl font-semibold text-gray-800 mb-4">Your Aura Energy</h2>
          <div className={`relative bg-gradient-to-br ${currentAura.bgGradient} rounded-2xl p-8 overflow-hidden shadow-lg`}>
            {/* Background shimmer effect */}
            <motion.div
              className="absolute inset-0 bg-gradient-to-r from-transparent via-white/10 to-transparent"
              animate={{
                x: ['-100%', '100%'],
              }}
              transition={{
                duration: 3,
                repeat: Infinity,
                ease: 'linear',
              }}
            />

            <div className="relative grid md:grid-cols-2 gap-8 items-center">
              {/* Aura Sphere Visualization */}
              <div className="flex items-center justify-center py-8">
                <div className="relative w-80 h-80">
                  {generatingAura && (
                    <div className="absolute inset-0 flex items-center justify-center z-10">
                      <div className="bg-black/50 backdrop-blur-sm rounded-full px-6 py-3 text-white text-sm font-medium">
                        Generating...
                      </div>
                    </div>
                  )}

                  {/* Outer glow */}
                  <motion.div
                    className="absolute inset-0 rounded-full blur-3xl opacity-40"
                    /* eslint-disable-next-line react/forbid-dom-props */
                    style={{
                      background: `radial-gradient(circle, ${currentAura.outerGlow} 0%, transparent 70%)`,
                    }}
                    animate={{
                      scale: [1, 1.15, 1],
                    }}
                    transition={{
                      duration: 4,
                      repeat: Infinity,
                      ease: 'easeInOut',
                    }}
                  />

                  {/* Middle glow */}
                  <motion.div
                    className="absolute inset-8 rounded-full blur-2xl opacity-50"
                    /* eslint-disable-next-line react/forbid-dom-props */
                    style={{
                      background: `radial-gradient(circle, ${currentAura.innerGlow} 0%, transparent 70%)`,
                    }}
                    animate={{
                      scale: [1, 1.08, 1],
                    }}
                    transition={{
                      duration: 3,
                      repeat: Infinity,
                      ease: 'easeInOut',
                    }}
                  />

                  {/* Main sphere with advanced glass effect */}
                  <motion.div
                    className="absolute inset-10 rounded-full overflow-hidden shadow-2xl"
                    animate={{
                      scale: [1, 1.02, 1],
                    }}
                    transition={{
                      duration: 2,
                      repeat: Infinity,
                      ease: 'easeInOut',
                    }}
                  >
                    {/* Base gradient */}
                    <div
                      className={`absolute inset-0 rounded-full bg-gradient-to-br ${currentAura.gradient}`}
                    />

                    {/* Bottom shadow for depth */}
                    <div
                      className="absolute inset-0 rounded-full bg-gradient-to-t from-black/30 via-transparent to-transparent"
                    />

                    {/* Rim light effect */}
                    <div
                      className="absolute inset-0 rounded-full"
                      /* eslint-disable-next-line react/forbid-dom-props */
                      style={{
                        background: 'radial-gradient(circle, transparent 50%, rgba(255, 255, 255, 0.6) 70%, rgba(255, 255, 255, 0.9) 85%, transparent 100%)'
                      }}
                    />

                    {/* Primary highlight - top left */}
                    <div
                      className="absolute top-[15%] left-[25%] w-32 h-32 rounded-full"
                      /* eslint-disable-next-line react/forbid-dom-props */
                      style={{
                        background: 'radial-gradient(circle at 30% 30%, rgba(255, 255, 255, 0.9) 0%, rgba(255, 255, 255, 0.6) 30%, transparent 70%)'
                      }}
                    />

                    {/* Secondary highlight */}
                    <div
                      className="absolute top-[20%] left-[15%] w-16 h-16 rounded-full"
                      /* eslint-disable-next-line react/forbid-dom-props */
                      style={{
                        background: 'radial-gradient(circle at 40% 40%, rgba(255, 255, 255, 0.7) 0%, rgba(255, 255, 255, 0.3) 40%, transparent 70%)'
                      }}
                    />

                    {/* Diagonal shine */}
                    <div
                      className="absolute inset-0 rounded-full"
                      /* eslint-disable-next-line react/forbid-dom-props */
                      style={{
                        background: 'linear-gradient(135deg, rgba(255, 255, 255, 0.4) 0%, transparent 30%, transparent 70%, rgba(255, 255, 255, 0.2) 100%)'
                      }}
                    />

                    {/* Inner glow layer */}
                    <motion.div
                      className={`absolute inset-10 rounded-full bg-gradient-to-br ${currentAura.gradient} opacity-40 blur-2xl`}
                      animate={{
                        scale: [1, 1.15, 1],
                      }}
                      transition={{
                        duration: 2.5,
                        repeat: Infinity,
                        ease: 'easeInOut',
                      }}
                    />

                    {/* Glass overlay */}
                    <div
                      className="absolute inset-0 rounded-full bg-gradient-to-br from-white/10 via-transparent to-black/10"
                    />

                    {/* Bottom reflection */}
                    <div
                      className="absolute bottom-[10%] left-[50%] -translate-x-1/2 w-20 h-10 rounded-full"
                      /* eslint-disable-next-line react/forbid-dom-props */
                      style={{
                        background: 'radial-gradient(rgba(255, 255, 255, 0.4) 0%, transparent 70%)',
                        filter: 'blur(4px)'
                      }}
                    />

                    {/* Rotating shimmer streak */}
                    <motion.div
                      className="absolute inset-0 rounded-full"
                      /* eslint-disable-next-line react/forbid-dom-props */
                      style={{
                        background: 'linear-gradient(120deg, transparent 30%, rgba(255, 255, 255, 0.3) 50%, transparent 70%)'
                      }}
                      animate={{
                        rotate: 360,
                      }}
                      transition={{
                        duration: 20,
                        repeat: Infinity,
                        ease: 'linear',
                      }}
                    />

                    {/* Outer border highlight */}
                    <div className="absolute inset-0 rounded-full border-2 border-white/20" />
                  </motion.div>

                  {/* Energy Intensity Display */}
                  <motion.div
                    initial={{ opacity: 0, scale: 0.8 }}
                    animate={{ opacity: 1, scale: 1 }}
                    transition={{ delay: 0.5 }}
                    className="absolute bottom-0 left-1/2 -translate-x-1/2 text-center"
                  >
                    <p className="text-4xl font-bold text-gray-800">
                      {auraData ? Math.round(auraData.intensity * 100) : 0}%
                    </p>
                    <p className="text-sm text-gray-600 mt-1">Energy Intensity</p>
                  </motion.div>
                </div>
              </div>

              {/* Aura Information */}
              <div className="space-y-6">
                <div className="bg-white/60 backdrop-blur-sm rounded-2xl p-5 border border-white/50">
                  <Badge className={`bg-gradient-to-r ${currentAura.gradient} text-white mb-2`}>
                    {currentAura.name}
                  </Badge>
                  <h3 className="text-lg text-gray-800 mb-2">
                    {auraData?.color_code ? `${auraData.color_code.charAt(0).toUpperCase()}${auraData.color_code.slice(1)}` : 'Purple'} Aura
                  </h3>
                  <p className="text-sm text-gray-600 mb-4">
                    {currentAura.description}
                  </p>

                  {/* Mental State Selector */}
                  <div className="space-y-2">
                    <p className="text-xs text-gray-500 mb-3">How are you feeling right now?</p>
                    <Select value={mentalState} onValueChange={handleMentalStateChange} disabled={generatingAura}>
                      <SelectTrigger className="w-full bg-white/80 border-white/50">
                        <SelectValue placeholder="— None" />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="balanced">🧘 Balanced & Calm</SelectItem>
                        <SelectItem value="energized">⚡ Energized & Active</SelectItem>
                        <SelectItem value="stressed">😰 Stressed & Anxious</SelectItem>
                        <SelectItem value="focused">🎯 Focused & Sharp</SelectItem>
                        <SelectItem value="tired">😴 Tired & Drained</SelectItem>
                        <SelectItem value="joyful">😊 Joyful & Happy</SelectItem>
                        <SelectItem value="sad">😢 Sad & Low</SelectItem>
                        <SelectItem value="angry">😠 Angry & Frustrated</SelectItem>
                        <SelectItem value="peaceful">🕊️ Peaceful & Content</SelectItem>
                        <SelectItem value="confused">🤔 Confused & Uncertain</SelectItem>
                        <SelectItem value="motivated">🔥 Motivated & Driven</SelectItem>
                        <SelectItem value="overwhelmed">🌊 Overwhelmed</SelectItem>
                        <SelectItem value="creative">🎨 Creative & Inspired</SelectItem>
                        <SelectItem value="restless">😣 Restless & Agitated</SelectItem>
                        <SelectItem value="grateful">🙏 Grateful & Thankful</SelectItem>
                      </SelectContent>
                    </Select>
                    {generatingAura && (
                      <p className="text-xs text-purple-600 animate-pulse">Generating new aura...</p>
                    )}
                  </div>
                </div>

                {/* Color Therapy Info */}
                <div className="bg-white/60 backdrop-blur-sm rounded-2xl p-5 border border-white/50">
                  <h4 className="text-sm text-gray-700 mb-2">💡 Color Therapy</h4>
                  <p className="text-xs text-gray-600 leading-relaxed">
                    The colors you see are scientifically chosen based on color psychology to help regulate your emotions. Calming blues soothe anxiety, warm tones uplift mood, and balanced greens promote harmony.
                  </p>
                </div>

                {/* Remedy Section */}
                <div className="bg-white/60 backdrop-blur-sm rounded-2xl p-5 border border-white/50">
                  <div className="flex items-start gap-2">
                    <Sparkles className="w-5 h-5 text-purple-600 mt-0.5 flex-shrink-0" />
                    <div>
                      <p className="text-sm font-medium text-gray-800 mb-1">Recommended Practice</p>
                      <p className="text-xs text-gray-700">{currentAura.remedy}</p>
                    </div>
                  </div>
                </div>

                {/* View Details Button */}
                <motion.button
                  onClick={() => onNavigate('aura')}
                  className="w-full bg-gradient-to-r from-purple-500 to-pink-500 text-white py-3 rounded-lg font-medium shadow-md hover:shadow-lg transition-all"
                  whileHover={{ scale: 1.02 }}
                  whileTap={{ scale: 0.98 }}
                >
                  Explore Full Aura Analysis →
                </motion.button>
              </div>
            </div>
          </div>
        </motion.div>

        {/* Quick Actions */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.4 }}
          className="mb-6"
        >
          <h2 className="text-xl font-semibold text-gray-800 mb-4">Quick Actions</h2>
          <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-3">
            {quickActions.map((action, index) => (
              <motion.button
                key={action.id + action.label}
                onClick={() => onNavigate(action.id)}
                className={`bg-gradient-to-br ${action.bgGradient} rounded-xl p-4 shadow-md hover:shadow-lg transition-all`}
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.4 + index * 0.05 }}
              >
                <div className={`p-3 bg-gradient-to-br ${action.gradient} rounded-lg mb-2 mx-auto w-fit`}>
                  <action.icon className="w-6 h-6 text-white" />
                </div>
                <p className="text-sm font-medium text-gray-700">{action.label}</p>
                <p className="text-xs text-gray-500">{action.description}</p>
              </motion.button>
            ))}
          </div>
        </motion.div>

        {/* Dosha Balance */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.5 }}
          className="mb-6"
        >
          <h2 className="text-xl font-semibold text-gray-800 mb-4">Dosha Balance</h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {Object.entries(doshaDisplay).map(([key, dosha], index) => {
              const Icon = dosha.icon;
              return (
                <motion.div
                  key={key}
                  initial={{ opacity: 0, x: -20 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: 0.6 + index * 0.1 }}
                  whileHover={{ scale: 1.02 }}
                  className={`bg-gradient-to-br ${dosha.bgColor} backdrop-blur-sm rounded-xl p-5 shadow-md border border-white/50`}
                >
                  <div className="flex items-center justify-between mb-3">
                    <div className="flex items-center gap-2">
                      <div className={`p-2 bg-gradient-to-br ${dosha.color} rounded-lg`}>
                        <Icon className="w-5 h-5 text-white" />
                      </div>
                      <div>
                        <p className="font-semibold text-gray-800">{dosha.name}</p>
                        <p className="text-xs text-gray-600">{dosha.element}</p>
                      </div>
                    </div>
                    <p className="text-2xl font-bold text-gray-800">{Math.round(dosha.level)}%</p>
                  </div>
                  <div className="w-full bg-white/50 rounded-full h-2">
                    <motion.div
                      initial={{ width: 0 }}
                      animate={{ width: `${dosha.level}%` }}
                      transition={{ duration: 1, delay: 0.8 + index * 0.1 }}
                      className={`h-2 rounded-full bg-gradient-to-r ${dosha.color}`}
                    />
                  </div>
                </motion.div>
              );
            })}
          </div>
          {doshaData && (
            <motion.p
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ delay: 1 }}
              className="text-sm text-gray-600 mt-3 text-center"
            >
              Your dominant dosha is <span className="font-semibold">{doshaData.dominant_dosha.charAt(0).toUpperCase()}{doshaData.dominant_dosha.slice(1)}</span>
            </motion.p>
          )}
        </motion.div>

        {/* Recent Emotions */}
        {recentEmotions.length > 0 && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.7 }}
            className="mb-6"
          >
            <h2 className="text-xl font-semibold text-gray-800 mb-4">Recent Emotions</h2>
            <div className="bg-white/80 backdrop-blur-sm rounded-xl p-5 shadow-md">
              <div className="flex flex-wrap gap-2">
                {recentEmotions.slice(0, 10).map((emotion) => (
                  <Badge key={emotion.id} variant="secondary" className="px-3 py-1">
                    {emotion.emotion} ({emotion.intensity}/10)
                  </Badge>
                ))}
              </div>
            </div>
          </motion.div>
        )}
      </div>

      {/* Streak Calendar Dialog - keeping the existing implementation */}
      <Dialog open={showStreakCalendar} onOpenChange={setShowStreakCalendar}>
        <DialogContent className="max-w-md">
          <DialogHeader>
            <DialogTitle>Your Wellness Journey</DialogTitle>
            <DialogDescription>Daily activity streak: {streak} days</DialogDescription>
          </DialogHeader>
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <Button
                variant="outline"
                size="icon"
                onClick={() => {
                  if (streakViewMonth === 0) {
                    setStreakViewMonth(11);
                    setStreakViewYear(streakViewYear - 1);
                  } else {
                    setStreakViewMonth(streakViewMonth - 1);
                  }
                }}
              >
                <ChevronLeft className="w-4 h-4" />
              </Button>
              <div className="text-center">
                <p className="font-semibold">
                  {new Date(streakViewYear, streakViewMonth).toLocaleDateString('default', { month: 'long', year: 'numeric' })}
                </p>
              </div>
              <Button
                variant="outline"
                size="icon"
                onClick={() => {
                  if (streakViewMonth === 11) {
                    setStreakViewMonth(0);
                    setStreakViewYear(streakViewYear + 1);
                  } else {
                    setStreakViewMonth(streakViewMonth + 1);
                  }
                }}
              >
                <ChevronRight className="w-4 h-4" />
              </Button>
            </div>
            <div className="grid grid-cols-7 gap-2 text-center">
              {['S', 'M', 'T', 'W', 'T', 'F', 'S'].map((day, idx) => (
                <div key={`day-${idx}`} className="text-xs font-semibold text-gray-600">
                  {day}
                </div>
              ))}
              {Array.from({ length: new Date(streakViewYear, streakViewMonth, 1).getDay() }).map((_, i) => (
                <div key={`empty-${i}`} />
              ))}
              {Array.from({ length: new Date(streakViewYear, streakViewMonth + 1, 0).getDate() }).map((_, i) => {
                const dayDate = new Date(streakViewYear, streakViewMonth, i + 1);
                const dateStr = dayDate.toISOString().split('T')[0];
                const visited = isDateVisited(dateStr);
                const isToday = dateStr === new Date().toISOString().split('T')[0];

                return (
                  <div
                    key={i}
                    className={`
                      aspect-square rounded-lg flex items-center justify-center text-sm
                      ${visited ? 'bg-gradient-to-br from-purple-500 to-pink-500 text-white font-semibold' : 'bg-gray-100 text-gray-400'}
                      ${isToday ? 'ring-2 ring-purple-500 ring-offset-2' : ''}
                    `}
                  >
                    {i + 1}
                  </div>
                );
              })}
            </div>
          </div>
        </DialogContent>
      </Dialog>
    </div>
  );
}
