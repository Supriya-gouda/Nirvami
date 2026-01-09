import { useState } from 'react';
import { motion, AnimatePresence } from 'motion/react';
import { Save, Sparkles } from 'lucide-react';
import { Navigation } from './Navigation';
import { Button } from './ui/button';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { Dialog, DialogContent, DialogHeader, DialogTitle } from './ui/dialog';
import { toast } from 'sonner';
import type { PageType, User } from '../App';

interface ManualInputPageProps {
  user: User | null;
  onNavigate: (page: PageType) => void;
}

interface MoodEntry {
  id: string;
  emoji: string;
  color: string;
  label: string;
  timestamp: Date;
}

export function MoodBoardPage({ user, onNavigate }: ManualInputPageProps) {
  const [selectedEmoji, setSelectedEmoji] = useState<string | null>(null);
  const [selectedColor, setSelectedColor] = useState<string | null>(null);
  const [savedMoods, setSavedMoods] = useState<MoodEntry[]>([
    { id: '1', emoji: '😊', color: '#FFD700', label: 'Happy', timestamp: new Date(Date.now() - 86400000) },
    { id: '2', emoji: '😌', color: '#87CEEB', label: 'Calm', timestamp: new Date(Date.now() - 172800000) },
    { id: '3', emoji: '😴', color: '#9370DB', label: 'Tired', timestamp: new Date(Date.now() - 259200000) },
  ]);
  const [showConfirmation, setShowConfirmation] = useState(false);
  const [showRecommendation, setShowRecommendation] = useState(false);

  const moods = [
    { emoji: '😊', label: 'Happy', recommendation: 'Keep the positive energy flowing with some gentle stretching!' },
    { emoji: '😌', label: 'Calm', recommendation: 'Perfect state for meditation. Try 10 minutes of mindfulness.' },
    { emoji: '😢', label: 'Sad', recommendation: 'A gentle walk in nature might help lift your spirits.' },
    { emoji: '😰', label: 'Anxious', recommendation: 'Try 5 minutes of Pranayama breathing to calm your Vata.' },
    { emoji: '😴', label: 'Tired', recommendation: 'Consider a 20-minute Yoga Nidra session for deep restoration.' },
    { emoji: '😤', label: 'Frustrated', recommendation: 'Channel this energy with some dynamic yoga poses.' },
    { emoji: '🤗', label: 'Grateful', recommendation: 'Great! Practice gratitude journaling to amplify this feeling.' },
    { emoji: '😐', label: 'Neutral', recommendation: 'A balanced state. Maintain it with regular breathing exercises.' },
  ];

  const colors = [
    { hex: '#FF6B6B', name: 'Passionate Red', emotion: 'energetic' },
    { hex: '#FFD93D', name: 'Joyful Yellow', emotion: 'happy' },
    { hex: '#6BCB77', name: 'Peaceful Green', emotion: 'calm' },
    { hex: '#4D96FF', name: 'Serene Blue', emotion: 'relaxed' },
    { hex: '#9D84B7', name: 'Dreamy Purple', emotion: 'creative' },
    { hex: '#FF8FB1', name: 'Gentle Pink', emotion: 'loving' },
    { hex: '#A8E6CF', name: 'Fresh Mint', emotion: 'refreshed' },
    { hex: '#FF8C42', name: 'Vibrant Orange', emotion: 'motivated' },
  ];

  const handleSaveMood = () => {
    if (selectedEmoji && selectedColor) {
      const mood = moods.find((m) => m.emoji === selectedEmoji);
      const newMood: MoodEntry = {
        id: Date.now().toString(),
        emoji: selectedEmoji,
        color: selectedColor,
        label: mood?.label || 'Unknown',
        timestamp: new Date(),
      };
      setSavedMoods([newMood, ...savedMoods]);
      setShowConfirmation(true);
      
      // Show recommendation after a short delay
      setTimeout(() => {
        setShowConfirmation(false);
        setShowRecommendation(true);
      }, 1500);
    } else {
      toast.error('Please select both an emoji and a color');
    }
  };

  const getCurrentRecommendation = () => {
    const mood = moods.find((m) => m.emoji === selectedEmoji);
    return mood?.recommendation || '';
  };

  return (
    <div className="min-h-screen">
      <Navigation currentPage="moodboard" onNavigate={onNavigate} user={user} />

      <div className="max-w-6xl mx-auto p-8">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="mb-8"
        >
          <h1 className="mb-2">Mood Board</h1>
          <p className="text-gray-600">Express your feelings visually</p>
        </motion.div>

        <div className="grid md:grid-cols-2 gap-6">
          {/* Mood Selection */}
          <motion.div
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: 0.1 }}
          >
            <Card>
              <CardHeader>
                <CardTitle>How are you feeling?</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-4 gap-4">
                  {moods.map((mood, index) => (
                    <motion.button
                      key={mood.emoji}
                      onClick={() => setSelectedEmoji(mood.emoji)}
                      className={`aspect-square rounded-2xl flex flex-col items-center justify-center gap-2 transition-all ${
                        selectedEmoji === mood.emoji
                          ? 'bg-gradient-to-br from-purple-100 to-blue-100 ring-4 ring-purple-400 scale-110'
                          : 'bg-gray-50 hover:bg-gray-100'
                      }`}
                      initial={{ opacity: 0, scale: 0.8 }}
                      animate={{ opacity: 1, scale: 1 }}
                      transition={{ delay: 0.2 + index * 0.05 }}
                      whileHover={{ scale: selectedEmoji === mood.emoji ? 1.1 : 1.05 }}
                      whileTap={{ scale: 0.95 }}
                    >
                      <span className="text-4xl">{mood.emoji}</span>
                      <span className="text-xs text-gray-600">{mood.label}</span>
                    </motion.button>
                  ))}
                </div>
              </CardContent>
            </Card>
          </motion.div>

          {/* Color Selection */}
          <motion.div
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: 0.2 }}
          >
            <Card>
              <CardHeader>
                <CardTitle>Choose your mood color</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-4 gap-4">
                  {colors.map((color, index) => (
                    <motion.button
                      key={color.hex}
                      onClick={() => setSelectedColor(color.hex)}
                      className={`aspect-square rounded-2xl transition-all ${
                        selectedColor === color.hex
                          ? 'ring-4 ring-offset-2 ring-purple-400 scale-110'
                          : 'hover:scale-105'
                      }`}
                      style={{ backgroundColor: color.hex }}
                      initial={{ opacity: 0, scale: 0.8 }}
                      animate={{ opacity: 1, scale: 1 }}
                      transition={{ delay: 0.3 + index * 0.05 }}
                      whileHover={{ scale: selectedColor === color.hex ? 1.1 : 1.05 }}
                      whileTap={{ scale: 0.95 }}
                    >
                      <span className="sr-only">{color.name}</span>
                    </motion.button>
                  ))}
                </div>

                {selectedColor && (
                  <motion.div
                    initial={{ opacity: 0, y: 10 }}
                    animate={{ opacity: 1, y: 0 }}
                    className="mt-4 p-3 rounded-lg bg-purple-50"
                  >
                    <p className="text-sm text-purple-900">
                      {colors.find((c) => c.hex === selectedColor)?.name} - 
                      Feeling {colors.find((c) => c.hex === selectedColor)?.emotion}
                    </p>
                  </motion.div>
                )}
              </CardContent>
            </Card>
          </motion.div>
        </div>

        {/* Preview & Save */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.3 }}
          className="mt-6"
        >
          <Card>
            <CardHeader>
              <CardTitle>Your Current Mood</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-6">
                  <motion.div
                    className="w-24 h-24 rounded-2xl flex items-center justify-center text-5xl"
                    style={{ backgroundColor: selectedColor || '#e5e7eb' }}
                    animate={selectedEmoji && selectedColor ? { scale: [1, 1.1, 1] } : {}}
                    transition={{ duration: 0.5 }}
                  >
                    {selectedEmoji || '❓'}
                  </motion.div>
                  <div>
                    <p className="text-gray-600 mb-1">Selected Mood:</p>
                    <p className="text-xl">
                      {moods.find((m) => m.emoji === selectedEmoji)?.label || 'Not selected'}
                    </p>
                    {selectedColor && (
                      <p className="text-sm text-gray-500 mt-1">
                        Color: {colors.find((c) => c.hex === selectedColor)?.name}
                      </p>
                    )}
                  </div>
                </div>

                <Button
                  onClick={handleSaveMood}
                  disabled={!selectedEmoji || !selectedColor}
                  size="lg"
                  className="bg-gradient-to-r from-purple-500 to-blue-500 hover:from-purple-600 hover:to-blue-600"
                >
                  <Save className="w-4 h-4 mr-2" />
                  Save Mood
                </Button>
              </div>
            </CardContent>
          </Card>
        </motion.div>

        {/* Mood Wall */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.4 }}
          className="mt-6"
        >
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Sparkles className="w-5 h-5 text-purple-600" />
                Your Mood Wall
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-3 md:grid-cols-6 gap-4">
                <AnimatePresence>
                  {savedMoods.map((mood, index) => (
                    <motion.div
                      key={mood.id}
                      initial={{ opacity: 0, scale: 0 }}
                      animate={{ opacity: 1, scale: 1 }}
                      exit={{ opacity: 0, scale: 0 }}
                      transition={{ delay: index * 0.05 }}
                      className="aspect-square rounded-xl flex flex-col items-center justify-center gap-2 shadow-lg"
                      style={{ backgroundColor: mood.color }}
                      whileHover={{ scale: 1.1, rotate: 5 }}
                    >
                      <span className="text-4xl">{mood.emoji}</span>
                      <span className="text-xs text-gray-700">
                        {mood.timestamp.toLocaleDateString()}
                      </span>
                    </motion.div>
                  ))}
                </AnimatePresence>
              </div>
            </CardContent>
          </Card>
        </motion.div>
      </div>

      {/* Save Confirmation Dialog */}
      <Dialog open={showConfirmation} onOpenChange={setShowConfirmation}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle className="text-center">Mood Saved! ✨</DialogTitle>
            <DialogDescription className="text-center">Your mood has been recorded successfully</DialogDescription>
          </DialogHeader>
          <div className="flex justify-center py-6">
            <motion.div
              className="w-32 h-32 rounded-full flex items-center justify-center text-6xl"
              style={{ backgroundColor: selectedColor || '#e5e7eb' }}
              animate={{ scale: [0, 1.2, 1], rotate: [0, 360] }}
              transition={{ duration: 0.8 }}
            >
              {selectedEmoji}
            </motion.div>
          </div>
        </DialogContent>
      </Dialog>

      {/* Recommendation Dialog */}
      <Dialog open={showRecommendation} onOpenChange={setShowRecommendation}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Wellness Recommendation</DialogTitle>
            <DialogDescription>Based on your current mood, we suggest the following practice</DialogDescription>
          </DialogHeader>
          <div className="space-y-4 pt-4">
            <div className="bg-gradient-to-r from-purple-50 to-blue-50 p-6 rounded-lg">
              <p className="text-purple-900">{getCurrentRecommendation()}</p>
            </div>
            <Button
              onClick={() => {
                setShowRecommendation(false);
                onNavigate('yoga');
              }}
              className="w-full"
            >
              Start Practice
            </Button>
          </div>
        </DialogContent>
      </Dialog>
    </div>
  );
}
