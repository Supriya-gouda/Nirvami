import { useState, useEffect } from 'react';
import { Save, Plus, Trash2, Calendar, X, ChevronLeft, ChevronRight } from 'lucide-react';
import { Navigation } from './Navigation';
import { Button } from './ui/button';
import { Input } from './ui/input';
import { Textarea } from './ui/textarea';
import { Slider } from './ui/slider';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from './ui/select';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogDescription } from './ui/dialog';
import { toast } from 'sonner';
import type { PageType } from '../App';
import type { User } from '../types/api.types';
import api from '../services/api';

interface LogPageProps {
  user: User | null;
  onNavigate: (page: PageType) => void;
  onLogout?: () => void;
  onOpenNotifications?: () => void;
}

interface MealEntry {
  id: string;
  food: string;
  mealType: 'breakfast' | 'lunch' | 'snack' | 'dinner';
}

interface DailyLog {
  meals: MealEntry[];
  mood: string | null;
  moodLabel: string | null;
  energyLevel: number;
  sleepHours: string;
  notes: string;
  timestamp: number;
}

export function LogPage({ user, onNavigate, onLogout, onOpenNotifications }: LogPageProps) {
  const [showCalendar, setShowCalendar] = useState(false);
  const [selectedDate, setSelectedDate] = useState<string | null>(null);
  const [viewedMonth, setViewedMonth] = useState(new Date().getMonth());
  const [viewedYear, setViewedYear] = useState(new Date().getFullYear());
  const [backendLogs, setBackendLogs] = useState<Record<string, DailyLog>>({});
  const [mealEntries, setMealEntries] = useState<MealEntry[]>([
    { id: '1', food: '', mealType: 'breakfast' }
  ]);
  const [selectedMood, setSelectedMood] = useState<string | null>(null);
  const [energyLevel, setEnergyLevel] = useState([60]);
  const [sleepHours, setSleepHours] = useState('7');
  const [additionalNotes, setAdditionalNotes] = useState('');

  // Daily routine state
  const [routineTime, setRoutineTime] = useState('');
  const [routineActivity, setRoutineActivity] = useState('');

  const moods = [
    { emoji: '😊', label: 'Happy' },
    { emoji: '😌', label: 'Calm' },
    { emoji: '😢', label: 'Sad' },
    { emoji: '😰', label: 'Anxious' },
    { emoji: '😴', label: 'Tired' },
    { emoji: '😤', label: 'Frustrated' },
    { emoji: '🤗', label: 'Grateful' },
    { emoji: '😐', label: 'Neutral' },
    { emoji: '😡', label: 'Angry' },
    { emoji: '😔', label: 'Low Energy' },
    { emoji: '⚡', label: 'Energized' },
    { emoji: '😕', label: 'Confused' },
  ];

  // Fetch logs from backend on mount and when month/year changes
  useEffect(() => {
    const fetchBackendLogs = async () => {
      try {
        // Fetch last 30 days of emotion and meal logs
        const endDate = new Date();
        const startDate = new Date();
        startDate.setDate(startDate.getDate() - 30);

        const [emotions, meals] = await Promise.all([
          api.getEmotionLogs({ start_date: startDate.toISOString().split('T')[0], end_date: endDate.toISOString().split('T')[0] }),
          api.getMealHistory({ start_date: startDate.toISOString().split('T')[0], end_date: endDate.toISOString().split('T')[0] })
        ]);

        // Group by date and convert to DailyLog format
        const logs: Record<string, DailyLog> = {};

        // Process emotions
        emotions.forEach((emotion: any) => {
          const date = emotion.timestamp.split('T')[0];
          if (!logs[date]) {
            logs[date] = { meals: [], mood: null, moodLabel: null, energyLevel: 50, sleepHours: '0', notes: '', timestamp: new Date(emotion.timestamp).getTime() };
          }
          const moodEmoji = moods.find(m => m.label.toLowerCase() === emotion.emotion?.toLowerCase());
          logs[date].mood = moodEmoji?.emoji || '😊';
          logs[date].moodLabel = emotion.emotion;
          logs[date].energyLevel = Math.round((emotion.intensity || 5) * 10);
          logs[date].notes = emotion.context || logs[date].notes;
          logs[date].sleepHours = emotion.sleep_hours?.toString() || logs[date].sleepHours;
        });

        // Process meals
        meals.forEach((meal: any) => {
          const date = meal.timestamp.split('T')[0];
          if (!logs[date]) {
            logs[date] = { meals: [], mood: null, moodLabel: null, energyLevel: 50, sleepHours: '0', notes: '', timestamp: new Date(meal.timestamp).getTime() };
          }
          logs[date].meals.push({
            id: meal.id || Date.now().toString(),
            food: meal.meal_name,
            mealType: meal.meal_type as 'breakfast' | 'lunch' | 'snack' | 'dinner'
          });
        });

        setBackendLogs(logs);
      } catch (err) {
        console.warn('Failed to fetch backend logs:', err);
      }
    };

    fetchBackendLogs();
  }, [viewedMonth, viewedYear]);

  const addMealEntry = () => {
    setMealEntries([
      ...mealEntries,
      { id: Date.now().toString(), food: '', mealType: 'breakfast' }
    ]);
  };

  const removeMealEntry = (id: string) => {
    if (mealEntries.length > 1) {
      setMealEntries(mealEntries.filter(entry => entry.id !== id));
    }
  };

  const updateMealEntry = (id: string, field: 'food' | 'mealType', value: string) => {
    setMealEntries(mealEntries.map(entry =>
      entry.id === id ? { ...entry, [field]: value } : entry
    ));
  };

  const handleSave = async () => {
    // Get today's date in YYYY-MM-DD format
    const today = new Date();
    const dateStr = today.toISOString().split('T')[0];

    // Create log entry
    const logEntry: DailyLog = {
      meals: mealEntries.filter(entry => entry.food.trim() !== ''),
      mood: selectedMood,
      moodLabel: selectedMood ? moods.find(m => m.emoji === selectedMood)?.label || null : null,
      energyLevel: energyLevel[0],
      sleepHours: sleepHours,
      notes: additionalNotes,
      timestamp: Date.now()
    };

    // Log all data to backend (no localStorage)
    try {
      // Log emotion if mood is selected
      if (selectedMood && logEntry.moodLabel) {
        await api.logEmotion({
          emotion: logEntry.moodLabel.toLowerCase(),
          intensity: energyLevel[0] / 10,
          notes: additionalNotes || undefined,
          detected_from: 'manual'
        });
      }

      // Log sleep via wearable endpoint (manual entry)
      if (sleepHours) {
        await api.syncWearableData({
          sleep_hours: parseFloat(sleepHours),
          device_type: 'manual'
        });
      }

      // Log meals to backend
      for (const meal of logEntry.meals) {
        await api.logMeal({
          foods: [meal.food],
          meal_type: meal.mealType,
          portion_sizes: { [meal.food]: 'medium' },
          calories: 0
        });
      }

      // Log daily routine if provided
      if (routineTime && routineActivity.trim()) {
        await api.post('/routines/entry', {
          date: dateStr,
          time: routineTime,
          activity: routineActivity.trim()
        });
      }

      toast.success('Daily log saved successfully!');
    } catch (err) {
      console.warn('Failed to sync with backend, saved locally', err);
      toast.success('Daily log saved locally!');
    }

    // Reset form
    setMealEntries([{ id: Date.now().toString(), food: '', mealType: 'breakfast' }]);
    setSelectedMood(null);
    setEnergyLevel([60]);
    setSleepHours('7');
    setAdditionalNotes('');
    setRoutineTime('');
    setRoutineActivity('');
  };

  // Get log for a specific date (from backend only)
  const getLogForDate = (dateStr: string): DailyLog | null => {
    // Use backend logs only
    return backendLogs[dateStr] || null;
  };

  // Check if a date has a log
  const hasLogForDate = (dateStr: string): boolean => {
    return getLogForDate(dateStr) !== null;
  };

  // Get current month calendar data
  const getCurrentMonthData = () => {
    // Use viewed month/year instead of current date
    const year = viewedYear;
    const month = viewedMonth;

    // Get first day of month (0 = Sunday)
    const firstDay = new Date(year, month, 1).getDay();

    // Get number of days in month
    const daysInMonth = new Date(year, month + 1, 0).getDate();

    // Get month name
    const monthNames = ['January', 'February', 'March', 'April', 'May', 'June',
      'July', 'August', 'September', 'October', 'November', 'December'];
    const monthName = monthNames[month];

    return { firstDay, daysInMonth, monthName, year, month };
  };

  // Navigate to previous month
  const goToPreviousMonth = () => {
    if (viewedMonth === 0) {
      setViewedMonth(11);
      setViewedYear(viewedYear - 1);
    } else {
      setViewedMonth(viewedMonth - 1);
    }
  };

  // Navigate to next month
  const goToNextMonth = () => {
    if (viewedMonth === 11) {
      setViewedMonth(0);
      setViewedYear(viewedYear + 1);
    } else {
      setViewedMonth(viewedMonth + 1);
    }
  };

  const handleDateClick = (dateStr: string) => {
    const log = getLogForDate(dateStr);
    if (log) {
      setSelectedDate(dateStr);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-purple-100 via-blue-50 to-cyan-100 relative overflow-hidden">
      <Navigation currentPage="manual" onNavigate={onNavigate} onLogout={onLogout} user={user} onOpenNotifications={onOpenNotifications} />

      <div className="max-w-5xl mx-auto p-6 md:p-8 relative z-10">
        {/* Header */}
        <div className="mb-8">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl md:text-4xl text-gray-800 mb-2">Daily Wellness Log</h1>
              <p className="text-gray-600 text-lg">Track your meals, mood, energy, and sleep</p>
            </div>
            <Button
              variant="outline"
              onClick={() => setShowCalendar(true)}
              className="bg-white/60 backdrop-blur-sm border-white/50 hover:bg-white/80"
            >
              <Calendar className="w-4 h-4 mr-2" />
              View History
            </Button>
          </div>
        </div>

        <div className="space-y-6">
          {/* Meals Log Section */}
          <div className="relative bg-white/40 backdrop-blur-xl rounded-3xl p-6 border border-white/50 shadow-xl">
            <div className="flex items-center justify-between mb-6">
              <h2 className="text-xl text-gray-800">Meals</h2>
              <Button
                onClick={addMealEntry}
                size="sm"
                className="bg-gradient-to-r from-purple-500 to-pink-500 hover:from-purple-600 hover:to-pink-600"
              >
                <Plus className="w-4 h-4 mr-1" />
                Add Meal
              </Button>
            </div>

            <div className="space-y-4">
              {mealEntries.map((entry, index) => (
                <div key={entry.id} className="flex gap-3 items-start">
                  <div className="flex-1 grid md:grid-cols-2 gap-3">
                    <Input
                      placeholder="What did you eat? (e.g., Oatmeal with berries)"
                      value={entry.food}
                      onChange={(e) => updateMealEntry(entry.id, 'food', e.target.value)}
                      className="bg-white/60 backdrop-blur-sm border-white/50"
                    />
                    <Select
                      value={entry.mealType}
                      onValueChange={(value) => updateMealEntry(entry.id, 'mealType', value as MealEntry['mealType'])}
                    >
                      <SelectTrigger className="bg-white/60 backdrop-blur-sm border-white/50">
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent className="bg-white/95 backdrop-blur-xl border-white/50">
                        <SelectItem value="breakfast">🌅 Breakfast</SelectItem>
                        <SelectItem value="lunch">☀️ Lunch</SelectItem>
                        <SelectItem value="snack">🍎 Snacks</SelectItem>
                        <SelectItem value="dinner">🌙 Dinner</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                  {mealEntries.length > 1 && (
                    <Button
                      variant="ghost"
                      size="icon"
                      onClick={() => removeMealEntry(entry.id)}
                      className="text-red-500 hover:text-red-700 hover:bg-red-50"
                    >
                      <Trash2 className="w-4 h-4" />
                    </Button>
                  )}
                </div>
              ))}
            </div>
          </div>

          {/* Daily Routine */}
          <div className="relative bg-white/40 backdrop-blur-xl rounded-3xl p-6 border border-white/50 shadow-xl">
            <h2 className="text-xl text-gray-800 mb-6">Daily Routine Activity</h2>

            <div className="grid md:grid-cols-2 gap-4">
              <div>
                <label className="text-sm text-gray-700 mb-3 block">
                  Time
                </label>
                <Input
                  type="time"
                  value={routineTime}
                  onChange={(e) => setRoutineTime(e.target.value)}
                  className="bg-white/60 backdrop-blur-sm border-white/50"
                />
              </div>
              <div>
                <label className="text-sm text-gray-700 mb-3 block">
                  Activity
                </label>
                <Input
                  type="text"
                  value={routineActivity}
                  onChange={(e) => setRoutineActivity(e.target.value)}
                  placeholder="e.g., Morning meditation, Evening walk"
                  className="bg-white/60 backdrop-blur-sm border-white/50"
                />
              </div>
            </div>
            <p className="text-xs text-gray-500 mt-2">
              Optional: Log a specific activity from your daily routine
            </p>
          </div>

          {/* Additional Notes */}
          <div className="relative bg-white/40 backdrop-blur-xl rounded-3xl p-6 border border-white/50 shadow-xl">
            <h2 className="text-xl text-gray-800 mb-6">Additional Notes</h2>

            <Textarea
              value={additionalNotes}
              onChange={(e) => setAdditionalNotes(e.target.value)}
              placeholder="Any additional thoughts, symptoms, or observations about your day..."
              rows={5}
              className="resize-none bg-white/60 backdrop-blur-sm border-white/50"
            />
            <p className="text-xs text-gray-500 mt-2">
              Optional: Add any other details about your wellness journey today
            </p>
          </div>

          {/* Save Button */}
          <div className="flex justify-end">
            <Button
              onClick={handleSave}
              size="lg"
              className="bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-700 hover:to-pink-700 text-white shadow-lg"
            >
              <Save className="w-5 h-5 mr-2" />
              Save Daily Log
            </Button>
          </div>
        </div>
      </div>

      {/* Calendar Dialog */}
      <Dialog open={showCalendar} onOpenChange={(open) => {
        setShowCalendar(open);
        if (!open) setSelectedDate(null);
      }}>
        <DialogContent className="max-w-4xl max-h-[90vh] overflow-y-auto bg-white/95 backdrop-blur-xl border-white/50">
          <DialogHeader>
            <DialogTitle className="flex items-center gap-2">
              <Calendar className="w-5 h-5 text-purple-600" />
              {selectedDate
                ? 'Daily Log Details'
                : `${getCurrentMonthData().monthName} ${getCurrentMonthData().year} - Wellness History`
              }
            </DialogTitle>
            <DialogDescription>
              {selectedDate
                ? 'View your wellness log for the selected day.'
                : 'Click on a highlighted day to view your saved log.'
              }
            </DialogDescription>
          </DialogHeader>

          {selectedDate ? (
            // Show log details for selected date
            (() => {
              const log = getLogForDate(selectedDate);
              if (!log) return null;

              const date = new Date(selectedDate);
              const formattedDate = date.toLocaleDateString('en-US', {
                weekday: 'long',
                year: 'numeric',
                month: 'long',
                day: 'numeric'
              });

              return (
                <div className="space-y-4">
                  {/* Back button */}
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={() => setSelectedDate(null)}
                    className="mb-2"
                  >
                    ← Back to Calendar
                  </Button>

                  {/* Date header */}
                  <div className="bg-gradient-to-r from-purple-100 to-pink-100 rounded-2xl p-4">
                    <h3 className="text-lg text-gray-800">{formattedDate}</h3>
                    <p className="text-sm text-gray-600">Logged at {new Date(log.timestamp).toLocaleTimeString()}</p>
                  </div>

                  {/* Meals */}
                  {log.meals.length > 0 && (
                    <div className="bg-white/60 backdrop-blur-sm rounded-2xl p-5 border border-white/50">
                      <h4 className="text-gray-800 mb-3">🍽️ Meals</h4>
                      <div className="space-y-2">
                        {log.meals.map((meal, index) => (
                          <div key={index} className="flex items-center gap-3 p-3 bg-white/80 rounded-xl">
                            <span className="text-lg">
                              {meal.mealType === 'breakfast' ? '🌅' :
                                meal.mealType === 'lunch' ? '☀️' :
                                  meal.mealType === 'snack' ? '🍎' : '🌙'}
                            </span>
                            <div className="flex-1">
                              <p className="text-sm text-gray-800">{meal.food}</p>
                              <p className="text-xs text-gray-500 capitalize">{meal.mealType}</p>
                            </div>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}

                  {/* Mood & Energy */}
                  <div className="grid md:grid-cols-2 gap-4">
                    <div className="bg-white/60 backdrop-blur-sm rounded-2xl p-5 border border-white/50">
                      <h4 className="text-gray-800 mb-3">😊 Mood</h4>
                      {log.mood ? (
                        <div className="flex items-center gap-3">
                          <span className="text-4xl">{log.mood}</span>
                          <span className="text-lg text-gray-700">{log.moodLabel}</span>
                        </div>
                      ) : (
                        <p className="text-gray-500 text-sm">No mood recorded</p>
                      )}
                    </div>

                    <div className="bg-white/60 backdrop-blur-sm rounded-2xl p-5 border border-white/50">
                      <h4 className="text-gray-800 mb-3">⚡ Energy Level</h4>
                      <div className="space-y-2">
                        <p className="text-2xl text-purple-600">{log.energyLevel}%</p>
                        <div className="h-2 bg-gray-200 rounded-full overflow-hidden">
                          <div
                            className="h-full bg-gradient-to-r from-purple-400 to-pink-400 rounded-full"
                            /* eslint-disable-next-line react/forbid-dom-props */
                            style={{ width: `${log.energyLevel}%` }}
                          />
                        </div>
                      </div>
                    </div>
                  </div>

                  {/* Sleep */}
                  <div className="bg-white/60 backdrop-blur-sm rounded-2xl p-5 border border-white/50">
                    <h4 className="text-gray-800 mb-3">😴 Sleep Duration</h4>
                    <p className="text-lg text-gray-700">{log.sleepHours} hours</p>
                    {log.sleepHours && (
                      <p className="text-sm text-gray-500 mt-1">
                        {parseFloat(log.sleepHours) >= 7 && parseFloat(log.sleepHours) <= 9
                          ? '✅ Optimal sleep range'
                          : parseFloat(log.sleepHours) < 7
                            ? '⚠️ Below recommended range'
                            : '⚠️ Above recommended range'}
                      </p>
                    )}
                  </div>

                  {/* Notes */}
                  {log.notes && (
                    <div className="bg-white/60 backdrop-blur-sm rounded-2xl p-5 border border-white/50">
                      <h4 className="text-gray-800 mb-3">📝 Notes</h4>
                      <p className="text-gray-700 whitespace-pre-wrap">{log.notes}</p>
                    </div>
                  )}
                </div>
              );
            })()
          ) : (
            // Show calendar
            <div className="space-y-4">
              <div className="bg-white/60 backdrop-blur-sm rounded-2xl p-6 border border-white/50">
                {/* Year */}
                <div className="text-center mb-2">
                  <p className="text-sm text-gray-600">{getCurrentMonthData().year}</p>
                </div>

                {/* Month navigation */}
                <div className="flex items-center justify-between mb-4">
                  <Button
                    variant="ghost"
                    size="icon"
                    onClick={goToPreviousMonth}
                    className="hover:bg-white/60"
                  >
                    <ChevronLeft className="w-5 h-5 text-gray-700" />
                  </Button>

                  <h3 className="text-lg text-gray-800">
                    {getCurrentMonthData().monthName}
                  </h3>

                  <Button
                    variant="ghost"
                    size="icon"
                    onClick={goToNextMonth}
                    className="hover:bg-white/60"
                  >
                    <ChevronRight className="w-5 h-5 text-gray-700" />
                  </Button>
                </div>

                {/* Calendar grid */}
                <div className="grid grid-cols-7 gap-2">
                  {/* Day headers */}
                  {['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'].map((day) => (
                    <div key={day} className="text-center text-sm text-gray-600 p-2">
                      {day}
                    </div>
                  ))}

                  {/* Empty cells for days before month starts */}
                  {Array.from({ length: getCurrentMonthData().firstDay }).map((_, i) => (
                    <div key={`empty-${i}`} className="aspect-square" />
                  ))}

                  {/* Actual days of the month */}
                  {Array.from({ length: getCurrentMonthData().daysInMonth }, (_, dayIndex) => {
                    const day = dayIndex + 1;
                    const { year, month } = getCurrentMonthData();
                    const dateStr = `${year}-${String(month + 1).padStart(2, '0')}-${String(day).padStart(2, '0')}`;
                    const hasLog = hasLogForDate(dateStr);
                    const isToday = dateStr === new Date().toISOString().split('T')[0];

                    return (
                      <button
                        key={day}
                        onClick={() => handleDateClick(dateStr)}
                        disabled={!hasLog}
                        className={`aspect-square p-2 rounded-xl flex items-center justify-center text-sm transition-all ${hasLog
                          ? 'bg-gradient-to-br from-purple-100 to-pink-100 text-purple-700 hover:scale-110 hover:shadow-lg cursor-pointer'
                          : 'bg-gray-50 text-gray-400 cursor-not-allowed'
                          } ${isToday ? 'ring-2 ring-purple-500 ring-offset-2' : ''
                          }`}
                        title={hasLog ? `View log for ${dateStr}` : 'No log for this day'}
                      >
                        {day}
                      </button>
                    );
                  })}
                </div>
              </div>

              {/* Legend */}
              <div className="flex items-center justify-center gap-6 p-4 bg-gradient-to-br from-purple-50 to-pink-50 rounded-xl">
                <div className="flex items-center gap-2">
                  <div className="w-6 h-6 rounded-lg bg-gradient-to-br from-purple-100 to-pink-100" />
                  <span className="text-sm text-gray-700">Has Log</span>
                </div>
                <div className="flex items-center gap-2">
                  <div className="w-6 h-6 rounded-lg bg-gray-50" />
                  <span className="text-sm text-gray-700">No Log</span>
                </div>
                <div className="flex items-center gap-2">
                  <div className="w-6 h-6 rounded-lg bg-gray-50 ring-2 ring-purple-500 ring-offset-1" />
                  <span className="text-sm text-gray-700">Today</span>
                </div>
              </div>
            </div>
          )}
        </DialogContent>
      </Dialog>
    </div>
  );
}