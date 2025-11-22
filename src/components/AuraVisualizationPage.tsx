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
          color: 'blue',
          intensity: 75,
          glow_level: 80,
          aura_type: 'calm',
          emotion_basis: {},
          created_at: new Date().toISOString()
        });
      } finally {
        setLoading(false);
      }
    };

    loadAura();
  }, []);

  const auraColors: Record<string, AuraColor> = {
    red: {
      name: 'Red',
      color: '#FF5757',
      gradient: 'from-red-400 via-red-500 to-red-600',
      innerGlow: 'from-red-500 to-red-700',
      meaning: 'Passion & Energy',
      traits: ['Energetic', 'Strong-willed', 'Passionate', 'Courageous'],
      icon: Flame,
      chakra: 'Root Chakra',
      element: 'Fire'
    },
    orange: {
      name: 'Orange',
      color: '#FF8C42',
      gradient: 'from-orange-400 via-orange-500 to-orange-600',
      innerGlow: 'from-orange-500 to-orange-700',
      meaning: 'Creativity & Joy',
      traits: ['Creative', 'Adventurous', 'Confident', 'Enthusiastic'],
      icon: Sparkles,
      chakra: 'Sacral Chakra',
      element: 'Fire'
    },
    yellow: {
      name: 'Yellow',
      color: '#FFD93D',
      gradient: 'from-yellow-300 via-yellow-400 to-yellow-500',
      innerGlow: 'from-yellow-400 to-yellow-600',
      meaning: 'Optimism & Intellect',
      traits: ['Optimistic', 'Intelligent', 'Playful', 'Inspiring'],
      icon: Zap,
      chakra: 'Solar Plexus',
      element: 'Fire'
    },
    green: {
      name: 'Green',
      color: '#6BCF7F',
      gradient: 'from-green-400 via-green-500 to-green-600',
      innerGlow: 'from-green-500 to-green-700',
      meaning: 'Growth & Healing',
      traits: ['Balanced', 'Healing', 'Growth-oriented', 'Compassionate'],
      icon: Leaf,
      chakra: 'Heart Chakra',
      element: 'Earth'
    },
    blue: {
      name: 'Blue',
      color: '#5DADE2',
      gradient: 'from-blue-400 via-blue-500 to-blue-600',
      innerGlow: 'from-blue-500 to-blue-700',
      meaning: 'Calm & Communication',
      traits: ['Calm', 'Communicative', 'Trustworthy', 'Intuitive'],
      icon: Droplet,
      chakra: 'Throat Chakra',
      element: 'Water'
    },
    indigo: {
      name: 'Indigo',
      color: '#6C5CE7',
      gradient: 'from-indigo-400 via-indigo-500 to-indigo-600',
      innerGlow: 'from-indigo-500 to-indigo-700',
      meaning: 'Intuition & Insight',
      traits: ['Intuitive', 'Wise', 'Perceptive', 'Spiritual'],
      icon: Brain,
      chakra: 'Third Eye',
      element: 'Light'
    },
    violet: {
      name: 'Violet',
      color: '#A29BFE',
      gradient: 'from-violet-400 via-violet-500 to-violet-600',
      innerGlow: 'from-violet-500 to-violet-700',
      meaning: 'Spirituality & Magic',
      traits: ['Spiritual', 'Magical', 'Visionary', 'Transformative'],
      icon: Sparkles,
      chakra: 'Crown Chakra',
      element: 'Ether'
    },
    pink: {
      name: 'Pink',
      color: '#FDA7DF',
      gradient: 'from-pink-400 via-pink-500 to-pink-600',
      innerGlow: 'from-pink-500 to-pink-700',
      meaning: 'Love & Tenderness',
      traits: ['Loving', 'Tender', 'Romantic', 'Nurturing'],
      icon: Heart,
      chakra: 'Heart Chakra',
      element: 'Water'
    },
    white: {
      name: 'White',
      color: '#F8F9FA',
      gradient: 'from-gray-100 via-white to-gray-200',
      innerGlow: 'from-gray-200 to-gray-400',
      meaning: 'Purity & Truth',
      traits: ['Pure', 'Truthful', 'Spiritual', 'Enlightened'],
      icon: Sparkles,
      chakra: 'All Chakras',
      element: 'Light'
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
          <h1 className="text-4xl font-bold mb-2 bg-gradient-to-r from-purple-600 to-pink-600 bg-clip-text text-transparent">
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
          <Card className={`bg-gradient-to-br ${currentAuraColor.gradient} text-white border-none shadow-2xl overflow-hidden`}>
            <CardContent className="p-8">
              <div className="flex flex-col md:flex-row items-center gap-8">
                {/* Aura Visualization Circle */}
                <div className="relative">
                  <motion.div
                    className={`w-64 h-64 rounded-full bg-gradient-to-br ${currentAuraColor.innerGlow} shadow-2xl relative`}
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
                        <Badge key={idx} variant="secondary" className="bg-white/30 text-white border-white/50">
                          {trait}
                        </Badge>
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
                  return (
                    <motion.button
                      key={auraColor.name}
                      onClick={() => handleColorInfo(auraColor)}
                      className={`bg-gradient-to-br ${auraColor.gradient} rounded-xl p-4 text-white shadow-lg hover:shadow-xl transition-all`}
                      whileHover={{ scale: 1.05 }}
                      whileTap={{ scale: 0.95 }}
                      initial={{ opacity: 0, y: 20 }}
                      animate={{ opacity: 1, y: 0 }}
                      transition={{ delay: 0.3 + idx * 0.05 }}
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
        <DialogContent className={selectedColor ? `bg-gradient-to-br ${selectedColor.gradient} text-white border-none` : ''}>
          {selectedColor && (
            <>
              <DialogHeader>
                <DialogTitle className="text-3xl text-white flex items-center gap-2">
                  <selectedColor.icon className="w-8 h-8" />
                  {selectedColor.name} Aura
                </DialogTitle>
                <DialogDescription className="text-white/90 text-lg">
                  {selectedColor.meaning}
                </DialogDescription>
              </DialogHeader>
              <div className="space-y-4 mt-4">
                <div>
                  <h4 className="font-semibold mb-2">Characteristics</h4>
                  <div className="flex flex-wrap gap-2">
                    {selectedColor.traits.map((trait, idx) => (
                      <Badge key={idx} variant="secondary" className="bg-white/30 text-white border-white/50">
                        {trait}
                      </Badge>
                    ))}
                  </div>
                </div>
                <div className="grid grid-cols-2 gap-4">
                  <div className="bg-white/20 backdrop-blur-sm rounded-lg p-3">
                    <p className="text-sm opacity-80">Associated Chakra</p>
                    <p className="font-semibold">{selectedColor.chakra}</p>
                  </div>
                  <div className="bg-white/20 backdrop-blur-sm rounded-lg p-3">
                    <p className="text-sm opacity-80">Element</p>
                    <p className="font-semibold">{selectedColor.element}</p>
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
