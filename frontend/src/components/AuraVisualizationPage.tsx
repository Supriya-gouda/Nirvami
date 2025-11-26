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

export function AuraVisualizationPage({ user, onNavigate, onLogout, onOpenNotifications }: AuraVisualizationPageProps) {
  const [currentAura, setCurrentAura] = useState<AuraEntry | null>(null);
  const [loading, setLoading] = useState(true);
  const [showInfo, setShowInfo] = useState(false);
  const [selectedColor, setSelectedColor] = useState<AuraColor | null>(null);

  // Fetch current aura from backend
  useEffect(() => {
    const loadAura = async () => {
      try {
        setLoading(true);
        const data = await api.getTodayAura();
        setCurrentAura(data);
      } catch (err) {
        console.warn('Failed to load aura, using fallback', err);
        // Fallback aura
        setCurrentAura({
          id: '1',
          user_id: 'test',
          date: new Date().toISOString().split('T')[0],
          color: 'grey',
          intensity: 50,
          glow_level: 50,
          aura_type: 'balanced',
          emotion_basis: {},
          created_at: new Date().toISOString()
        });
      } finally {
        setLoading(false);
      }
    };

    loadAura();

    // Auto-refresh every 10 seconds to catch updates
    const interval = setInterval(loadAura, 10000);
    return () => clearInterval(interval);
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

  const currentAuraColor = currentAura ? auraColors[currentAura.color] || auraColors.blue : auraColors.blue;
  const Icon = currentAuraColor.icon;

  const handleColorInfo = (color: AuraColor) => {
    setSelectedColor(color);
    setShowInfo(true);
  };

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

        {/* Current Aura Display */}
        <motion.div
          initial={{ opacity: 0, scale: 0.9 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ delay: 0.1 }}
          className="mb-8"
        >
          <Card 
            className="text-white border-none shadow-2xl overflow-hidden"
            style={{
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
                return gradientMap[currentAuraColor.gradient] || 'linear-gradient(135deg, #9ca3af, #6b7280)';
              })(),
            }}
          >
            <CardContent className="p-8">
              <div className="flex flex-col md:flex-row items-center gap-8">
                {/* Aura Visualization Circle */}
                <div className="relative">
                  <motion.div
                    className="w-64 h-64 rounded-full shadow-2xl relative"
                    style={{
                      background: (() => {
                        const innerGlowMap: Record<string, string> = {
                          'from-red-500 to-red-700': 'linear-gradient(135deg, #ef4444, #b91c1c)',
                          'from-orange-500 to-orange-700': 'linear-gradient(135deg, #f97316, #c2410c)',
                          'from-yellow-400 to-yellow-600': 'linear-gradient(135deg, #facc15, #ca8a04)',
                          'from-yellow-500 to-yellow-700': 'linear-gradient(135deg, #eab308, #a16207)',
                          'from-green-500 to-green-700': 'linear-gradient(135deg, #22c55e, #15803d)',
                          'from-blue-500 to-blue-700': 'linear-gradient(135deg, #3b82f6, #1d4ed8)',
                          'from-teal-500 to-teal-700': 'linear-gradient(135deg, #14b8a6, #0f766e)',
                          'from-indigo-500 to-indigo-700': 'linear-gradient(135deg, #6366f1, #4338ca)',
                          'from-violet-500 to-violet-700': 'linear-gradient(135deg, #8b5cf6, #6d28d9)',
                          'from-pink-500 to-pink-700': 'linear-gradient(135deg, #ec4899, #be185d)',
                          'from-gray-200 to-gray-400': 'linear-gradient(135deg, #e5e7eb, #9ca3af)',
                          'from-gray-500 to-gray-700': 'linear-gradient(135deg, #6b7280, #374151)',
                          'from-gray-400 to-gray-600': 'linear-gradient(135deg, #9ca3af, #4b5563)',
                        };
                        return innerGlowMap[currentAuraColor.innerGlow] || 'linear-gradient(135deg, #6b7280, #374151)';
                      })(),
                    }}
                    animate={{
                      boxShadow: [
                        `0 0 60px ${currentAuraColor.color}`,
                        `0 0 80px ${currentAuraColor.color}`,
                        `0 0 60px ${currentAuraColor.color}`
                      ]
                    }}
                    transition={{ duration: 3, repeat: Infinity }}
                  >
                    <div className="absolute inset-0 flex items-center justify-center">
                      <Icon className="w-32 h-32 text-white opacity-90" />
                    </div>

                    {/* Pulsing rings */}
                    <motion.div
                      className="absolute inset-0 rounded-full border-4 border-white opacity-30"
                      animate={{ scale: [1, 1.2, 1], opacity: [0.3, 0, 0.3] }}
                      transition={{ duration: 2, repeat: Infinity }}
                    />
                    <motion.div
                      className="absolute inset-0 rounded-full border-4 border-white opacity-20"
                      animate={{ scale: [1, 1.4, 1], opacity: [0.2, 0, 0.2] }}
                      transition={{ duration: 2, repeat: Infinity, delay: 0.5 }}
                    />
                  </motion.div>
                </div>

                {/* Aura Details */}
                <div className="flex-1 text-center md:text-left">
                  <h2 className="text-4xl font-bold mb-2">{currentAuraColor.name} Aura</h2>
                  <p className="text-2xl mb-4 opacity-90">{currentAuraColor.meaning}</p>

                  <div className="grid grid-cols-2 gap-4 mb-6">
                    <div className="bg-white/20 backdrop-blur-sm rounded-lg p-4">
                      <p className="text-sm opacity-80 mb-1">Intensity</p>
                      <p className="text-3xl font-bold">{currentAura ? Math.round(currentAura.intensity) : 75}%</p>
                    </div>
                    <div className="bg-white/20 backdrop-blur-sm rounded-lg p-4">
                      <p className="text-sm opacity-80 mb-1">Glow Level</p>
                      <p className="text-3xl font-bold">{currentAura ? Math.round(currentAura.glow_level || 0) : 80}%</p>
                    </div>
                  </div>

                  <div className="mb-6">
                    <p className="text-sm opacity-80 mb-2">Dominant Traits</p>
                    <div className="flex flex-wrap gap-2">
                      {currentAuraColor.traits.map((trait, idx) => (
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
                            backgroundColor: currentAuraColor.name === 'White' ? 'rgba(31, 41, 55, 0.2)' : 'rgba(255, 255, 255, 0.3)',
                            color: currentAuraColor.name === 'White' ? '#1f2937' : 'white',
                            border: currentAuraColor.name === 'White' ? '1px solid rgba(31, 41, 55, 0.3)' : '1px solid rgba(255, 255, 255, 0.5)',
                          }}
                        >
                          {trait}
                        </span>
                      ))}
                    </div>
                  </div>

                  <div className="flex gap-4 text-sm">
                    <div className="bg-white/20 backdrop-blur-sm rounded-lg px-4 py-2">
                      <strong>Chakra:</strong> {currentAuraColor.chakra}
                    </div>
                    <div className="bg-white/20 backdrop-blur-sm rounded-lg px-4 py-2">
                      <strong>Element:</strong> {currentAuraColor.element}
                    </div>
                  </div>

                  {/* Emotion Basis */}
                  {currentAura?.emotion_basis && Object.keys(currentAura.emotion_basis).length > 0 && (
                    <div className="mt-6">
                      <p className="text-sm opacity-80 mb-2">Emotional Influences</p>
                      <div className="space-y-2">
                        {Object.entries(currentAura.emotion_basis)
                          .sort(([, a], [, b]) => (b as number) - (a as number))
                          .slice(0, 5)
                          .map(([emotion, value], idx) => (
                            <div key={emotion} className="bg-white/20 backdrop-blur-sm rounded-lg p-2">
                              <div className="flex justify-between items-center mb-1">
                                <span className="text-sm capitalize">{emotion}</span>
                                <span className="text-sm font-semibold">{Math.round((value as number) * 100)}%</span>
                              </div>
                              <div className="h-1.5 bg-white/30 rounded-full overflow-hidden">
                                <motion.div
                                  className="h-full bg-white"
                                  initial={{ width: 0 }}
                                  animate={{ width: `${(value as number) * 100}%` }}
                                  transition={{ duration: 0.8, delay: 0.3 + idx * 0.1 }}
                                />
                              </div>
                            </div>
                          ))}
                      </div>
                    </div>
                  )}
                </div>
              </div>
            </CardContent>
          </Card>
        </motion.div>

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
