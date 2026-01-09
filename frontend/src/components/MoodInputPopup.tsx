import { useState } from 'react';
import { motion } from 'motion/react';
import { Smile, ThumbsUp, ThumbsDown } from 'lucide-react';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogDescription } from './ui/dialog';
import { Button } from './ui/button';
import { toast } from 'sonner';
import api from '../services/api';

interface MoodInputPopupProps {
  isOpen: boolean;
  onClose: () => void;
  onMoodSubmitted: () => void;
}

// Updated mood options matching the provided UI design - all emojis are unique
const moodOptions = [
  { value: 'happy', label: 'Happy', emoji: '😊', color: 'from-yellow-400 to-orange-400' },
  { value: 'calm', label: 'Calm', emoji: '😌', color: 'from-blue-400 to-cyan-400' },
  { value: 'sad', label: 'Sad', emoji: '😢', color: 'from-blue-500/85 to-blue-700/85' },
  { value: 'anxious', label: 'Anxious', emoji: '😰', color: 'from-yellow-500 to-red-500' },
  { value: 'tired', label: 'Tired', emoji: '😴', color: 'from-purple-400 to-purple-600' },
  { value: 'frustrated', label: 'Frustrated', emoji: '😤', color: 'from-orange-500/85 to-orange-700/85' },
  { value: 'grateful', label: 'Grateful', emoji: '🤗', color: 'from-pink-400 to-rose-400' },
  { value: 'neutral', label: 'Neutral', emoji: '😐', color: 'from-gray-400 to-gray-500' },
  { value: 'angry', label: 'Angry', emoji: '😡', color: 'from-red-600/85 to-red-800/85' },
  { value: 'low-energy', label: 'Low Energy', emoji: '😔', color: 'from-slate-500/85 to-slate-700/85' },
  { value: 'energized', label: 'Energized', emoji: '⚡', color: 'from-yellow-300 to-amber-400' },
  { value: 'confused', label: 'Confused', emoji: '😕', color: 'from-purple-500 to-indigo-700' },
];

export function MoodInputPopup({ isOpen, onClose, onMoodSubmitted }: MoodInputPopupProps) {
  const [selectedMood, setSelectedMood] = useState<string | null>(null);
  const [intensity, setIntensity] = useState(5);
  const [energy, setEnergy] = useState<number | null>(null);
  const [notes, setNotes] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSubmit = async () => {
    // Validation: mood and intensity are required
    if (!selectedMood) {
      toast.error('Please select a mood');
      return;
    }
    if (!intensity || intensity < 1 || intensity > 10) {
      toast.error('Please set intensity between 1 and 10');
      return;
    }

    setLoading(true);
    try {
      const response = await api.logMoodFromPopup({
        mood: selectedMood,
        intensity,
        energy: energy || undefined,
        notes: notes || undefined,
        source: 'mood_popup',
      });

      if (response.ok) {
        toast.success('Mood saved! Your aura is updating...');
        
        // Dispatch custom event for Dashboard to listen
        window.dispatchEvent(new CustomEvent('moodLogged'));
        
        // Trigger aura refresh in parent components
        onMoodSubmitted();
        
        // Close popup after short delay to let user see success
        setTimeout(() => {
          onClose();
          
          // Reset form
          setSelectedMood(null);
          setIntensity(5);
          setEnergy(null);
          setNotes('');
        }, 800);
      } else {
        toast.error(response.detail || 'Failed to save mood');
      }
    } catch (error: any) {
      console.error('Failed to log mood:', error);
      const errorMessage = error.response?.data?.detail || error.message || 'Failed to log mood. Please try again.';
      toast.error(errorMessage);
    } finally {
      setLoading(false);
    }
  };

  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent className="max-w-xl max-h-[90vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle className="text-xl flex items-center gap-2">
            <Smile className="w-5 h-5 text-purple-600" />
            How are you feeling right now?
          </DialogTitle>
          <DialogDescription className="text-xs">
            Take a moment to check in with yourself. Your mood helps us personalize your wellness journey.
          </DialogDescription>
        </DialogHeader>

        <div className="space-y-4 py-2">
          {/* Mood Selection */}
          <div>
            <label className="text-sm font-medium text-gray-700 mb-2 block">
              Select your mood
            </label>
            <div className="grid grid-cols-4 gap-2">
              {moodOptions.map((mood) => (
                <motion.button
                  key={mood.value}
                  onClick={() => setSelectedMood(mood.value)}
                  whileHover={{ scale: 1.05 }}
                  whileTap={{ scale: 0.95 }}
                  className={`p-3 rounded-xl border-2 transition-all aspect-square flex flex-col items-center justify-center ${
                    selectedMood === mood.value
                      ? `border-purple-500 bg-gradient-to-br ${mood.color} text-white shadow-lg`
                      : 'border-gray-200 hover:border-purple-300 bg-white'
                  }`}
                >
                  <div className="text-2xl mb-1">{mood.emoji}</div>
                  <div className="text-xs font-medium">{mood.label}</div>
                </motion.button>
              ))}
            </div>
          </div>

          {/* Intensity Slider - Required */}
          {selectedMood && (
            <motion.div
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              className="space-y-2"
            >
              <div className="flex items-center justify-between">
                <label className="text-sm font-medium text-gray-700">
                  Intensity <span className="text-red-500">*</span>
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
                  required
                />
                <ThumbsUp className="w-5 h-5 text-gray-400" />
              </div>
            </motion.div>
          )}

          {/* Optional Energy Slider */}
          {selectedMood && (
            <motion.div
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.05 }}
              className="space-y-2"
            >
              <div className="flex items-center justify-between">
                <label className="text-sm font-medium text-gray-700">
                  Energy Level (optional)
                </label>
                {energy !== null && (
                  <span className="text-sm font-semibold text-purple-600">
                    {energy}/10
                  </span>
                )}
              </div>
              <div className="flex items-center gap-4">
                <ThumbsDown className="w-5 h-5 text-gray-400" />
                <input
                  id="energy-slider"
                  type="range"
                  min="1"
                  max="10"
                  value={energy || 5}
                  onChange={(e) => setEnergy(Number(e.target.value))}
                  className="flex-1 h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer accent-blue-600"
                  aria-label="Energy level slider"
                />
                <ThumbsUp className="w-5 h-5 text-gray-400" />
              </div>
              <button
                type="button"
                onClick={() => setEnergy(null)}
                className="text-xs text-gray-500 hover:text-gray-700 underline"
              >
                Clear energy level
              </button>
            </motion.div>
          )}

          {/* Submit Button */}
          <div className="flex gap-3 pt-2">
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
              disabled={!selectedMood || !intensity || loading}
              className="flex-1 bg-gradient-to-r from-purple-500 to-blue-500 hover:from-purple-600 hover:to-blue-600 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {loading ? (
                <span className="flex items-center gap-2">
                  <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
                  Saving...
                </span>
              ) : (
                'Save Mood'
              )}
            </Button>
          </div>
        </div>
      </DialogContent>
    </Dialog>
  );
}
