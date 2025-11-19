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
  ChevronRight
} from 'lucide-react';
import { Navigation } from './Navigation';
import { Button } from './ui/button';
import { Badge } from './ui/badge';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogDescription } from './ui/dialog';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from './ui/select';
import type { PageType, User } from '../App';

interface DashboardProps {
  user: User | null;
  onNavigate: (page: PageType) => void;
  onLogout: () => void;
}

export function Dashboard({ user, onNavigate, onLogout }: DashboardProps) {
  const [showNotification, setShowNotification] = useState(false);
  const [showStreakCalendar, setShowStreakCalendar] = useState(false);
  const [streakViewMonth, setStreakViewMonth] = useState(new Date().getMonth());
  const [streakViewYear, setStreakViewYear] = useState(new Date().getFullYear());
  const [currentDosha, setCurrentDosha] = useState<'vata' | 'pitta' | 'kapha'>('vata');
  
  // Initialize mental state from localStorage or default to 'none'
  const [mentalState, setMentalState] = useState<
    'sadness' | 'anxiety' | 'anger' | 'exhaustion' | 'confusion' | 'numbness' | 
    'stress' | 'overstimulation' | 'loneliness' | 'insecurity' | 'resentment' | 
    'love' | 'happiness' | 'mindfulness' | 'motivation' | 'none'
  >(() => {
    // Check localStorage on initial load
    const stored = localStorage.getItem('nirvami_mental_state');
    const timestamp = localStorage.getItem('nirvami_mental_state_timestamp');
    
    if (stored && timestamp) {
      const now = Date.now();
      const elapsed = now - parseInt(timestamp, 10);
      const twentyFourHours = 24 * 60 * 60 * 1000; // 24 hours in milliseconds
      
      // If less than 24 hours, use stored state
      if (elapsed < twentyFourHours) {
        return stored as typeof mentalState;
      }
    }
    
    // Default to 'none' if no valid stored state
    return 'none';
  });

  // Streak calculation - resets at midnight, requires daily visits
  const [streak, setStreak] = useState<number>(() => {
    const today = new Date();
    today.setHours(0, 0, 0, 0); // Reset to start of day
    const todayStr = today.toISOString().split('T')[0]; // YYYY-MM-DD format
    
    const lastVisitStr = localStorage.getItem('nirvami_last_visit_date');
    const currentStreak = parseInt(localStorage.getItem('nirvami_streak') || '0', 10);
    
    // Track all visit dates for calendar
    const visitDatesStr = localStorage.getItem('nirvami_visit_dates');
    const visitDates = visitDatesStr ? JSON.parse(visitDatesStr) : [];
    
    // Add today to visit dates if not already there
    if (!visitDates.includes(todayStr)) {
      visitDates.push(todayStr);
      localStorage.setItem('nirvami_visit_dates', JSON.stringify(visitDates));
    }
    
    if (!lastVisitStr) {
      // First visit ever
      localStorage.setItem('nirvami_last_visit_date', todayStr);
      localStorage.setItem('nirvami_streak', '1');
      return 1;
    }
    
    const lastVisit = new Date(lastVisitStr);
    lastVisit.setHours(0, 0, 0, 0);
    
    const yesterday = new Date(today);
    yesterday.setDate(yesterday.getDate() - 1);
    
    // Same day - keep current streak
    if (lastVisitStr === todayStr) {
      return currentStreak;
    }
    
    // Visited yesterday - increment streak
    if (lastVisit.getTime() === yesterday.getTime()) {
      const newStreak = currentStreak + 1;
      localStorage.setItem('nirvami_last_visit_date', todayStr);
      localStorage.setItem('nirvami_streak', newStreak.toString());
      return newStreak;
    }
    
    // Missed a day - reset to 1
    localStorage.setItem('nirvami_last_visit_date', todayStr);
    localStorage.setItem('nirvami_streak', '1');
    return 1;
  });

  // Get visited dates for calendar
  const getVisitedDates = (): string[] => {
    const visitDatesStr = localStorage.getItem('nirvami_visit_dates');
    return visitDatesStr ? JSON.parse(visitDatesStr) : [];
  };

  // Check if a date was visited
  const isDateVisited = (dateStr: string): boolean => {
    const visitedDates = getVisitedDates();
    return visitedDates.includes(dateStr);
  };

  // Get today's log data for wellness goals
  const getTodayLog = () => {
    const todayStr = new Date().toISOString().split('T')[0];
    const logsStr = localStorage.getItem('nirvami_daily_logs');
    if (!logsStr) return null;
    const logs = JSON.parse(logsStr);
    return logs[todayStr] || null;
  };

  // Check wellness goals completion
  const checkWellnessGoals = () => {
    const todayLog = getTodayLog();
    
    // Check if 3 main meals logged (breakfast, lunch, dinner)
    const has3Meals = todayLog && todayLog.meals ? 
      todayLog.meals.some((m: any) => m.mealType === 'breakfast') &&
      todayLog.meals.some((m: any) => m.mealType === 'lunch') &&
      todayLog.meals.some((m: any) => m.mealType === 'dinner') : false;
    
    // Check if mood tracked
    const moodTracked = todayLog && todayLog.mood !== null;
    
    // Check if 8+ hours sleep
    const has8HoursSleep = todayLog && todayLog.sleepHours ? 
      parseFloat(todayLog.sleepHours) >= 8 : false;
    
    return {
      meals: has3Meals,
      mood: moodTracked,
      sleep: has8HoursSleep
    };
  };

  const wellnessGoals = checkWellnessGoals();

  // Save mental state to localStorage whenever it changes
  useEffect(() => {
    localStorage.setItem('nirvami_mental_state', mentalState);
    localStorage.setItem('nirvami_mental_state_timestamp', Date.now().toString());
  }, [mentalState]);

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
      gradient: 'from-violet-400 to-purple-400',
      bgGradient: 'from-violet-50 to-purple-50',
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

  const doshaData = {
    vata: { 
      name: 'Vata',
      element: 'Air + Space',
      level: 65,
      color: 'from-blue-400 via-cyan-400 to-blue-500',
      icon: Wind,
      bgColor: 'from-blue-100/50 to-cyan-100/50'
    },
    pitta: { 
      name: 'Pitta',
      element: 'Fire + Water',
      level: 45,
      color: 'from-orange-400 via-red-400 to-pink-500',
      icon: Flame,
      bgColor: 'from-orange-100/50 to-pink-100/50'
    },
    kapha: { 
      name: 'Kapha',
      element: 'Earth + Water',
      level: 55,
      color: 'from-green-400 via-emerald-400 to-teal-500',
      icon: Droplet,
      bgColor: 'from-green-100/50 to-teal-100/50'
    },
  };

  // Aura colors based on mental state - using color psychology
  const auraStates = {
    anxiety: {
      name: 'Anxiety',
      description: 'Calming blue tones to soothe anxiety',
      gradient: 'from-blue-300 via-indigo-300 to-purple-300',
      innerGlow: 'from-blue-400 to-indigo-400',
      outerGlow: 'from-blue-200 to-purple-200',
      remedy: 'Deep breathing recommended',
      bgGradient: 'from-blue-50/50 to-indigo-50/50'
    },
    sadness: {
      name: 'Sadness',
      description: 'Uplifting warm colors for emotional support',
      gradient: 'from-rose-300 via-pink-300 to-fuchsia-300',
      innerGlow: 'from-rose-400 to-pink-400',
      outerGlow: 'from-rose-200 to-fuchsia-200',
      remedy: 'Self-care and mindfulness',
      bgGradient: 'from-rose-50/50 to-pink-50/50'
    },
    anger: {
      name: 'Anger',
      description: 'Cooling green tones to calm anger',
      gradient: 'from-emerald-300 via-teal-300 to-cyan-300',
      innerGlow: 'from-emerald-400 to-teal-400',
      outerGlow: 'from-emerald-200 to-cyan-200',
      remedy: 'Mindful breathing exercises',
      bgGradient: 'from-emerald-50/50 to-teal-50/50'
    },
    exhaustion: {
      name: 'Exhaustion',
      description: 'Energizing warm tones to uplift',
      gradient: 'from-amber-300 via-orange-300 to-yellow-300',
      innerGlow: 'from-amber-400 to-orange-400',
      outerGlow: 'from-amber-200 to-yellow-200',
      remedy: 'Light exercise or rest needed',
      bgGradient: 'from-amber-50/50 to-orange-50/50'
    },
    confusion: {
      name: 'Confusion',
      description: 'Clearing blue tones to enhance focus',
      gradient: 'from-blue-300 via-indigo-300 to-purple-300',
      innerGlow: 'from-blue-400 to-indigo-400',
      outerGlow: 'from-blue-200 to-purple-200',
      remedy: 'Meditation and deep breathing',
      bgGradient: 'from-blue-50/50 to-indigo-50/50'
    },
    numbness: {
      name: 'Numbness',
      description: 'Warm and grounding tones to reconnect',
      gradient: 'from-orange-300 via-red-300 to-pink-300',
      innerGlow: 'from-orange-400 to-red-400',
      outerGlow: 'from-orange-200 to-pink-200',
      remedy: 'Physical activity and mindfulness',
      bgGradient: 'from-orange-50/50 to-red-50/50'
    },
    stress: {
      name: 'Stress',
      description: 'Relaxing green tones to reduce stress',
      gradient: 'from-emerald-300 via-teal-300 to-cyan-300',
      innerGlow: 'from-emerald-400 to-teal-400',
      outerGlow: 'from-emerald-200 to-cyan-200',
      remedy: 'Progressive muscle relaxation',
      bgGradient: 'from-emerald-50/50 to-teal-50/50'
    },
    overstimulation: {
      name: 'Overstimulation',
      description: 'Calm blue tones to soothe the mind',
      gradient: 'from-blue-300 via-indigo-300 to-purple-300',
      innerGlow: 'from-blue-400 to-indigo-400',
      outerGlow: 'from-blue-200 to-purple-200',
      remedy: 'Guided imagery and deep breathing',
      bgGradient: 'from-blue-50/50 to-indigo-50/50'
    },
    loneliness: {
      name: 'Loneliness',
      description: 'Warm and comforting tones to alleviate loneliness',
      gradient: 'from-rose-300 via-pink-300 to-fuchsia-300',
      innerGlow: 'from-rose-400 to-pink-400',
      outerGlow: 'from-rose-200 to-fuchsia-200',
      remedy: 'Connect with loved ones',
      bgGradient: 'from-rose-50/50 to-pink-50/50'
    },
    insecurity: {
      name: 'Insecurity',
      description: 'Boosting yellow tones to enhance confidence',
      gradient: 'from-amber-300 via-orange-300 to-yellow-300',
      innerGlow: 'from-amber-400 to-orange-400',
      outerGlow: 'from-amber-200 to-yellow-200',
      remedy: 'Affirmations and positive self-talk',
      bgGradient: 'from-amber-50/50 to-orange-50/50'
    },
    resentment: {
      name: 'Resentment',
      description: 'Cooling blue tones to release negative emotions',
      gradient: 'from-blue-300 via-indigo-300 to-purple-300',
      innerGlow: 'from-blue-400 to-indigo-400',
      outerGlow: 'from-blue-200 to-purple-200',
      remedy: 'Forgiveness practices',
      bgGradient: 'from-blue-50/50 to-indigo-50/50'
    },
    love: {
      name: 'Love',
      description: 'Warm and heartwarming tones to promote love',
      gradient: 'from-rose-300 via-pink-300 to-fuchsia-300',
      innerGlow: 'from-rose-400 to-pink-400',
      outerGlow: 'from-rose-200 to-fuchsia-200',
      remedy: 'Express gratitude and kindness',
      bgGradient: 'from-rose-50/50 to-pink-50/50'
    },
    happiness: {
      name: 'Happiness',
      description: 'Bright and uplifting tones to boost happiness',
      gradient: 'from-yellow-300 via-orange-300 to-red-300',
      innerGlow: 'from-yellow-400 to-orange-400',
      outerGlow: 'from-yellow-200 to-red-200',
      remedy: 'Engage in activities you enjoy',
      bgGradient: 'from-yellow-50/50 to-orange-50/50'
    },
    mindfulness: {
      name: 'Mindfulness',
      description: 'Calm blue tones to enhance mindfulness',
      gradient: 'from-blue-300 via-indigo-300 to-purple-300',
      innerGlow: 'from-blue-400 to-indigo-400',
      outerGlow: 'from-blue-200 to-purple-200',
      remedy: 'Mindful meditation practices',
      bgGradient: 'from-blue-50/50 to-indigo-50/50'
    },
    motivation: {
      name: 'Motivation',
      description: 'Energizing orange tones to boost motivation',
      gradient: 'from-orange-300 via-red-300 to-pink-300',
      innerGlow: 'from-orange-400 to-red-400',
      outerGlow: 'from-orange-200 to-pink-200',
      remedy: 'Set small, achievable goals',
      bgGradient: 'from-orange-50/50 to-red-50/50'
    },
    none: {
      name: 'None',
      description: 'No specific emotional state detected',
      gradient: 'from-gray-300 via-gray-400 to-gray-500',
      innerGlow: 'from-gray-400 to-gray-500',
      outerGlow: 'from-gray-200 to-gray-300',
      remedy: 'Continue with your routine',
      bgGradient: 'from-gray-50/50 to-gray-50/50'
    }
  };

  const currentAura = auraStates[mentalState];

  return (
    <div className="min-h-screen bg-gradient-to-br from-purple-100 via-blue-50 to-cyan-100 relative overflow-hidden">
      {/* Animated background blobs removed for performance */}

      <Navigation currentPage="dashboard" onNavigate={onNavigate} onLogout={onLogout} user={user} />

      <div className="max-w-7xl mx-auto p-6 md:p-8 relative z-10">
        {/* Welcome Section */}
        <div className="mb-8">
          <div className="flex items-center justify-between mb-6">
            <div>
              <h1 className="text-3xl md:text-4xl text-gray-800 mb-2">
                Welcome back, <span className="bg-gradient-to-r from-purple-600 to-pink-600 bg-clip-text text-transparent">{user?.name}</span>! ✨
              </h1>
              <p className="text-gray-600 text-lg">Here's your wellness journey today</p>
            </div>
            <Button
              variant="ghost"
              size="icon"
              className="relative"
              onClick={() => setShowNotification(true)}
            >
              <Bell className="w-6 h-6 text-purple-600" />
              <span className="absolute top-0 right-0 w-2 h-2 bg-pink-500 rounded-full animate-pulse" />
            </Button>
          </div>
        </div>

        {/* Stats Cards Row */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8">
          {[
            { label: 'Mood Score', value: '8.5/10', icon: Heart, gradient: 'from-pink-400 to-rose-400', clickable: false },
            { label: 'Streak', value: `${streak} Days`, icon: Flame, gradient: 'from-orange-400 to-red-400', clickable: true },
            { label: 'Activity', value: '85%', icon: Activity, gradient: 'from-blue-400 to-cyan-400', clickable: false },
            { label: 'Balance', value: 'Optimal', icon: Target, gradient: 'from-purple-400 to-violet-400', clickable: false },
          ].map((stat) => (
            <div key={stat.label} className="relative group">
              {/* Glass card */}
              <div 
                className={`relative bg-white/40 backdrop-blur-xl rounded-3xl p-5 border border-white/50 shadow-xl ${
                  stat.clickable ? 'cursor-pointer hover:scale-105 transition-transform' : ''
                }`}
                onClick={() => stat.clickable && setShowStreakCalendar(true)}
              >
                <div className={`inline-flex p-3 rounded-2xl bg-gradient-to-br ${stat.gradient} mb-3`}>
                  <stat.icon className="w-5 h-5 text-white" />
                </div>
                <p className="text-sm text-gray-600 mb-1">{stat.label}</p>
                <p className="text-xl text-gray-900">{stat.value}</p>
              </div>
            </div>
          ))}
        </div>

        {/* Aura Visualization Section */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.15 }}
          className="mb-8"
        >
          <div className="relative bg-white/40 backdrop-blur-xl rounded-3xl p-8 border border-white/50 shadow-xl overflow-hidden">
            {/* Background gradient that matches aura */}
            <div className={`absolute inset-0 bg-gradient-to-br ${currentAura.bgGradient} opacity-30`} />
            
            <div className="relative z-10">
              <div className="flex items-center justify-between mb-6">
                <div>
                  <h2 className="text-2xl text-gray-800 mb-1">Your Aura Today</h2>
                  <p className="text-sm text-gray-600">{currentAura.description}</p>
                </div>
                <Badge className="bg-white/80 text-gray-700 border-0">
                  <Sparkles className="w-3 h-3 mr-1" />
                  AI Detected
                </Badge>
              </div>

              <div className="grid md:grid-cols-2 gap-8 items-center">
                {/* Aura Sphere */}
                <div className="flex items-center justify-center py-8">
                  <div className="relative w-80 h-80">
                    {/* Outer glow layers */}
                    <motion.div
                      className={`absolute inset-0 rounded-full bg-gradient-to-br ${currentAura.outerGlow} blur-3xl opacity-40`}
                      animate={{
                        scale: [1, 1.3, 1],
                        opacity: [0.4, 0.6, 0.4],
                      }}
                      transition={{
                        duration: 4,
                        repeat: Infinity,
                        ease: "easeInOut",
                      }}
                    />
                    
                    <motion.div
                      className={`absolute inset-8 rounded-full bg-gradient-to-br ${currentAura.outerGlow} blur-2xl opacity-50`}
                      animate={{
                        scale: [1, 1.2, 1],
                        opacity: [0.5, 0.7, 0.5],
                      }}
                      transition={{
                        duration: 3,
                        repeat: Infinity,
                        ease: "easeInOut",
                        delay: 0.5,
                      }}
                    />

                    {/* Main sphere container */}
                    <motion.div
                      className="absolute inset-10 rounded-full overflow-hidden shadow-2xl"
                      animate={{
                        scale: [1, 1.03, 1],
                      }}
                      transition={{
                        duration: 4,
                        repeat: Infinity,
                        ease: "easeInOut",
                      }}
                    >
                      {/* Base gradient sphere */}
                      <div className={`absolute inset-0 rounded-full bg-gradient-to-br ${currentAura.gradient}`} />
                      
                      {/* Shadow/depth layer - bottom dark */}
                      <div className="absolute inset-0 rounded-full bg-gradient-to-t from-black/30 via-transparent to-transparent" />
                      
                      {/* Rim lighting - bright edges */}
                      <div className="absolute inset-0 rounded-full" style={{
                        background: 'radial-gradient(circle at 50% 50%, transparent 50%, rgba(255,255,255,0.6) 70%, rgba(255,255,255,0.9) 85%, transparent 100%)'
                      }} />
                      
                      {/* Top highlight - main glossy spot */}
                      <motion.div
                        className="absolute top-[15%] left-[25%] w-32 h-32 rounded-full"
                        style={{
                          background: 'radial-gradient(circle at 30% 30%, rgba(255,255,255,0.9) 0%, rgba(255,255,255,0.6) 30%, transparent 70%)'
                        }}
                        animate={{
                          opacity: [0.8, 1, 0.8],
                        }}
                        transition={{
                          duration: 3,
                          repeat: Infinity,
                          ease: "easeInOut",
                        }}
                      />
                      
                      {/* Secondary smaller highlight */}
                      <div 
                        className="absolute top-[20%] left-[15%] w-16 h-16 rounded-full"
                        style={{
                          background: 'radial-gradient(circle at 40% 40%, rgba(255,255,255,0.7) 0%, rgba(255,255,255,0.3) 40%, transparent 70%)'
                        }}
                      />
                      
                      {/* Diagonal light streak */}
                      <motion.div
                        className="absolute inset-0 rounded-full"
                        style={{
                          background: 'linear-gradient(135deg, rgba(255,255,255,0.4) 0%, transparent 30%, transparent 70%, rgba(255,255,255,0.2) 100%)'
                        }}
                        animate={{
                          opacity: [0.5, 0.8, 0.5],
                        }}
                        transition={{
                          duration: 4,
                          repeat: Infinity,
                          ease: "easeInOut",
                          delay: 1,
                        }}
                      />
                      
                      {/* Inner glow pulse */}
                      <motion.div
                        className={`absolute inset-10 rounded-full bg-gradient-to-br ${currentAura.innerGlow} opacity-40 blur-2xl`}
                        animate={{
                          scale: [1, 1.3, 1],
                          opacity: [0.4, 0.7, 0.4],
                        }}
                        transition={{
                          duration: 2.5,
                          repeat: Infinity,
                          ease: "easeInOut",
                        }}
                      />
                      
                      {/* Glass refraction effect */}
                      <div className="absolute inset-0 rounded-full bg-gradient-to-br from-white/10 via-transparent to-black/10" />
                      
                      {/* Bottom light reflection */}
                      <div 
                        className="absolute bottom-[10%] left-[50%] -translate-x-1/2 w-20 h-10 rounded-full"
                        style={{
                          background: 'radial-gradient(ellipse at center, rgba(255,255,255,0.4) 0%, transparent 70%)',
                          filter: 'blur(4px)'
                        }}
                      />

                      {/* Rotating shimmer */}
                      <motion.div
                        className="absolute inset-0 rounded-full"
                        style={{
                          background: 'linear-gradient(120deg, transparent 30%, rgba(255,255,255,0.3) 50%, transparent 70%)',
                        }}
                        animate={{
                          rotate: [0, 360],
                        }}
                        transition={{
                          duration: 10,
                          repeat: Infinity,
                          ease: "linear",
                        }}
                      />
                      
                      {/* Outer glass reflection edge */}
                      <div className="absolute inset-0 rounded-full border-2 border-white/20" />
                    </motion.div>
                  </div>
                </div>

                {/* Aura Info & State Selector */}
                <div className="space-y-6">
                  <div className="bg-white/60 backdrop-blur-sm rounded-2xl p-5 border border-white/50">
                    <h3 className="text-lg text-gray-800 mb-2">Current State: {currentAura.name}</h3>
                    <p className="text-sm text-gray-600 mb-4">{currentAura.remedy}</p>
                    
                    {/* Mental State Selector */}
                    <div className="space-y-2">
                      <p className="text-xs text-gray-500 mb-3">How are you feeling right now?</p>
                      <Select value={mentalState} onValueChange={(value) => setMentalState(value as typeof mentalState)}>
                        <SelectTrigger className="w-full bg-white/80 border-white/50">
                          <SelectValue placeholder="Select your emotional state" />
                        </SelectTrigger>
                        <SelectContent className="bg-white/95 backdrop-blur-xl border-white/50">
                          <SelectItem value="none">— None</SelectItem>
                          <SelectItem value="sadness">😔 Sadness / Low Energy</SelectItem>
                          <SelectItem value="anxiety">😰 Anxiety / Fear</SelectItem>
                          <SelectItem value="anger">😡 Anger / Frustration</SelectItem>
                          <SelectItem value="exhaustion">😴 Exhaustion / Burnout</SelectItem>
                          <SelectItem value="confusion">😕 Confusion / Overthinking</SelectItem>
                          <SelectItem value="numbness">😶 Emotional Numbness</SelectItem>
                          <SelectItem value="stress">😤 Stress / Pressure</SelectItem>
                          <SelectItem value="overstimulation">🤯 Overstimulation / Digital Fatigue</SelectItem>
                          <SelectItem value="loneliness">😢 Loneliness / Isolation</SelectItem>
                          <SelectItem value="insecurity">😬 Insecurity / Self-Doubt</SelectItem>
                          <SelectItem value="resentment">😠 Resentment / Inner Conflict</SelectItem>
                          <SelectItem value="love">😍 Love / Compassion / Gratitude</SelectItem>
                          <SelectItem value="happiness">😊 Happiness / Contentment</SelectItem>
                          <SelectItem value="mindfulness">😇 Mindfulness / Spiritual Calm</SelectItem>
                          <SelectItem value="motivation">⚡ Motivation / Creative Flow</SelectItem>
                        </SelectContent>
                      </Select>
                    </div>
                  </div>

                  {/* Color Psychology Info */}
                  <div className="bg-white/60 backdrop-blur-sm rounded-2xl p-5 border border-white/50">
                    <h4 className="text-sm text-gray-700 mb-2">💡 Color Therapy</h4>
                    <p className="text-xs text-gray-600 leading-relaxed">
                      The colors you see are scientifically chosen based on color psychology to help regulate your emotions. 
                      Calming blues soothe anxiety, warm tones uplift mood, and balanced greens promote harmony.
                    </p>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </motion.div>

        <div className="grid md:grid-cols-3 gap-6 mb-8">
          {/* Dosha Balance Visualization */}
          <div className="md:col-span-2">
            {/* Glass card */}
            <div className="relative bg-white/40 backdrop-blur-xl rounded-3xl p-6 border border-white/50 shadow-xl">
              <div className="flex items-center justify-between mb-6">
                <h2 className="text-xl text-gray-800">Dosha Balance</h2>
                <Badge className="bg-purple-100 text-purple-700 border-0">
                  <Sparkles className="w-3 h-3 mr-1" />
                  AI Analyzed
                </Badge>
              </div>

              {/* Dosha Cards */}
              <div className="grid grid-cols-3 gap-4 mb-6">
                {(Object.keys(doshaData) as Array<keyof typeof doshaData>).map((dosha) => {
                  const data = doshaData[dosha];
                  const Icon = data.icon;
                  return (
                    <div
                      key={dosha}
                      onClick={() => setCurrentDosha(dosha)}
                      className={`cursor-pointer relative bg-gradient-to-br ${data.bgColor} backdrop-blur-sm rounded-2xl p-4 border ${
                        currentDosha === dosha ? 'border-white shadow-lg' : 'border-white/30'
                      } transition-all hover:scale-105`}
                    >
                      <div className={`inline-flex p-2 rounded-xl bg-gradient-to-br ${data.color} mb-2`}>
                        <Icon className="w-5 h-5 text-white" />
                      </div>
                      <p className="text-sm text-gray-700 mb-1">{data.name}</p>
                      <p className="text-xs text-gray-500 mb-2">{data.element}</p>
                      <div className="relative h-2 bg-white/50 rounded-full overflow-hidden">
                        <div
                          className={`h-full bg-gradient-to-r ${data.color} rounded-full transition-all duration-1000`}
                          style={{ width: `${data.level}%` }}
                        />
                      </div>
                      <p className="text-xs text-gray-600 mt-1">{data.level}%</p>
                    </div>
                  );
                })}
              </div>

              {/* Current Dosha Display */}
              <div className="relative">
                <div className={`bg-gradient-to-br ${doshaData[currentDosha].color} rounded-2xl p-6 text-white`}>
                  <div className="flex items-center gap-4">
                    <div>
                      {(() => {
                        const Icon = doshaData[currentDosha].icon;
                        return <Icon className="w-12 h-12" />;
                      })()}
                    </div>
                    <div>
                      <h3 className="text-2xl mb-1">{doshaData[currentDosha].name} Dominant</h3>
                      <p className="text-white/80">
                        Your {doshaData[currentDosha].name.toLowerCase()} energy is balanced. Keep maintaining your routine!
                      </p>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>

          {/* Quick Stats */}
          <div>
            <div className="relative bg-white/40 backdrop-blur-xl rounded-3xl p-6 border border-white/50 shadow-xl h-full">
              <h2 className="text-xl text-gray-800 mb-6">Today's Summary</h2>
              
              <div className="space-y-5">
                <div>
                  <div className="flex justify-between mb-2">
                    <span className="text-sm text-gray-700">Energy Level</span>
                    <Badge className="bg-gradient-to-r from-green-100 to-emerald-100 text-green-700 border-0">
                      High
                    </Badge>
                  </div>
                  <div className="relative h-2.5 bg-white/60 rounded-full overflow-hidden">
                    <div
                      className="h-full bg-gradient-to-r from-green-400 to-emerald-400 rounded-full transition-all duration-1000"
                      style={{ width: '82%' }}
                    />
                  </div>
                </div>

                <div>
                  <div className="flex justify-between mb-2">
                    <span className="text-sm text-gray-700">Stress Level</span>
                    <Badge className="bg-gradient-to-r from-blue-100 to-cyan-100 text-blue-700 border-0">
                      Low
                    </Badge>
                  </div>
                  <div className="relative h-2.5 bg-white/60 rounded-full overflow-hidden">
                    <div
                      className="h-full bg-gradient-to-r from-blue-400 to-cyan-400 rounded-full transition-all duration-1000"
                      style={{ width: '25%' }}
                    />
                  </div>
                </div>

                <div>
                  <div className="flex justify-between mb-2">
                    <span className="text-sm text-gray-700">Mindfulness</span>
                    <Badge className="bg-gradient-to-r from-purple-100 to-pink-100 text-purple-700 border-0">
                      Excellent
                    </Badge>
                  </div>
                  <div className="relative h-2.5 bg-white/60 rounded-full overflow-hidden">
                    <div
                      className="h-full bg-gradient-to-r from-purple-400 to-pink-400 rounded-full transition-all duration-1000"
                      style={{ width: '90%' }}
                    />
                  </div>
                </div>

                <div className="pt-4 border-t border-white/30">
                  <div className="flex items-center gap-3 p-3 rounded-xl bg-gradient-to-br from-purple-100/50 to-pink-100/50">
                    <TrendingUp className="w-5 h-5 text-purple-600" />
                    <div className="flex-1">
                      <p className="text-xs text-gray-600">Overall Wellness</p>
                      <p className="text-sm text-gray-800">+15% this week</p>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Quick Actions section removed for performance optimization */}

        {/* Today's Goals */}
        <div>
          <div className="relative bg-white/40 backdrop-blur-xl rounded-3xl p-6 border border-white/50 shadow-xl">
            <h2 className="text-xl text-gray-800 mb-6">Today's Wellness Goals</h2>
            <div className="grid md:grid-cols-2 gap-4">
              {[
                { task: 'Morning Meditation', time: '10 min', completed: true, color: 'from-purple-400 to-pink-400' },
                { task: 'Yoga Practice', time: '30 min', completed: true, color: 'from-blue-400 to-cyan-400' },
                { task: 'Log Meals', time: '3 meals', completed: wellnessGoals.meals, color: 'from-orange-400 to-amber-400' },
                { task: 'Evening Walk', time: '20 min', completed: false, color: 'from-green-400 to-emerald-400' },
              ].map((goal) => (
                <div
                  key={goal.task}
                  className={`relative flex items-center gap-4 p-4 rounded-2xl ${
                    goal.completed 
                      ? 'bg-white/60' 
                      : 'bg-gradient-to-br from-white/40 to-white/20'
                  } border border-white/50`}
                >
                  <div className={`flex-shrink-0 w-10 h-10 rounded-xl ${
                    goal.completed 
                      ? `bg-gradient-to-br ${goal.color}` 
                      : 'bg-white/60'
                  } flex items-center justify-center`}>
                    {goal.completed ? (
                      <span className="text-white text-lg">✓</span>
                    ) : (
                      <span className="text-gray-400 text-lg">○</span>
                    )}
                  </div>
                  <div className="flex-1">
                    <p className={`text-sm ${goal.completed ? 'line-through text-gray-500' : 'text-gray-800'}`}>
                      {goal.task}
                    </p>
                    <p className="text-xs text-gray-500">{goal.time}</p>
                  </div>
                  {!goal.completed && (
                    <Button size="sm" variant="ghost" className="text-xs">
                      Start
                    </Button>
                  )}
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>

      {/* Notification Dialog */}
      <Dialog open={showNotification} onOpenChange={setShowNotification}>
        <DialogContent className="bg-white/95 backdrop-blur-xl border-white/50">
          <DialogHeader>
            <DialogTitle className="flex items-center gap-2">
              <Sparkles className="w-5 h-5 text-purple-600" />
              Wellness Reminder
            </DialogTitle>
            <DialogDescription className="text-gray-600">
              Based on your current wellness state, we recommend:
            </DialogDescription>
          </DialogHeader>
          <div className="space-y-4">
            <div className="bg-gradient-to-br from-purple-50 to-pink-50 p-4 rounded-xl border border-purple-100">
              <p className="text-purple-900">
                ✨ Try a 5-minute breathing exercise to restore balance and enhance your energy flow.
              </p>
            </div>
            <Button 
              className="w-full bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-700 hover:to-pink-700" 
              onClick={() => {
                setShowNotification(false);
                onNavigate('yoga');
              }}
            >
              Start Pranayama Session
            </Button>
          </div>
        </DialogContent>
      </Dialog>

      {/* Streak Calendar Dialog */}
      <Dialog open={showStreakCalendar} onOpenChange={(open) => {
        setShowStreakCalendar(open);
        if (!open) {
          // Reset to current month when closing
          setStreakViewMonth(new Date().getMonth());
          setStreakViewYear(new Date().getFullYear());
        }
      }}>
        <DialogContent className="max-w-2xl max-h-[85vh] overflow-y-auto bg-white/95 backdrop-blur-xl border-white/50">
          <DialogHeader>
            <DialogTitle className="flex items-center gap-2">
              <Flame className="w-6 h-6 text-orange-600" />
              Your Wellness Journey
            </DialogTitle>
            <DialogDescription className="text-gray-600">
              Days you've visited Nirvami - Keep your streak alive! 🔥
            </DialogDescription>
          </DialogHeader>
          
          {/* Single Month View with Navigation */}
          <div className="space-y-6">
            <div className="bg-white/60 backdrop-blur-sm rounded-2xl p-6 border border-white/50">
              {/* Year */}
              <div className="text-center mb-2">
                <p className="text-sm text-gray-600">{streakViewYear}</p>
              </div>
              
              {/* Month navigation */}
              <div className="flex items-center justify-between mb-4">
                <Button
                  variant="ghost"
                  size="icon"
                  onClick={() => {
                    if (streakViewMonth === 0) {
                      setStreakViewMonth(11);
                      setStreakViewYear(streakViewYear - 1);
                    } else {
                      setStreakViewMonth(streakViewMonth - 1);
                    }
                  }}
                  className="hover:bg-white/60"
                >
                  <ChevronLeft className="w-5 h-5 text-gray-700" />
                </Button>
                
                <h3 className="text-lg text-gray-800">
                  {['January', 'February', 'March', 'April', 'May', 'June', 
                    'July', 'August', 'September', 'October', 'November', 'December'][streakViewMonth]}
                </h3>
                
                <Button
                  variant="ghost"
                  size="icon"
                  onClick={() => {
                    if (streakViewMonth === 11) {
                      setStreakViewMonth(0);
                      setStreakViewYear(streakViewYear + 1);
                    } else {
                      setStreakViewMonth(streakViewMonth + 1);
                    }
                  }}
                  className="hover:bg-white/60"
                >
                  <ChevronRight className="w-5 h-5 text-gray-700" />
                </Button>
              </div>
              
              {/* Day headers */}
              <div className="grid grid-cols-7 gap-2 mb-2">
                {['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'].map((day, i) => (
                  <div key={i} className="text-center text-sm text-gray-600 py-2">
                    {day}
                  </div>
                ))}
              </div>
              
              {/* Calendar days */}
              <div className="grid grid-cols-7 gap-2">
                {/* Empty cells for days before month starts */}
                {Array.from({ length: new Date(streakViewYear, streakViewMonth, 1).getDay() }).map((_, i) => (
                  <div key={`empty-${i}`} className="aspect-square" />
                ))}
                
                {/* Actual days of the month */}
                {Array.from({ length: new Date(streakViewYear, streakViewMonth + 1, 0).getDate() }, (_, dayIndex) => {
                  const day = dayIndex + 1;
                  const dateStr = `${streakViewYear}-${String(streakViewMonth + 1).padStart(2, '0')}-${String(day).padStart(2, '0')}`;
                  const isVisited = isDateVisited(dateStr);
                  const isToday = dateStr === new Date().toISOString().split('T')[0];
                  
                  return (
                    <div
                      key={day}
                      className={`aspect-square flex items-center justify-center text-sm rounded-xl transition-all ${
                        isVisited 
                          ? 'bg-gradient-to-br from-orange-400 to-red-500 text-white shadow-md hover:scale-105' 
                          : 'bg-gray-100 text-gray-400'
                      } ${
                        isToday ? 'ring-2 ring-purple-500 ring-offset-2' : ''
                      }`}
                      title={isVisited ? `Visited on ${dateStr}` : dateStr}
                    >
                      {day}
                    </div>
                  );
                })}
              </div>
            </div>
            
            {/* Legend */}
            <div className="flex items-center justify-center gap-6 p-4 bg-gradient-to-br from-purple-50 to-pink-50 rounded-xl">
              <div className="flex items-center gap-2">
                <div className="w-6 h-6 rounded-lg bg-gradient-to-br from-orange-400 to-red-500" />
                <span className="text-sm text-gray-700">Visited</span>
              </div>
              <div className="flex items-center gap-2">
                <div className="w-6 h-6 rounded-lg bg-gray-100" />
                <span className="text-sm text-gray-700">Not Visited</span>
              </div>
              <div className="flex items-center gap-2">
                <div className="w-6 h-6 rounded-lg bg-gray-100 ring-2 ring-purple-500 ring-offset-1" />
                <span className="text-sm text-gray-700">Today</span>
              </div>
            </div>
            
            {/* Stats */}
            <div className="grid grid-cols-3 gap-4">
              <div className="bg-white/60 backdrop-blur-sm rounded-xl p-4 text-center border border-white/50">
                <p className="text-2xl text-orange-600">{streak}</p>
                <p className="text-xs text-gray-600 mt-1">Current Streak</p>
              </div>
              <div className="bg-white/60 backdrop-blur-sm rounded-xl p-4 text-center border border-white/50">
                <p className="text-2xl text-purple-600">{getVisitedDates().length}</p>
                <p className="text-xs text-gray-600 mt-1">Total Days</p>
              </div>
              <div className="bg-white/60 backdrop-blur-sm rounded-xl p-4 text-center border border-white/50">
                <p className="text-2xl text-pink-600">{Math.round((getVisitedDates().length / 365) * 100)}%</p>
                <p className="text-xs text-gray-600 mt-1">Year Progress</p>
              </div>
            </div>
          </div>
        </DialogContent>
      </Dialog>
    </div>
  );
}