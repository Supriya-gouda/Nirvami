import { useState } from 'react';
import { motion } from 'motion/react';
import { Calendar, Save, Clock } from 'lucide-react';
import { Navigation } from './Navigation';
import { Button } from './ui/button';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { Input } from './ui/input';
import { Textarea } from './ui/textarea';
import { Slider } from './ui/slider';
import { Dialog, DialogContent, DialogHeader, DialogTitle } from './ui/dialog';
import { toast } from 'sonner';
import type { PageType, User } from '../App';

interface ManualInputPageProps {
  user: User | null;
  onNavigate: (page: PageType) => void;
}

export function ManualInputPage({ user, onNavigate }: ManualInputPageProps) {
  const [showCalendar, setShowCalendar] = useState(false);
  const [mealLog, setMealLog] = useState('');
  const [sleepHours, setSleepHours] = useState('7');
  const [sleepQuality, setSleepQuality] = useState([70]);
  const [energyLevel, setEnergyLevel] = useState([60]);
  const [stressLevel, setStressLevel] = useState([40]);
  const [notes, setNotes] = useState('');

  const handleSave = () => {
    toast.success('Daily log saved successfully!');
    // Reset form
    setMealLog('');
    setSleepHours('7');
    setSleepQuality([70]);
    setEnergyLevel([60]);
    setStressLevel([40]);
    setNotes('');
  };

  return (
    <div className="min-h-screen">
      <Navigation currentPage="manual" onNavigate={onNavigate} user={user} />

      <div className="max-w-4xl mx-auto p-8">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="mb-8"
        >
          <div className="flex items-center justify-between">
            <div>
              <h1>Daily Wellness Log</h1>
              <p className="text-gray-600">Track your daily habits and well-being</p>
            </div>
            <Button variant="outline" onClick={() => setShowCalendar(true)}>
              <Calendar className="w-4 h-4 mr-2" />
              View Calendar
            </Button>
          </div>
        </motion.div>

        <div className="space-y-6">
          {/* Meals Section */}
          <motion.div
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: 0.1 }}
          >
            <Card>
              <CardHeader>
                <CardTitle>Meals Eaten Today</CardTitle>
              </CardHeader>
              <CardContent>
                <Textarea
                  value={mealLog}
                  onChange={(e) => setMealLog(e.target.value)}
                  placeholder="Breakfast: Oatmeal with berries&#10;Lunch: Quinoa salad with vegetables&#10;Dinner: Grilled fish with steamed broccoli"
                  rows={6}
                  className="resize-none"
                />
                <p className="text-sm text-gray-500 mt-2">
                  List your meals with approximate times and ingredients
                </p>
              </CardContent>
            </Card>
          </motion.div>

          {/* Sleep Section */}
          <motion.div
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: 0.2 }}
          >
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Clock className="w-5 h-5" />
                  Sleep Duration & Quality
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-6">
                <div>
                  <label className="text-sm text-gray-600 mb-2 block">
                    Hours of Sleep
                  </label>
                  <Input
                    type="number"
                    value={sleepHours}
                    onChange={(e) => setSleepHours(e.target.value)}
                    min="0"
                    max="24"
                    step="0.5"
                    className="max-w-xs"
                  />
                </div>

                <div>
                  <label className="text-sm text-gray-600 mb-3 block">
                    Sleep Quality: {sleepQuality[0]}%
                  </label>
                  <Slider
                    value={sleepQuality}
                    onValueChange={setSleepQuality}
                    max={100}
                    step={1}
                    className="w-full"
                  />
                  <div className="flex justify-between text-xs text-gray-500 mt-1">
                    <span>Poor</span>
                    <span>Excellent</span>
                  </div>
                </div>
              </CardContent>
            </Card>
          </motion.div>

          {/* Mood Sliders */}
          <motion.div
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: 0.3 }}
          >
            <Card>
              <CardHeader>
                <CardTitle>Mood & Energy Levels</CardTitle>
              </CardHeader>
              <CardContent className="space-y-6">
                <div>
                  <label className="text-sm text-gray-600 mb-3 block">
                    Energy Level: {energyLevel[0]}%
                  </label>
                  <Slider
                    value={energyLevel}
                    onValueChange={setEnergyLevel}
                    max={100}
                    step={1}
                    className="w-full"
                  />
                  <div className="flex justify-between text-xs text-gray-500 mt-1">
                    <span>Exhausted</span>
                    <span>Energized</span>
                  </div>
                </div>

                <div>
                  <label className="text-sm text-gray-600 mb-3 block">
                    Stress Level: {stressLevel[0]}%
                  </label>
                  <Slider
                    value={stressLevel}
                    onValueChange={setStressLevel}
                    max={100}
                    step={1}
                    className="w-full"
                  />
                  <div className="flex justify-between text-xs text-gray-500 mt-1">
                    <span>Calm</span>
                    <span>Very Stressed</span>
                  </div>
                </div>

                <div className="grid grid-cols-2 gap-4 pt-4">
                  <motion.div
                    className="p-4 rounded-lg bg-gradient-to-br from-blue-50 to-blue-100"
                    whileHover={{ scale: 1.02 }}
                  >
                    <p className="text-sm text-gray-600 mb-1">Mood</p>
                    <p className="text-blue-700">
                      {energyLevel[0] > 70 ? 'Energetic' : energyLevel[0] > 40 ? 'Balanced' : 'Low Energy'}
                    </p>
                  </motion.div>
                  <motion.div
                    className="p-4 rounded-lg bg-gradient-to-br from-purple-50 to-purple-100"
                    whileHover={{ scale: 1.02 }}
                  >
                    <p className="text-sm text-gray-600 mb-1">Stress</p>
                    <p className="text-purple-700">
                      {stressLevel[0] < 30 ? 'Calm' : stressLevel[0] < 60 ? 'Moderate' : 'High'}
                    </p>
                  </motion.div>
                </div>
              </CardContent>
            </Card>
          </motion.div>

          {/* Additional Notes */}
          <motion.div
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: 0.4 }}
          >
            <Card>
              <CardHeader>
                <CardTitle>Additional Notes</CardTitle>
              </CardHeader>
              <CardContent>
                <Textarea
                  value={notes}
                  onChange={(e) => setNotes(e.target.value)}
                  placeholder="Any additional thoughts, symptoms, or observations about your day..."
                  rows={4}
                  className="resize-none"
                />
              </CardContent>
            </Card>
          </motion.div>

          {/* Save Button */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.5 }}
            className="flex justify-end"
          >
            <Button
              onClick={handleSave}
              size="lg"
              className="bg-gradient-to-r from-purple-500 to-blue-500 hover:from-purple-600 hover:to-blue-600"
            >
              <Save className="w-4 h-4 mr-2" />
              Save Daily Log
            </Button>
          </motion.div>
        </div>
      </div>

      {/* Calendar Dialog */}
      <Dialog open={showCalendar} onOpenChange={setShowCalendar}>
        <DialogContent className="max-w-3xl">
          <DialogHeader>
            <DialogTitle>Calendar View - Past Logs</DialogTitle>
          </DialogHeader>
          <div className="grid grid-cols-7 gap-2 p-4">
            {['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'].map((day) => (
              <div key={day} className="text-center text-sm text-gray-600 p-2">
                {day}
              </div>
            ))}
            {Array.from({ length: 35 }, (_, i) => {
              const hasLog = i % 3 === 0 && i > 0;
              return (
                <motion.div
                  key={i}
                  className={`aspect-square p-2 rounded-lg flex items-center justify-center text-sm cursor-pointer ${
                    hasLog
                      ? 'bg-gradient-to-br from-purple-100 to-blue-100 text-purple-700'
                      : 'bg-gray-50 text-gray-400'
                  }`}
                  whileHover={{ scale: hasLog ? 1.1 : 1 }}
                >
                  {i + 1}
                </motion.div>
              );
            })}
          </div>
        </DialogContent>
      </Dialog>
    </div>
  );
}
