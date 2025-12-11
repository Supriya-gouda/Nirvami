import { useState } from 'react';
import { motion } from 'motion/react';
import { Calendar, Heart, Bed, Footprints, TrendingUp, Save, X } from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { Button } from './ui/button';
import { Input } from './ui/input';
import { Label } from './ui/label';
import { toast } from 'sonner';
import api from '../services/api';

interface ManualHealthEntryProps {
  onSuccess?: () => void;
  onCancel?: () => void;
}

export function ManualHealthEntry({ onSuccess, onCancel }: ManualHealthEntryProps) {
  const [loading, setLoading] = useState(false);
  const [formData, setFormData] = useState({
    date: new Date().toISOString().split('T')[0],
    sleep_hours: '',
    avg_heart_rate: '',
    steps: '',
    stress_level: '5',
    calories_burned: ''
  });

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!formData.sleep_hours && !formData.steps && !formData.avg_heart_rate) {
      toast.error('Please fill in at least one health metric');
      return;
    }

    try {
      setLoading(true);

      const payload = {
        date: formData.date,
        sleep_hours: formData.sleep_hours ? parseFloat(formData.sleep_hours) : undefined,
        avg_heart_rate: formData.avg_heart_rate ? parseInt(formData.avg_heart_rate) : undefined,
        steps: formData.steps ? parseInt(formData.steps) : undefined,
        stress_level: parseInt(formData.stress_level),
        calories_burned: formData.calories_burned ? parseFloat(formData.calories_burned) : undefined
      };

      console.log('Submitting manual health entry:', payload);
      const response = await api.submitManualHealthEntry(payload);
      console.log('Manual health entry response:', response);
      
      // Check if response indicates success
      if (response && (response.success || response.data)) {
        toast.success('Health data saved successfully!');
      } else {
        throw new Error('Invalid response from server');
      }
      
      // Reset form
      setFormData({
        date: new Date().toISOString().split('T')[0],
        sleep_hours: '',
        avg_heart_rate: '',
        steps: '',
        stress_level: '5',
        calories_burned: ''
      });

      if (onSuccess) {
        onSuccess();
      }
    } catch (error: any) {
      console.error('Error submitting health data:', error);
      const errorMsg = error.response?.data?.detail || error.message || 'Failed to save health data';
      toast.error(errorMsg);
    } finally {
      setLoading(false);
    }
  };

  const handleChange = (field: string, value: string) => {
    setFormData(prev => ({ ...prev, [field]: value }));
  };

  return (
    <Card className="w-full max-w-2xl mx-auto">
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Calendar className="w-5 h-5 text-purple-600" />
          Manual Health Entry
        </CardTitle>
        <p className="text-sm text-gray-600">
          Track your health metrics manually if you don't have a smartwatch
        </p>
      </CardHeader>
      <CardContent>
        <form onSubmit={handleSubmit} className="space-y-6">
          {/* Date */}
          <div className="space-y-2">
            <Label htmlFor="date" className="flex items-center gap-2">
              <Calendar className="w-4 h-4" />
              Date
            </Label>
            <Input
              id="date"
              type="date"
              value={formData.date}
              max={new Date().toISOString().split('T')[0]}
              onChange={(e) => handleChange('date', e.target.value)}
              required
            />
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {/* Sleep Hours */}
            <div className="space-y-2">
              <Label htmlFor="sleep_hours" className="flex items-center gap-2">
                <Bed className="w-4 h-4 text-blue-600" />
                Sleep Hours
              </Label>
              <Input
                id="sleep_hours"
                type="number"
                step="0.1"
                min="0"
                max="24"
                placeholder="e.g., 7.5"
                value={formData.sleep_hours}
                onChange={(e) => handleChange('sleep_hours', e.target.value)}
              />
              <p className="text-xs text-gray-500">How many hours did you sleep?</p>
            </div>

            {/* Heart Rate */}
            <div className="space-y-2">
              <Label htmlFor="avg_heart_rate" className="flex items-center gap-2">
                <Heart className="w-4 h-4 text-red-600" />
                Average Heart Rate (bpm)
              </Label>
              <Input
                id="avg_heart_rate"
                type="number"
                min="40"
                max="200"
                placeholder="e.g., 72"
                value={formData.avg_heart_rate}
                onChange={(e) => handleChange('avg_heart_rate', e.target.value)}
              />
              <p className="text-xs text-gray-500">Optional - your resting heart rate</p>
            </div>

            {/* Steps */}
            <div className="space-y-2">
              <Label htmlFor="steps" className="flex items-center gap-2">
                <Footprints className="w-4 h-4 text-green-600" />
                Steps Walked
              </Label>
              <Input
                id="steps"
                type="number"
                min="0"
                placeholder="e.g., 8000"
                value={formData.steps}
                onChange={(e) => handleChange('steps', e.target.value)}
              />
              <p className="text-xs text-gray-500">Approximate steps for the day</p>
            </div>

            {/* Stress Level */}
            <div className="space-y-2">
              <Label htmlFor="stress_level" className="flex items-center gap-2">
                <TrendingUp className="w-4 h-4 text-orange-600" />
                Stress Level (1-10)
              </Label>
              <Input
                id="stress_level"
                type="range"
                min="1"
                max="10"
                value={formData.stress_level}
                onChange={(e) => handleChange('stress_level', e.target.value)}
                className="w-full"
              />
              <div className="flex justify-between text-xs text-gray-500">
                <span>Very Low (1)</span>
                <span className="font-medium text-gray-700">{formData.stress_level}</span>
                <span>Very High (10)</span>
              </div>
            </div>

            {/* Calories Burned */}
            <div className="space-y-2 md:col-span-2">
              <Label htmlFor="calories_burned" className="flex items-center gap-2">
                🔥 Calories Burned
              </Label>
              <Input
                id="calories_burned"
                type="number"
                min="0"
                placeholder="e.g., 350"
                value={formData.calories_burned}
                onChange={(e) => handleChange('calories_burned', e.target.value)}
              />
              <p className="text-xs text-gray-500">Optional - estimated active calories</p>
            </div>
          </div>

          {/* Action Buttons */}
          <div className="flex gap-3 justify-end pt-4">
            {onCancel && (
              <Button
                type="button"
                variant="outline"
                onClick={onCancel}
                disabled={loading}
              >
                <X className="w-4 h-4 mr-2" />
                Cancel
              </Button>
            )}
            <button
              type="submit"
              disabled={loading}
              style={{
                display: 'inline-flex',
                alignItems: 'center',
                justifyContent: 'center',
                gap: '8px',
                padding: '10px 16px',
                background: 'linear-gradient(to right, #9333ea, #2563eb)',
                color: 'white',
                fontWeight: '500',
                fontSize: '14px',
                borderRadius: '6px',
                border: 'none',
                cursor: loading ? 'not-allowed' : 'pointer',
                opacity: loading ? 0.5 : 1,
                transition: 'all 0.2s ease-in-out',
              }}
              onMouseEnter={(e) => {
                if (!loading) {
                  e.currentTarget.style.background = 'linear-gradient(to right, #7e22ce, #1d4ed8)';
                }
              }}
              onMouseLeave={(e) => {
                e.currentTarget.style.background = 'linear-gradient(to right, #9333ea, #2563eb)';
              }}
            >
              {loading ? (
                'Saving...'
              ) : (
                <>
                  <Save className="w-4 h-4 mr-2" />
                  Save Health Data
                </>
              )}
            </button>
          </div>
        </form>

        <div className="mt-6 p-4 bg-blue-50 rounded-lg border border-blue-200">
          <p className="text-sm text-blue-800">
            <strong>💡 Tip:</strong> Fill in this form daily to track your health patterns. 
            The system will analyze your data to detect stress, provide personalized food and yoga 
            recommendations, and help you maintain optimal wellness.
          </p>
        </div>
      </CardContent>
    </Card>
  );
}
