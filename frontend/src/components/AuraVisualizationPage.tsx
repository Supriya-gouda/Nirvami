import { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'motion/react';
import { Sparkles, Zap, Heart, Brain, Flame, Wind, Droplet, Leaf, Info } from 'lucide-react';
import { Navigation } from './Navigation';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { Badge } from './ui/badge';
import { Button } from './ui/button';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogDescription } from './ui/dialog';
import type { PageType, User } from '../App';
import api from '../services/api';
import type { AuraEntry } from '../types/api.types';

interface AuraVisualizationPageProps {
  user: User | null;
  onNavigate: (page: PageType) => void;
  onLogout?: () => void;
  onOpenNotifications?: () => void;
  refreshTrigger?: number; // Change this value to trigger refresh
}

interface AuraColor {
  name: string;
  color: string;
  gradient: string;
  innerGlow: string;
  meaning: string;
  traits: string[];
  icon: any;
  chakra: string;
  element: string;
}

export function AuraVisualizationPage({ user, onNavigate, onLogout, onOpenNotifications, refreshTrigger }: AuraVisualizationPageProps) {
  const [dynamicAura, setDynamicAura] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [showInfo, setShowInfo] = useState(false);
  const [selectedColor, setSelectedColor] = useState<AuraColor | null>(null);

  // Refresh when trigger changes (e.g., after mood submission)
  useEffect(() => {
    if (refreshTrigger && refreshTrigger > 0) {
      console.log('[AuraViz] Refresh triggered by mood submission');
      loadAura();
    }
  }, [refreshTrigger]);

  // Fetch current aura - loads once on mount
  const loadAura = async () => {
    try {
      setLoading(true);
      const data = await api.getCurrentAura();
      console.log('[AuraViz] Loaded aura:', data);
      setDynamicAura(data);
    } catch (err) {
      console.error('[AuraViz] Failed to load aura:', err);
      // Fallback
      setDynamicAura({
        auraName: 'Neutral Grey Aura',
        emotionLabel: 'No mood logged yet',
        colorCode: 'grey',
        gradient: ['#9ca3af', '#6b7280', '#4b5563'],
        traits: ['Neutral', 'Balanced', 'Calm', 'Stillness'],
        description: 'Neutral, balanced, and centered',
        chakra: 'All Chakras',
        element: 'Earth',
        intensity: 50
      });
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadAura();
  }, []);

  const auraColors: Record<string, AuraColor> = {
    red: {
      name: 'Red',
      color: '#E53935',
      gradient: 'from-red-400 via-red-500 to-red-600',
      innerGlow: 'from-red-500 to-red-700',
      meaning: 'Energy & Courage',
      traits: ['Energetic', 'Courageous', 'Grounding', 'Motivated'],
      icon: Flame,
      chakra: 'Root Chakra',
      element: 'Fire'
    },
    orange: {
      name: 'Orange',
      color: '#FB8C00',
      gradient: 'from-orange-400 via-orange-500 to-orange-600',
      innerGlow: 'from-orange-500 to-orange-700',
      meaning: 'Joy & Playfulness',
      traits: ['Joyful', 'Playful', 'Creative', 'Social'],
      icon: Sparkles,
      chakra: 'Sacral Chakra',
      element: 'Fire'
    },
    yellow: {
      name: 'Yellow',
      color: '#FDD835',
      gradient: 'from-yellow-300 via-yellow-400 to-yellow-500',
      innerGlow: 'from-yellow-400 to-yellow-600',
      meaning: 'Optimism & Clarity',
      traits: ['Optimistic', 'Clear-minded', 'Confident', 'Bright'],
      icon: Zap,
      chakra: 'Solar Plexus',
      element: 'Fire'
    },
    green: {
      name: 'Green',
      color: '#66BB6A',
      gradient: 'from-green-400 via-green-500 to-green-600',
      innerGlow: 'from-green-500 to-green-700',
      meaning: 'Balance & Healing',
      traits: ['Balanced', 'Healing', 'Compassionate', 'Growing'],
      icon: Leaf,
      chakra: 'Heart Chakra',
      element: 'Earth'
    },
    blue: {
      name: 'Blue',
      color: '#42A5F5',
      gradient: 'from-blue-400 via-blue-500 to-blue-600',
      innerGlow: 'from-blue-500 to-blue-700',
      meaning: 'Calm & Communication',
      traits: ['Calm', 'Communicative', 'Trustworthy', 'Peaceful'],
      icon: Droplet,
      chakra: 'Throat Chakra',
      element: 'Water'
    },
    teal: {
      name: 'Teal',
      color: '#26A69A',
      gradient: 'from-teal-400 via-teal-500 to-teal-600',
      innerGlow: 'from-teal-500 to-teal-700',
      meaning: 'Emotional Healing',
      traits: ['Healing', 'Safe', 'Vulnerable', 'Processing'],
      icon: Heart,
      chakra: 'Heart-Throat Bridge',
      element: 'Water'
    },
    indigo: {
      name: 'Indigo',
      color: '#1A237E',
      gradient: 'from-indigo-400 via-indigo-500 to-indigo-600',
      innerGlow: 'from-indigo-500 to-indigo-700',
      meaning: 'Depth & Protection',
      traits: ['Deep', 'Protected', 'Contained', 'Reflective'],
      icon: Brain,
      chakra: 'Third Eye',
      element: 'Light'
    },
    violet: {
      name: 'Violet',
      color: '#8E24AA',
      gradient: 'from-violet-400 via-violet-500 to-violet-600',
      innerGlow: 'from-violet-500 to-violet-700',
      meaning: 'Insight & Transformation',
      traits: ['Insightful', 'Intuitive', 'Transformative', 'Spiritual'],
      icon: Sparkles,
      chakra: 'Crown Chakra',
      element: 'Ether'
    },
    pink: {
      name: 'Pink',
      color: '#EC407A',
      gradient: 'from-pink-400 via-pink-500 to-pink-600',
      innerGlow: 'from-pink-500 to-pink-700',
      meaning: 'Self-Love & Gentleness',
      traits: ['Loving', 'Gentle', 'Compassionate', 'Nurturing'],
      icon: Heart,
      chakra: 'Heart Chakra',
      element: 'Water'
    },
    white: {
      name: 'White',
      color: '#F5F5F5',
      gradient: 'from-gray-100 via-white to-gray-200',
      innerGlow: 'from-gray-200 to-gray-400',
      meaning: 'Clarity & Reset',
      traits: ['Clear', 'Spacious', 'Reset', 'Open'],
      icon: Sparkles,
      chakra: 'All Chakras',
      element: 'Light'
    },
    grey: {
      name: 'Grey',
      color: '#9E9E9E',
      gradient: 'from-gray-400 via-gray-500 to-gray-600',
      innerGlow: 'from-gray-500 to-gray-700',
      meaning: 'Neutral & Balanced',
      traits: ['Neutral', 'Balanced', 'Calm', 'Stillness'],
      icon: Wind,
      chakra: 'All Chakras',
      element: 'Earth'
    },
    silver: {
      name: 'Silver',
      color: '#C0C0C0',
      gradient: 'from-gray-300 via-gray-400 to-gray-500',
      innerGlow: 'from-gray-400 to-gray-600',
      meaning: 'Abundance & Flow',
      traits: ['Abundant', 'Flowing', 'Intuitive', 'Receptive'],
      icon: Wind,
      chakra: 'Crown Chakra',
      element: 'Air'
    }
  };

  const currentAuraColor = dynamicAura ? auraColors[dynamicAura.colorCode] || auraColors.grey : auraColors.grey;
  const Icon = currentAuraColor.icon;
  
  // Use dynamic gradient from backend if available
  const currentGradient = dynamicAura?.gradient 
    ? `linear-gradient(135deg, ${dynamicAura.gradient.join(', ')})` 
    : 'linear-gradient(135deg, #9ca3af, #6b7280, #4b5563)';

  const handleColorInfo = (color: AuraColor) => {
    setSelectedColor(color);
    setShowInfo(true);
  };

  // Show loading state
  if (loading && !dynamicAura) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-purple-50 via-blue-50 to-pink-50">
        <Navigation currentPage="aura" onNavigate={onNavigate} onLogout={onLogout} user={user} onOpenNotifications={onOpenNotifications} />
        <div className="max-w-7xl mx-auto p-8">
          <div className="flex items-center justify-center min-h-[60vh]">
            <div className="text-center">
              <div className="animate-spin rounded-full h-16 w-16 border-b-2 border-purple-600 mx-auto mb-4"></div>
              <p className="text-gray-600">Loading your aura...</p>
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-purple-50 via-blue-50 to-pink-50">
      <Navigation currentPage="aura" onNavigate={onNavigate} onLogout={onLogout} user={user} onOpenNotifications={onOpenNotifications} />

      <div className="max-w-7xl mx-auto p-8">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="mb-8"
        >
          <h1 
            className="text-4xl font-bold mb-2"
            style={{
              background: 'linear-gradient(to right, #9333ea, #db2777)',
              WebkitBackgroundClip: 'text',
              WebkitTextFillColor: 'transparent',
              backgroundClip: 'text',
            }}
          >
            Aura Visualization
          </h1>
          <p className="text-gray-600">Your energetic signature and emotional state</p>
        </motion.div>

        {/* Current Aura Display - Spinning Ball with Info Cards */}
        <motion.div
          initial={{ opacity: 0, scale: 0.9 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ delay: 0.1 }}
          className="mb-8"
        >
          <div className="space-y-4">
              {/* Aura Name & Description Card with Emoji */}
              {dynamicAura && (
                <motion.div
                  initial={{ opacity: 0, scale: 0.9 }}
                  animate={{ opacity: 1, scale: 1 }}
                  transition={{ delay: 0.2 }}
                >
                  <Card 
                    className="border-none shadow-lg"
                    style={{
                      background: dynamicAura?.gradient 
                        ? `linear-gradient(135deg, ${dynamicAura.gradient.join(', ')})` 
                        : 'linear-gradient(135deg, #9ca3af, #6b7280, #4b5563)'
                    }}
                  >
                    <CardContent className="p-6 text-center">
                      <div className="text-5xl mb-3">
                        {(() => {
                          const emotionLabel = dynamicAura?.emotionLabel?.toLowerCase() || '';
                          const emojiMap: Record<string, string> = {
                            'happy': '😊',
                            'calm': '😌',
                            'sad': '😢',
                            'anxious': '😰',
                            'tired': '😴',
                            'frustrated': '😤',
                            'grateful': '🤗',
                            'neutral': '😐',
                            'angry': '😡',
                            'low-energy': '😔',
                            'low energy': '😔',
                            'energized': '⚡',
                            'confused': '😕'
                          };
                          return emojiMap[emotionLabel] || '✨';
                        })()}
                      </div>
                      <h2 className="text-2xl font-bold text-white mb-2">
                        {dynamicAura?.auraName || 'Loading...'}
                      </h2>
                      <p className="text-lg text-white/90">
                        {dynamicAura?.description || 'Analyzing your energy...'}
                      </p>
                      {dynamicAura?.emotionLabel && 
                       dynamicAura.emotionLabel !== 'No recent mood logged' && 
                       dynamicAura.emotionLabel !== 'No recent mood (>24h)' && 
                       dynamicAura.emotionLabel !== 'No mood logged yet' && (
                        <p className="text-sm text-white/80 mt-3">
                          💫 Based on: <span className="font-bold">{dynamicAura.emotionLabel}</span>
                        </p>
                      )}
                    </CardContent>
                  </Card>
                </motion.div>
              )}

              {/* Intensity & Chakra */}
              <Card className="bg-white/80 backdrop-blur-sm shadow-lg">
                <CardContent className="p-6">
                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <p className="text-sm text-gray-600 mb-2">Intensity</p>
                      <p className="text-4xl font-bold bg-gradient-to-r from-purple-600 to-pink-600 bg-clip-text text-transparent">
                        {dynamicAura?.intensity || 50}%
                      </p>
                    </div>
                    <div>
                      <p className="text-sm text-gray-600 mb-2">Chakra</p>
                      <p className="text-xl font-semibold text-gray-800">{dynamicAura?.chakra || 'All Chakras'}</p>
                    </div>
                  </div>
                </CardContent>
              </Card>

              {/* Aura Traits */}
              <Card className="bg-white/80 backdrop-blur-sm shadow-lg">
                <CardContent className="p-6">
                  <p className="text-sm text-gray-600 mb-3 font-semibold">Aura Traits</p>
                  <div className="flex flex-wrap gap-2">
                    {(dynamicAura?.traits || currentAuraColor.traits).map((trait: string, idx: number) => (
                      <span
                        key={idx}
                        className="px-3 py-1.5 text-sm font-medium bg-gradient-to-r from-purple-100 to-pink-100 text-purple-700 rounded-lg border border-purple-200"
                      >
                        {trait}
                      </span>
                    ))}
                  </div>
                </CardContent>
              </Card>

              {/* Element */}
              {dynamicAura?.element && (
                <Card className="bg-white/80 backdrop-blur-sm shadow-lg">
                  <CardContent className="p-6">
                    <p className="text-sm text-gray-600 mb-2 font-semibold">Element</p>
                    <p className="text-xl font-semibold text-gray-800">🌿 {dynamicAura.element}</p>
                  </CardContent>
                </Card>
              )}

              {/* Status Messages */}
              {dynamicAura?.emotionLabel === 'No recent mood logged' && (
                <Card className="bg-purple-50 border-purple-200 shadow-lg">
                  <CardContent className="p-6">
                    <p className="text-sm text-purple-700">✨ Log your mood to activate your personalized aura</p>
                  </CardContent>
                </Card>
              )}
              
              {dynamicAura?.emotionLabel === 'No recent mood (>24h)' && (
                <Card className="bg-orange-50 border-orange-200 shadow-lg">
                  <CardContent className="p-6">
                    <p className="text-sm text-orange-700">⏰ Your aura has reset to neutral. Log a new mood to reactivate!</p>
                  </CardContent>
                </Card>
              )}
            </div>
        </motion.div>

        {/* Therapeutic Information Cards - Below Main Card */}
        {dynamicAura?.why && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.15 }}
            className="mb-8"
          >
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              {/* Why This Color Card */}
              <Card 
                className="text-white border-none shadow-xl overflow-hidden hover:shadow-2xl transition-all"
                style={{
                  background: currentGradient
                }}
              >
                <CardContent className="p-6">
                  <div className="flex items-start gap-3 mb-4">
                    <div className="w-12 h-12 rounded-xl bg-white/30 flex items-center justify-center text-2xl flex-shrink-0 shadow-md">
                      🔍
                    </div>
                    <h3 className="text-xl font-bold text-white drop-shadow-lg pt-2">
                      Why This Color?
                    </h3>
                  </div>
                  <p className="text-base leading-relaxed text-white/95 font-medium">
                    {dynamicAura.why}
                  </p>
                </CardContent>
              </Card>

              {/* What This Color Does Card */}
              {dynamicAura?.whatItDoes && (
                <Card 
                  className="text-white border-none shadow-xl overflow-hidden hover:shadow-2xl transition-all"
                  style={{
                    background: currentGradient
                  }}
                >
                  <CardContent className="p-6">
                    <div className="flex items-start gap-3 mb-4">
                      <div className="w-12 h-12 rounded-xl bg-white/30 flex items-center justify-center text-2xl flex-shrink-0 shadow-md">
                        ✨
                      </div>
                      <h3 className="text-xl font-bold text-white drop-shadow-lg pt-2">
                        What This Color Does
                      </h3>
                    </div>
                    <p className="text-base leading-relaxed text-white/95 font-medium">
                      {dynamicAura.whatItDoes}
                    </p>
                  </CardContent>
                </Card>
              )}

              {/* Purpose Card */}
              {dynamicAura?.purpose && (
                <Card 
                  className="text-white border-none shadow-xl overflow-hidden hover:shadow-2xl transition-all"
                  style={{
                    background: currentGradient
                  }}
                >
                  <CardContent className="p-6">
                    <div className="flex items-start gap-3 mb-4">
                      <div className="w-12 h-12 rounded-xl bg-white/30 flex items-center justify-center text-2xl flex-shrink-0 shadow-md">
                        🎯
                      </div>
                      <h3 className="text-xl font-bold text-white drop-shadow-lg pt-2">
                        Purpose (Healing Intent)
                      </h3>
                    </div>
                    <p className="text-base leading-relaxed text-white/95 font-medium">
                      {dynamicAura.purpose}
                    </p>
                  </CardContent>
                </Card>
              )}
            </div>
          </motion.div>
        )}

        {/* Aura Color Palette */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2 }}
          className="mb-8"
        >
          <Card>
            <CardHeader>
              <CardTitle>Aura Color Meanings</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-5 gap-4">
                {Object.values(auraColors).map((auraColor, idx) => {
                  const ColorIcon = auraColor.icon;
                  const getGradient = (gradientClass: string) => {
                    const gradientMap: Record<string, string> = {
                      'from-red-400 via-red-500 to-red-600': 'linear-gradient(135deg, #f87171, #ef4444, #dc2626)',
                      'from-orange-400 via-orange-500 to-orange-600': 'linear-gradient(135deg, #fb923c, #f97316, #ea580c)',
                      'from-yellow-300 via-yellow-400 to-yellow-500': 'linear-gradient(135deg, #fde047, #facc15, #eab308)',
                      'from-yellow-400 via-yellow-500 to-yellow-600': 'linear-gradient(135deg, #facc15, #eab308, #ca8a04)',
                      'from-green-400 via-green-500 to-green-600': 'linear-gradient(135deg, #4ade80, #22c55e, #16a34a)',
                      'from-blue-400 via-blue-500 to-blue-600': 'linear-gradient(135deg, #60a5fa, #3b82f6, #2563eb)',
                      'from-teal-400 via-teal-500 to-teal-600': 'linear-gradient(135deg, #2dd4bf, #14b8a6, #0d9488)',
                      'from-indigo-400 via-indigo-500 to-indigo-600': 'linear-gradient(135deg, #818cf8, #6366f1, #4f46e5)',
                      'from-violet-400 via-violet-500 to-violet-600': 'linear-gradient(135deg, #a78bfa, #8b5cf6, #7c3aed)',
                      'from-pink-400 via-pink-500 to-pink-600': 'linear-gradient(135deg, #f472b6, #ec4899, #db2777)',
                      'from-gray-100 via-white to-gray-200': 'linear-gradient(135deg, #f3f4f6, #ffffff, #e5e7eb)',
                      'from-gray-400 via-gray-500 to-gray-600': 'linear-gradient(135deg, #9ca3af, #6b7280, #4b5563)',
                      'from-gray-300 via-gray-400 to-gray-500': 'linear-gradient(135deg, #d1d5db, #9ca3af, #6b7280)',
                    };
                    return gradientMap[gradientClass] || 'linear-gradient(135deg, #9ca3af, #6b7280)';
                  };
                  return (
                    <motion.button
                      key={auraColor.name}
                      onClick={() => handleColorInfo(auraColor)}
                      style={{
                        background: getGradient(auraColor.gradient),
                        borderRadius: '12px',
                        padding: '16px',
                        color: auraColor.name === 'White' ? '#1f2937' : 'white',
                        border: 'none',
                        boxShadow: '0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05)',
                        cursor: 'pointer',
                        transition: 'all 0.2s ease-in-out',
                      }}
                      whileHover={{ scale: 1.05 }}
                      whileTap={{ scale: 0.95 }}
                      initial={{ opacity: 0, y: 20 }}
                      animate={{ opacity: 1, y: 0 }}
                      transition={{ delay: 0.3 + idx * 0.05 }}
                      onMouseEnter={(e) => {
                        e.currentTarget.style.boxShadow = '0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04)';
                      }}
                      onMouseLeave={(e) => {
                        e.currentTarget.style.boxShadow = '0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05)';
                      }}
                    >
                      <ColorIcon className="w-8 h-8 mb-2 mx-auto" />
                      <p className="font-semibold">{auraColor.name}</p>
                      <p className="text-xs opacity-80 mt-1">{auraColor.meaning}</p>
                    </motion.button>
                  );
                })}
              </div>
            </CardContent>
          </Card>
        </motion.div>

        {/* Aura Types */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.3 }}
        >
          <Card>
            <CardHeader>
              <CardTitle>Understanding Your Aura</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="bg-purple-50 p-4 rounded-lg">
                <h3 className="font-semibold text-purple-900 mb-2">What is an Aura?</h3>
                <p className="text-gray-700 text-sm">
                  Your aura is an energetic field that surrounds your body, reflecting your emotional, mental, and spiritual state.
                  It changes based on your thoughts, feelings, and overall wellness.
                </p>
              </div>

              <div className="bg-blue-50 p-4 rounded-lg">
                <h3 className="font-semibold text-blue-900 mb-2">How We Calculate Your Aura</h3>
                <p className="text-gray-700 text-sm">
                  We analyze your emotions, wellness metrics, and energy levels to determine your dominant aura color.
                  This visualization updates daily based on your logged activities and emotional state.
                </p>
              </div>

              <div className="bg-green-50 p-4 rounded-lg">
                <h3 className="font-semibold text-green-900 mb-2">Improving Your Aura</h3>
                <ul className="text-gray-700 text-sm space-y-1 list-disc list-inside">
                  <li>Practice daily meditation and mindfulness</li>
                  <li>Maintain positive emotional states</li>
                  <li>Engage in activities that align with your dosha</li>
                  <li>Log your wellness activities consistently</li>
                  <li>Stay balanced in all aspects of life</li>
                </ul>
              </div>
            </CardContent>
          </Card>
        </motion.div>
      </div>

      {/* Aura Color Info Dialog */}
      <Dialog open={showInfo} onOpenChange={setShowInfo}>
        <DialogContent 
          className="text-white border-none"
          style={selectedColor ? {
            background: (() => {
              const gradientMap: Record<string, string> = {
                'from-red-400 via-red-500 to-red-600': 'linear-gradient(135deg, #f87171, #ef4444, #dc2626)',
                'from-orange-400 via-orange-500 to-orange-600': 'linear-gradient(135deg, #fb923c, #f97316, #ea580c)',
                'from-yellow-300 via-yellow-400 to-yellow-500': 'linear-gradient(135deg, #fde047, #facc15, #eab308)',
                'from-yellow-400 via-yellow-500 to-yellow-600': 'linear-gradient(135deg, #facc15, #eab308, #ca8a04)',
                'from-green-400 via-green-500 to-green-600': 'linear-gradient(135deg, #4ade80, #22c55e, #16a34a)',
                'from-blue-400 via-blue-500 to-blue-600': 'linear-gradient(135deg, #60a5fa, #3b82f6, #2563eb)',
                'from-teal-400 via-teal-500 to-teal-600': 'linear-gradient(135deg, #2dd4bf, #14b8a6, #0d9488)',
                'from-indigo-400 via-indigo-500 to-indigo-600': 'linear-gradient(135deg, #818cf8, #6366f1, #4f46e5)',
                'from-violet-400 via-violet-500 to-violet-600': 'linear-gradient(135deg, #a78bfa, #8b5cf6, #7c3aed)',
                'from-pink-400 via-pink-500 to-pink-600': 'linear-gradient(135deg, #f472b6, #ec4899, #db2777)',
                'from-gray-100 via-white to-gray-200': 'linear-gradient(135deg, #f3f4f6, #ffffff, #e5e7eb)',
                'from-gray-400 via-gray-500 to-gray-600': 'linear-gradient(135deg, #9ca3af, #6b7280, #4b5563)',
                'from-gray-300 via-gray-400 to-gray-500': 'linear-gradient(135deg, #d1d5db, #9ca3af, #6b7280)',
              };
              return gradientMap[selectedColor.gradient] || 'linear-gradient(135deg, #9ca3af, #6b7280)';
            })(),
            color: selectedColor.name === 'White' ? '#1f2937' : 'white',
          } : {}}
        >
          {selectedColor && (
            <>
              <DialogHeader>
                <DialogTitle 
                  className="text-3xl flex items-center gap-2"
                  style={{ color: selectedColor.name === 'White' ? '#1f2937' : 'white' }}
                >
                  <selectedColor.icon className="w-8 h-8" />
                  {selectedColor.name} Aura
                </DialogTitle>
                <DialogDescription 
                  className="text-lg"
                  style={{ 
                    color: selectedColor.name === 'White' ? '#374151' : 'white',
                    opacity: 0.9 
                  }}
                >
                  {selectedColor.meaning}
                </DialogDescription>
              </DialogHeader>
              <div className="space-y-4 mt-4">
                <div>
                  <h4 
                    className="font-semibold mb-2"
                    style={{ color: selectedColor.name === 'White' ? '#1f2937' : 'white' }}
                  >
                    Characteristics
                  </h4>
                  <div className="flex flex-wrap gap-2">
                    {selectedColor.traits.map((trait, idx) => (
                      <span
                        key={idx}
                        style={{
                          display: 'inline-flex',
                          alignItems: 'center',
                          justifyContent: 'center',
                          padding: '4px 8px',
                          fontSize: '12px',
                          fontWeight: '500',
                          borderRadius: '6px',
                          backgroundColor: selectedColor.name === 'White' ? 'rgba(31, 41, 55, 0.2)' : 'rgba(255, 255, 255, 0.3)',
                          color: selectedColor.name === 'White' ? '#1f2937' : 'white',
                          border: selectedColor.name === 'White' ? '1px solid rgba(31, 41, 55, 0.3)' : '1px solid rgba(255, 255, 255, 0.5)',
                        }}
                      >
                        {trait}
                      </span>
                    ))}
                  </div>
                </div>
                <div className="grid grid-cols-2 gap-4">
                  <div 
                    className="backdrop-blur-sm rounded-lg p-3"
                    style={{
                      backgroundColor: selectedColor.name === 'White' ? 'rgba(31, 41, 55, 0.1)' : 'rgba(255, 255, 255, 0.2)',
                    }}
                  >
                    <p 
                      className="text-sm mb-1"
                      style={{ 
                        color: selectedColor.name === 'White' ? '#6b7280' : 'white',
                        opacity: 0.8 
                      }}
                    >
                      Associated Chakra
                    </p>
                    <p 
                      className="font-semibold"
                      style={{ color: selectedColor.name === 'White' ? '#1f2937' : 'white' }}
                    >
                      {selectedColor.chakra}
                    </p>
                  </div>
                  <div 
                    className="backdrop-blur-sm rounded-lg p-3"
                    style={{
                      backgroundColor: selectedColor.name === 'White' ? 'rgba(31, 41, 55, 0.1)' : 'rgba(255, 255, 255, 0.2)',
                    }}
                  >
                    <p 
                      className="text-sm mb-1"
                      style={{ 
                        color: selectedColor.name === 'White' ? '#6b7280' : 'white',
                        opacity: 0.8 
                      }}
                    >
                      Element
                    </p>
                    <p 
                      className="font-semibold"
                      style={{ color: selectedColor.name === 'White' ? '#1f2937' : 'white' }}
                    >
                      {selectedColor.element}
                    </p>
                  </div>
                </div>
              </div>
            </>
          )}
        </DialogContent>
      </Dialog>
    </div>
  );
}
