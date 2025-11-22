import { useState } from 'react';
import { motion, AnimatePresence } from 'motion/react';
import { Smile, Frown, Meh, ThumbsUp, ThumbsDown, X } from 'lucide-react';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogDescription } from './ui/dialog';
import { Button } from './ui/button';
import api from '../services/api';

interface MoodInputPopupProps {
  isOpen: boolean;
  onClose: () => void;
  onMoodSubmitted: () => void;
}

const moodOptions = [
  { value: 'joy', label: 'Joyful', emoji: '😊', color: 'from-yellow-400 to-orange-400' },
  { value: 'calm', label: 'Calm', emoji: '😌', color: 'from-blue-400 to-cyan-400' },
  { value: 'excited', label: 'Excited', emoji: '🤩', color: 'from-pink-400 to-purple-400' },
  { value: 'neutral', label: 'Neutral', emoji: '😐', color: 'from-gray-400 to-gray-500' },
  { value: 'sad', label: 'Sad', emoji: '😢', color: 'from-blue-500 to-indigo-600' },
  { value: 'anxious', label: 'Anxious', emoji: '😰', color: 'from-yellow-500 to-red-500' },
  { value: 'angry', label: 'Angry', emoji: '😠', color: 'from-red-500 to-red-700' },
  { value: 'tired', label: 'Tired', emoji: '😴', color: 'from-purple-400 to-purple-600' },
];

export function MoodInputPopup({ isOpen, onClose, onMoodSubmitted }: MoodInputPopupProps) {
  const [selectedMood, setSelectedMood] = useState<string | null>(null);
  const [intensity, setIntensity] = useState(5);
  const [note, setNote] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSubmit = async () => {
    if (!selectedMood) return;

    setLoading(true);
    try {
      await api.logEmotion({
        emotion: selectedMood,
        intensity,
        notes: note || undefined,
        detected_from: 'manual',
      });

      // Mark mood as logged today
      localStorage.setItem('nirvami_mood_logged_today', new Date().toISOString().split('T')[0]);
      
      onMoodSubmitted();
      onClose();
      
      // Reset form
      setSelectedMood(null);
      setIntensity(5);
      setNote('');
    } catch (error) {
      console.error('Failed to log mood:', error);
      alert('Failed to log mood. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent className="max-w-2xl">
        <DialogHeader>
          <DialogTitle className="text-2xl flex items-center gap-2">
            <Smile className="w-6 h-6 text-purple-600" />
            How are you feeling right now?
          </DialogTitle>
          <DialogDescription>
            Take a moment to check in with yourself. Your mood helps us personalize your wellness journey.
          </DialogDescription>
        </DialogHeader>

        <div className="space-y-6 py-4">
          {/* Mood Selection */}
          <div>
            <label className="text-sm font-medium text-gray-700 mb-3 block">
              Select your mood
            </label>
            <div className="grid grid-cols-4 gap-3">
              {moodOptions.map((mood) => (
                <motion.button
                  key={mood.value}
                  onClick={() => setSelectedMood(mood.value)}
                  whileHover={{ scale: 1.05 }}
                  whileTap={{ scale: 0.95 }}
                  className={`p-4 rounded-xl border-2 transition-all ${
                    selectedMood === mood.value
                      ? `border-purple-500 bg-gradient-to-br ${mood.color} text-white shadow-lg`
                      : 'border-gray-200 hover:border-purple-300 bg-white'
                  }`}
                >
                  <div className="text-3xl mb-2">{mood.emoji}</div>
                  <div className="text-sm font-medium">{mood.label}</div>
                </motion.button>
              ))}
            </div>
          </div>

          {/* Intensity Slider */}
          {selectedMood && (
            <motion.div
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              className="space-y-3"
            >
              <div className="flex items-center justify-between">
                <label className="text-sm font-medium text-gray-700">
                  Intensity
                </label>
                <span className="text-sm font-semibold text-purple-600">
                  {intensity}/10
                </span>
              </div>
              <div className="flex items-center gap-4">
                <ThumbsDown className="w-5 h-5 text-gray-400" />
                <input
                  id="intensity-slider"
                  type="range"
                  min="1"
                  max="10"
                  value={intensity}
                  onChange={(e) => setIntensity(Number(e.target.value))}
                  className="flex-1 h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer accent-purple-600"
                  aria-label="Mood intensity slider"
                />
                <ThumbsUp className="w-5 h-5 text-gray-400" />
              </div>
            </motion.div>
          )}

          {/* Optional Note */}
          {selectedMood && (
            <motion.div
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.1 }}
              className="space-y-2"
            >
              <label className="text-sm font-medium text-gray-700">
                Add a note (optional)
              </label>
              <textarea
                value={note}
                onChange={(e) => setNote(e.target.value)}
                placeholder="What's on your mind?"
                rows={3}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent outline-none resize-none"
              />
            </motion.div>
          )}

          {/* Submit Button */}
          <div className="flex gap-3 pt-4">
            <Button
              type="button"
              variant="outline"
              onClick={onClose}
              className="flex-1"
            >
              Skip for Now
            </Button>
            <Button
              onClick={handleSubmit}
              disabled={!selectedMood || loading}
              className="flex-1 bg-gradient-to-r from-purple-500 to-blue-500 hover:from-purple-600 hover:to-blue-600"
            >
              {loading ? (
                <span className="flex items-center gap-2">
                  <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
                  Saving...
                </span>
              ) : (
                'Submit Mood'
              )}
            </Button>
          </div>
        </div>
      </DialogContent>
    </Dialog>
  );
}
