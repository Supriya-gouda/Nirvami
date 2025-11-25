import { useState, useEffect } from 'react';
import { motion } from 'motion/react';
import { Calendar, Clock, Plus, Trash2, Save, AlertCircle, CheckCircle } from 'lucide-react';
import { Navigation } from './Navigation';
import { Button } from './ui/button';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { Input } from './ui/input';
import { Textarea } from './ui/textarea';
import type { PageType } from '../App';
import type { User } from '../types/api.types';
import api from '../services/api';

interface DailyRoutinesPageProps {
  user: User | null;
  onNavigate: (page: PageType) => void;
  onLogout?: () => void;
  onOpenNotifications?: () => void;
}

interface RoutineEntry {
  id: string;
  date: string;
  time: string;
  activity: string;
  notes?: string;
  created_at: string;
}

export function DailyRoutinesPage({ user, onNavigate, onLogout, onOpenNotifications }: DailyRoutinesPageProps) {
  const [routines, setRoutines] = useState<RoutineEntry[]>([]);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);

  // Form state
  const [selectedDate, setSelectedDate] = useState<string>(new Date().toISOString().split('T')[0]);
  const [newTime, setNewTime] = useState('');
  const [newActivity, setNewActivity] = useState('');
  const [newNotes, setNewNotes] = useState('');

  // Filter state
  const [filterDays, setFilterDays] = useState(7); // Show last 7 days by default

  // Load routines
  useEffect(() => {
    loadRoutines();
  }, [filterDays]);

  const loadRoutines = async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await api.getRoutines(filterDays);
      setRoutines(data);
    } catch (err) {
      console.error('Failed to load routines:', err);
      setError('Failed to load routines. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const handleAddRoutine = async () => {
    if (!newTime || !newActivity.trim()) {
      setError('Time and activity are required');
      return;
    }

    try {
      setSaving(true);
      setError(null);
      setSuccess(null);

      await api.addRoutine({
        date: selectedDate,
        time: newTime,
        activity: newActivity.trim(),
        notes: newNotes.trim() || undefined,
      });

      setSuccess('Routine added successfully!');
      
      // Reset form
      setNewTime('');
      setNewActivity('');
      setNewNotes('');
      
      // Reload routines
      await loadRoutines();
      
      // Clear success message after 3 seconds
      setTimeout(() => setSuccess(null), 3000);
    } catch (err) {
      console.error('Failed to add routine:', err);
      setError('Failed to add routine. Please try again.');
    } finally {
      setSaving(false);
    }
  };

  const handleDeleteRoutine = async (id: string) => {
    if (!confirm('Are you sure you want to delete this routine?')) {
      return;
    }

    try {
      setError(null);
      await api.deleteRoutine(id);
      setSuccess('Routine deleted successfully!');
      await loadRoutines();
      setTimeout(() => setSuccess(null), 3000);
    } catch (err) {
      console.error('Failed to delete routine:', err);
      setError('Failed to delete routine. Please try again.');
    }
  };

  // Group routines by date
  const groupedRoutines = routines.reduce((acc, routine) => {
    const date = routine.date;
    if (!acc[date]) {
      acc[date] = [];
    }
    acc[date].push(routine);
    return acc;
  }, {} as Record<string, RoutineEntry[]>);

  // Sort dates descending
  const sortedDates = Object.keys(groupedRoutines).sort((a, b) => b.localeCompare(a));

  return (
    <div className="min-h-screen bg-gradient-to-br from-purple-50 via-pink-50 to-orange-50">
      <Navigation
        currentPage="routines"
        onNavigate={onNavigate}
        user={user}
        onLogout={onLogout}
        onOpenNotifications={onOpenNotifications}
      />

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Header */}
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          className="mb-8"
        >
          <h1 className="text-4xl font-bold bg-gradient-to-r from-purple-600 to-pink-600 bg-clip-text text-transparent mb-2">
            Daily Routines (Dinacharya)
          </h1>
          <p className="text-gray-600">
            Track your daily activities to maintain a balanced Ayurvedic lifestyle
          </p>
        </motion.div>

        {/* Success/Error Messages */}
        {success && (
          <motion.div
            initial={{ opacity: 0, y: -10 }}
            animate={{ opacity: 1, y: 0 }}
            className="mb-6 p-4 bg-green-50 border border-green-200 rounded-lg flex items-center gap-2 text-green-800"
          >
            <CheckCircle className="w-5 h-5" />
            {success}
          </motion.div>
        )}

        {error && (
          <motion.div
            initial={{ opacity: 0, y: -10 }}
            animate={{ opacity: 1, y: 0 }}
            className="mb-6 p-4 bg-red-50 border border-red-200 rounded-lg flex items-center gap-2 text-red-800"
          >
            <AlertCircle className="w-5 h-5" />
            {error}
          </motion.div>
        )}

        <div className="grid lg:grid-cols-3 gap-6">
          {/* Add Routine Form */}
          <div className="lg:col-span-1">
            <Card className="sticky top-4 bg-white/80 backdrop-blur-sm border-white/50 shadow-xl">
              <CardHeader>
                <CardTitle className="flex items-center gap-2 text-purple-600">
                  <Plus className="w-5 h-5" />
                  Add New Routine
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                {/* Date Picker */}
                <div>
                  <label className="text-sm font-medium text-gray-700 mb-2 flex items-center gap-2">
                    <Calendar className="w-4 h-4" />
                    Date
                  </label>
                  <Input
                    type="date"
                    value={selectedDate}
                    onChange={(e) => setSelectedDate(e.target.value)}
                    className="bg-white/60 backdrop-blur-sm border-white/50"
                  />
                </div>

                {/* Time Picker */}
                <div>
                  <label className="text-sm font-medium text-gray-700 mb-2 flex items-center gap-2">
                    <Clock className="w-4 h-4" />
                    Time *
                  </label>
                  <Input
                    type="time"
                    value={newTime}
                    onChange={(e) => setNewTime(e.target.value)}
                    className="bg-white/60 backdrop-blur-sm border-white/50"
                    required
                  />
                </div>

                {/* Activity Input */}
                <div>
                  <label className="text-sm font-medium text-gray-700 mb-2 block">
                    Activity *
                  </label>
                  <Input
                    type="text"
                    value={newActivity}
                    onChange={(e) => setNewActivity(e.target.value)}
                    placeholder="e.g., Morning meditation, Oil pulling"
                    className="bg-white/60 backdrop-blur-sm border-white/50"
                    required
                  />
                </div>

                {/* Notes Input */}
                <div>
                  <label className="text-sm font-medium text-gray-700 mb-2 block">
                    Notes (Optional)
                  </label>
                  <Textarea
                    value={newNotes}
                    onChange={(e) => setNewNotes(e.target.value)}
                    placeholder="Additional details about this activity..."
                    rows={3}
                    className="resize-none bg-white/60 backdrop-blur-sm border-white/50"
                  />
                </div>

                {/* Add Button */}
                <Button
                  onClick={handleAddRoutine}
                  disabled={saving || !newTime || !newActivity.trim()}
                  className="w-full bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-700 hover:to-pink-700 text-white"
                >
                  {saving ? (
                    <>Saving...</>
                  ) : (
                    <>
                      <Save className="w-4 h-4 mr-2" />
                      Add Routine
                    </>
                  )}
                </Button>

                <p className="text-xs text-gray-500 text-center">
                  You can add multiple routines for the same day
                </p>
              </CardContent>
            </Card>
          </div>

          {/* Routines List */}
          <div className="lg:col-span-2">
            <Card className="bg-white/80 backdrop-blur-sm border-white/50 shadow-xl">
              <CardHeader className="flex flex-row items-center justify-between">
                <CardTitle className="text-purple-600">Your Routines</CardTitle>
                <div className="flex items-center gap-2">
                  <label className="text-sm text-gray-600">Show last:</label>
                  <select
                    value={filterDays}
                    onChange={(e) => setFilterDays(Number(e.target.value))}
                    className="px-3 py-1 border border-gray-300 rounded-md text-sm bg-white/60"
                  >
                    <option value={7}>7 days</option>
                    <option value={14}>14 days</option>
                    <option value={30}>30 days</option>
                    <option value={90}>90 days</option>
                  </select>
                </div>
              </CardHeader>
              <CardContent>
                {loading ? (
                  <div className="text-center py-12 text-gray-500">
                    Loading routines...
                  </div>
                ) : sortedDates.length === 0 ? (
                  <div className="text-center py-12">
                    <Calendar className="w-16 h-16 mx-auto text-gray-300 mb-4" />
                    <p className="text-gray-500">No routines recorded yet</p>
                    <p className="text-sm text-gray-400 mt-2">
                      Start tracking your daily Ayurvedic activities
                    </p>
                  </div>
                ) : (
                  <div className="space-y-6">
                    {sortedDates.map((date) => {
                      const dateObj = new Date(date + 'T00:00:00');
                      const formattedDate = dateObj.toLocaleDateString('en-US', {
                        weekday: 'long',
                        year: 'numeric',
                        month: 'long',
                        day: 'numeric',
                      });

                      // Sort routines by time
                      const dayRoutines = groupedRoutines[date].sort((a, b) =>
                        a.time.localeCompare(b.time)
                      );

                      return (
                        <motion.div
                          key={date}
                          initial={{ opacity: 0, y: 20 }}
                          animate={{ opacity: 1, y: 0 }}
                          className="border-l-4 border-purple-300 pl-4"
                        >
                          <h3 className="font-semibold text-gray-800 mb-3">
                            {formattedDate}
                          </h3>
                          <div className="space-y-3">
                            {dayRoutines.map((routine) => (
                              <div
                                key={routine.id}
                                className="bg-gradient-to-r from-purple-50 to-pink-50 p-4 rounded-lg border border-purple-100 hover:border-purple-300 transition-colors"
                              >
                                <div className="flex items-start justify-between">
                                  <div className="flex-1">
                                    <div className="flex items-center gap-2 mb-2">
                                      <Clock className="w-4 h-4 text-purple-600" />
                                      <span className="font-medium text-purple-700">
                                        {routine.time}
                                      </span>
                                    </div>
                                    <p className="text-gray-800 font-medium mb-1">
                                      {routine.activity}
                                    </p>
                                    {routine.notes && (
                                      <p className="text-sm text-gray-600 mt-2">
                                        {routine.notes}
                                      </p>
                                    )}
                                  </div>
                                  <Button
                                    variant="ghost"
                                    size="sm"
                                    onClick={() => handleDeleteRoutine(routine.id)}
                                    className="text-red-600 hover:text-red-700 hover:bg-red-50"
                                  >
                                    <Trash2 className="w-4 h-4" />
                                  </Button>
                                </div>
                              </div>
                            ))}
                          </div>
                        </motion.div>
                      );
                    })}
                  </div>
                )}
              </CardContent>
            </Card>
          </div>
        </div>

        {/* Ayurvedic Tips */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2 }}
          className="mt-8"
        >
          <Card className="bg-gradient-to-r from-purple-100 to-pink-100 border-purple-200">
            <CardHeader>
              <CardTitle className="text-purple-700">💡 Ayurvedic Daily Routine Tips</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid md:grid-cols-2 gap-4 text-sm text-gray-700">
                <div>
                  <h4 className="font-semibold mb-2">🌅 Morning (6-10 AM - Kapha Time)</h4>
                  <ul className="list-disc list-inside space-y-1 text-gray-600">
                    <li>Wake before sunrise</li>
                    <li>Tongue scraping & oil pulling</li>
                    <li>Warm water with lemon</li>
                    <li>Morning meditation & yoga</li>
                  </ul>
                </div>
                <div>
                  <h4 className="font-semibold mb-2">☀️ Midday (10 AM - 2 PM - Pitta Time)</h4>
                  <ul className="list-disc list-inside space-y-1 text-gray-600">
                    <li>Eat largest meal at noon</li>
                    <li>Peak productivity time</li>
                    <li>Stay hydrated</li>
                    <li>Brief walk after eating</li>
                  </ul>
                </div>
                <div>
                  <h4 className="font-semibold mb-2">🌆 Evening (6-10 PM - Kapha Time)</h4>
                  <ul className="list-disc list-inside space-y-1 text-gray-600">
                    <li>Light, early dinner</li>
                    <li>Evening walk</li>
                    <li>Gentle activities</li>
                    <li>Wind down routine</li>
                  </ul>
                </div>
                <div>
                  <h4 className="font-semibold mb-2">🌙 Night (10 PM - 2 AM - Pitta Time)</h4>
                  <ul className="list-disc list-inside space-y-1 text-gray-600">
                    <li>Sleep before 10 PM</li>
                    <li>Avoid screens 1 hour before bed</li>
                    <li>Self-massage with oil</li>
                    <li>Calm breathing exercises</li>
                  </ul>
                </div>
              </div>
            </CardContent>
          </Card>
        </motion.div>
      </div>
    </div>
  );
}
