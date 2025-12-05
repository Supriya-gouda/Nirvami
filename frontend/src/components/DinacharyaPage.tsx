import { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { 
  Calendar, 
  Clock, 
  Plus, 
  Trash2, 
  Sparkles,
  AlertCircle,
  CheckCircle
} from 'lucide-react';
import { Navigation } from './Navigation';
import api from '../services/api';

interface DinacharyaPageProps {
  user: any;
  onNavigate: (page: string) => void;
  onLogout: () => void;
  onOpenNotifications: () => void;
}

interface RoutineItem {
  id?: string;
  date?: string;
  time: string;
  activity: string;
  notes?: string;
}

interface AISuggestions {
  routine_score: number;
  overall_assessment?: string;
  sleep_recommendations?: string[];
  break_recommendations?: string[];
  movement_recommendations?: string[];
  meal_recommendations?: string[];
  productivity_recommendations?: string[];
  stress_recommendations?: string[];
  dosha_recommendations?: string[];
  rescheduling_suggestions?: Array<{
    task: string;
    current_time: string;
    suggested_time: string;
    reason: string;
  }>;
  missing_elements?: string[];
  optimal_schedule?: {
    [key: string]: string;
  };
  generated_at?: string;
  
  // Legacy fields for backward compatibility
  areas_for_improvement?: string[];
  suggestions?: {
    [key: string]: string;
  };
}

export function DinacharyaPage({ user, onNavigate, onLogout, onOpenNotifications }: DinacharyaPageProps) {
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [analyzing, setAnalyzing] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);

  // Form state
  const [selectedDate, setSelectedDate] = useState<string>(new Date().toISOString().split('T')[0]);
  const [routines, setRoutines] = useState<RoutineItem[]>([]);

  // New routine form
  const [newTime, setNewTime] = useState('');
  const [newActivity, setNewActivity] = useState('');
  const [newNotes, setNewNotes] = useState('');

  // AI suggestions
  const [aiSuggestions, setAiSuggestions] = useState<AISuggestions | null>(null);

  // History view
  const [viewMode, setViewMode] = useState<'today' | 'history'>('today');
  const [historyDays, setHistoryDays] = useState(7);
  const [historyData, setHistoryData] = useState<any[]>([]);

  // Load routines on mount and when date changes
  useEffect(() => {
    loadTodayData();
  }, [selectedDate]);

  const loadTodayData = async () => {
    try {
      setLoading(true);
      setError(null);
      
      const today = new Date().toISOString().split('T')[0];
      const lastDate = localStorage.getItem('dinacharya_last_date');
      
      // Calculate yesterday's date
      const yesterday = new Date();
      yesterday.setDate(yesterday.getDate() - 1);
      const yesterdayDate = yesterday.toISOString().split('T')[0];
      
      // Fetch routines from both yesterday and today
      const response = await api.getRoutineEntries(yesterdayDate, today, 2);
      
      if (response && response.length > 0) {
        // Sort routines by date (descending) then time (ascending)
        // This will show today's routines first, then yesterday's
        const sortedRoutines = response
          .map((r: any) => ({
            id: r.id,
            date: r.date,
            time: r.time,
            activity: r.activity,
            notes: r.notes || ''
          }))
          .sort((a: any, b: any) => {
            // First sort by date (descending - newer first)
            if (a.date !== b.date) {
              return b.date.localeCompare(a.date);
            }
            // Then sort by time (ascending - earlier first)
            return a.time.localeCompare(b.time);
          });
        setRoutines(sortedRoutines);
      } else {
        setRoutines([]);
      }
      
      // Check if it's a new day and auto-copy from yesterday if needed
      const isNewDay = lastDate && lastDate !== today;
      if (isNewDay) {
        // Check if we have any routines for today
        const todayRoutines = response?.filter((r: any) => r.date === today) || [];
        
        if (todayRoutines.length === 0) {
          // No routines for today yet, copy from yesterday
          const yesterdayRoutines = response?.filter((r: any) => r.date === yesterdayDate) || [];
          
          if (yesterdayRoutines.length > 0) {
            try {
              // Copy each routine to today
              const copyPromises = yesterdayRoutines.map((routine: any) =>
                api.addRoutine({
                  date: today,
                  time: routine.time,
                  activity: routine.activity,
                  notes: routine.notes
                })
              );
              
              await Promise.all(copyPromises);
              
              // Reload to show copied routines
              const updatedResponse = await api.getRoutineEntries(yesterdayDate, today, 2);
              if (updatedResponse && updatedResponse.length > 0) {
                const sortedRoutines = updatedResponse
                  .map((r: any) => ({
                    id: r.id,
                    date: r.date,
                    time: r.time,
                    activity: r.activity,
                    notes: r.notes || ''
                  }))
                  .sort((a: any, b: any) => {
                    if (a.date !== b.date) {
                      return b.date.localeCompare(a.date);
                    }
                    return a.time.localeCompare(b.time);
                  });
                setRoutines(sortedRoutines);
              }
            } catch (err) {
              console.error('Failed to copy routines:', err);
            }
          }
        }
      }

      // Update last date in localStorage
      localStorage.setItem('dinacharya_last_date', today);

    } catch (err) {
      console.error('Failed to load dinacharya data:', err);
      setError('Failed to load data. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const loadHistory = async () => {
    try {
      setLoading(true);
      const data = await api.getDinacharyaHistory(historyDays);
      setHistoryData(data.history || []);
    } catch (err) {
      console.error('Failed to load history:', err);
      setError('Failed to load history.');
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

      // Save to backend immediately
      const routineData = {
        date: selectedDate,
        time: newTime,
        activity: newActivity.trim(),
        notes: newNotes.trim() || undefined
      };

      await api.addRoutine(routineData);

      // Reload data to show both yesterday's and today's routines
      await loadTodayData();

      // Reset form
      setNewTime('');
      setNewActivity('');
      setNewNotes('');
      setSuccess('Routine added successfully!');
      setTimeout(() => setSuccess(null), 3000);
    } catch (err) {
      console.error('Failed to add routine:', err);
      setError('Failed to add routine. Please try again.');
    } finally {
      setSaving(false);
    }
  };

  const handleRemoveRoutine = async (id: string | undefined, index: number) => {
    if (!id) {
      // If no ID, just remove from local state
      setRoutines(routines.filter((_, i) => i !== index));
      return;
    }

    try {
      await api.deleteRoutine(id);
      // Reload data to refresh the list with both yesterday's and today's routines
      await loadTodayData();
      setSuccess('Routine deleted successfully!');
      setTimeout(() => setSuccess(null), 3000);
    } catch (err) {
      console.error('Failed to delete routine:', err);
      setError('Failed to delete routine. Please try again.');
    }
  };

  const handleAnalyze = async () => {
    if (routines.length === 0) {
      setError('Please add some routines before analyzing');
      return;
    }

    try {
      setAnalyzing(true);
      setError(null);

      // Find the most recent date with routines from the current list
      const latestRoutineDate = routines.reduce((latest, routine) => {
        if (!routine.date) return latest;
        return !latest || routine.date > latest ? routine.date : latest;
      }, '');

      // Use latest routine date or fallback to selected date
      const dateToAnalyze = latestRoutineDate || selectedDate;

      const result = await api.analyzeDinacharya(dateToAnalyze);
      setAiSuggestions(result.suggestions);
      setSuccess('AI analysis complete! Using Gemini AI for Ayurvedic routine analysis.');
      
      setTimeout(() => setSuccess(null), 5000);
    } catch (err) {
      console.error('Failed to analyze:', err);
      setError('Failed to generate AI analysis.');
    } finally {
      setAnalyzing(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-purple-50 via-pink-50 to-orange-50">
      <Navigation 
        currentPage="dinacharya"
        user={user}
        onNavigate={onNavigate}
        onLogout={onLogout}
        onOpenNotifications={onOpenNotifications}
      />

      <div className="container mx-auto px-4 py-8 max-w-7xl">
        {/* Header */}
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          className="mb-8"
        >
          <div className="flex items-center justify-between mb-4">
            <div>
              <h1 className="text-4xl font-bold bg-gradient-to-r from-purple-600 to-pink-600 bg-clip-text text-transparent mb-2">
                Dinacharya
              </h1>
              <p className="text-gray-600">
                Your daily wellness routine powered by Ayurvedic wisdom
              </p>
            </div>
            <div className="flex gap-2">
              <button
                onClick={() => setViewMode('today')}
                className={`px-4 py-2 rounded-lg transition-all ${
                  viewMode === 'today'
                    ? 'bg-purple-600 text-white'
                    : 'bg-white text-gray-600 hover:bg-purple-50'
                }`}
              >
                Today
              </button>
              <button
                onClick={() => {
                  setViewMode('history');
                  loadHistory();
                }}
                className={`px-4 py-2 rounded-lg transition-all ${
                  viewMode === 'history'
                    ? 'bg-purple-600 text-white'
                    : 'bg-white text-gray-600 hover:bg-purple-50'
                }`}
              >
                History
              </button>
            </div>
          </div>
        </motion.div>

        {/* Notifications */}
        {error && (
          <div className="mb-4 p-4 bg-red-50 border border-red-200 rounded-lg flex items-start gap-3">
            <AlertCircle className="w-5 h-5 text-red-600 flex-shrink-0 mt-0.5" />
            <p className="text-red-800">{error}</p>
          </div>
        )}

        {success && (
          <div className="mb-4 p-4 bg-green-50 border border-green-200 rounded-lg flex items-start gap-3">
            <CheckCircle className="w-5 h-5 text-green-600 flex-shrink-0 mt-0.5" />
            <p className="text-green-800">{success}</p>
          </div>
        )}

        {viewMode === 'today' ? (
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Left Column - Input Forms */}
            <div className="space-y-6">
              {/* Date Selector */}
              <motion.div
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                className="bg-white rounded-2xl p-6 shadow-lg"
              >
                <div className="flex items-center gap-3 mb-4">
                  <Calendar className="w-6 h-6 text-purple-600" />
                  <h2 className="text-xl font-semibold">Select Date</h2>
                </div>
                <input
                  type="date"
                  value={selectedDate}
                  onChange={(e) => setSelectedDate(e.target.value)}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                  aria-label="Select date"
                />
              </motion.div>

              {/* Add Daily Routine */}
              <motion.div
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: 0.1 }}
                className="bg-white rounded-2xl p-6 shadow-lg"
              >
                <div className="flex items-center gap-3 mb-4">
                  <Clock className="w-6 h-6 text-purple-600" />
                  <h2 className="text-xl font-semibold">Add Daily Routine</h2>
                </div>

                {/* Add Routine Form */}
                <div className="space-y-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">Time</label>
                    <input
                      type="time"
                      value={newTime}
                      onChange={(e) => setNewTime(e.target.value)}
                      className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500"
                      aria-label="Routine time"
                    />
                  </div>
                  
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">Activity</label>
                    <input
                      type="text"
                      value={newActivity}
                      onChange={(e) => setNewActivity(e.target.value)}
                      className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500"
                      placeholder="e.g., Morning yoga, Breakfast"
                    />
                  </div>
                  
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">Notes (Optional)</label>
                    <textarea
                      value={newNotes}
                      onChange={(e) => setNewNotes(e.target.value)}
                      className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500"
                      placeholder="Any additional details..."
                      rows={2}
                    />
                  </div>
                  
                  <button
                    onClick={handleAddRoutine}
                    disabled={saving || !newTime || !newActivity.trim()}
                    className="w-full flex items-center justify-center gap-2 px-6 py-3.5 bg-gradient-to-r from-purple-600 to-purple-700 text-white rounded-lg hover:from-purple-700 hover:to-purple-800 transition-all disabled:opacity-50 disabled:cursor-not-allowed font-semibold shadow-lg text-base"
                  >
                    <Plus className="w-5 h-5" />
                    {saving ? 'Adding Routine...' : 'Add Routine'}
                  </button>
                </div>
              </motion.div>

              {/* Analyze Button */}
              <motion.div
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: 0.2 }}
              >
                <button
                  onClick={handleAnalyze}
                  disabled={analyzing || routines.length === 0}
                  className="w-full flex items-center justify-center gap-2 px-6 py-4 bg-gradient-to-r from-purple-700 to-pink-700 text-white rounded-lg hover:from-purple-800 hover:to-pink-800 transition-all disabled:opacity-50 disabled:cursor-not-allowed font-bold shadow-xl text-lg"
                >
                  <Sparkles className="w-6 h-6" />
                  {analyzing ? 'Analyzing Schedule...' : 'Analyze My Schedule'}
                </button>
              </motion.div>
            </div>

            {/* Right Column - My Routine & AI Suggestions */}
            <div className="space-y-6">
              {/* My Routine Section */}
              <motion.div
                initial={{ opacity: 0, x: 20 }}
                animate={{ opacity: 1, x: 0 }}
                className="bg-white rounded-2xl p-6 shadow-lg"
              >
                <div className="flex items-center gap-3 mb-4">
                  <Clock className="w-6 h-6 text-purple-600" />
                  <h2 className="text-xl font-semibold">My Routine</h2>
                </div>

                <div className="space-y-2 max-h-96 overflow-y-auto">
                  {routines.length === 0 ? (
                    <div className="text-center py-8">
                      <Clock className="w-12 h-12 mx-auto text-gray-300 mb-2" />
                      <p className="text-gray-500">No routines added yet</p>
                      <p className="text-sm text-gray-400 mt-1">Add your daily schedule on the left</p>
                    </div>
                  ) : (
                    routines.map((routine, index) => {
                      const today = new Date().toISOString().split('T')[0];
                      const isToday = routine.date === today;
                      const dateLabel = isToday ? 'Today' : 'Yesterday';
                      const dateBgColor = isToday ? 'bg-green-100 text-green-700' : 'bg-blue-100 text-blue-700';
                      
                      return (
                        <div
                          key={index}
                          className="flex items-start gap-3 p-3 bg-gradient-to-r from-purple-50 to-pink-50 rounded-lg border border-purple-100"
                        >
                          <div className="flex-1">
                            <div className="flex items-center gap-2 mb-1 flex-wrap">
                              <Clock className="w-4 h-4 text-purple-600" />
                              <span className="font-semibold text-purple-700">{routine.time}</span>
                              {routine.date && (
                                <span className={`text-xs px-2 py-0.5 rounded-full font-medium ${dateBgColor}`}>
                                  {dateLabel}
                                </span>
                              )}
                            </div>
                            <p className="text-gray-800 font-medium">{routine.activity}</p>
                            {routine.notes && (
                              <p className="text-sm text-gray-600 mt-1">{routine.notes}</p>
                            )}
                        </div>
                          <button
                            onClick={() => handleRemoveRoutine(routine.id, index)}
                            className="text-red-500 hover:text-red-700 p-1 hover:bg-red-50 rounded transition-colors"
                            aria-label="Remove routine"
                          >
                            <Trash2 className="w-4 h-4" />
                          </button>
                        </div>
                      );
                    })
                  )}
                </div>
              </motion.div>
              {aiSuggestions ? (
                <>
                  {/* Routine Score & Overall Assessment */}
                  <motion.div
                    initial={{ opacity: 0, x: 20 }}
                    animate={{ opacity: 1, x: 0 }}
                    className="bg-gradient-to-br from-purple-600 to-pink-600 rounded-2xl p-6 shadow-lg text-white"
                  >
                    <div className="flex items-center justify-between mb-4">
                      <h2 className="text-2xl font-bold">Schedule Health Score</h2>
                      <Sparkles className="w-8 h-8" />
                    </div>
                    <div className="text-6xl font-bold mb-3">
                      {aiSuggestions.routine_score}/100
                    </div>
                    <p className="text-purple-100 text-sm leading-relaxed">
                      {aiSuggestions.overall_assessment || 
                       (aiSuggestions.routine_score >= 80 ? 'Excellent schedule alignment!' :
                        aiSuggestions.routine_score >= 60 ? 'Good progress with room for optimization' :
                        'Significant improvements recommended')}
                    </p>
                  </motion.div>

                  {/* 1. Sleep & Wake Cycle */}
                  {aiSuggestions.sleep_recommendations && aiSuggestions.sleep_recommendations.length > 0 && (
                    <motion.div initial={{ opacity: 0, x: 20 }} animate={{ opacity: 1, x: 0 }} transition={{ delay: 0.05 }} className="bg-white rounded-2xl p-5 shadow-lg">
                      <h3 className="text-lg font-bold text-indigo-600 mb-3 flex items-center gap-2">
                        <span>😴</span> Sleep & Wake Cycle
                      </h3>
                      <ul className="space-y-2">
                        {aiSuggestions.sleep_recommendations.map((rec: string, i: number) => (
                          <li key={i} className="flex items-start gap-2 text-sm text-gray-700">
                            <span className="text-indigo-500 font-bold">✓</span>
                            <span>{rec}</span>
                          </li>
                        ))}
                      </ul>
                    </motion.div>
                  )}

                  {/* 2. Break Scheduling & Burnout Prevention */}
                  {aiSuggestions.break_recommendations && aiSuggestions.break_recommendations.length > 0 && (
                    <motion.div initial={{ opacity: 0, x: 20 }} animate={{ opacity: 1, x: 0 }} transition={{ delay: 0.1 }} className="bg-white rounded-2xl p-5 shadow-lg">
                      <h3 className="text-lg font-bold text-orange-600 mb-3 flex items-center gap-2">
                        <span>⏸️</span> Break Scheduling & Burnout Prevention
                      </h3>
                      <ul className="space-y-2">
                        {aiSuggestions.break_recommendations.map((rec: string, i: number) => (
                          <li key={i} className="flex items-start gap-2 text-sm text-gray-700">
                            <span className="text-orange-500 font-bold">✓</span>
                            <span>{rec}</span>
                          </li>
                        ))}
                      </ul>
                    </motion.div>
                  )}

                  {/* 3. Movement & Exercise */}
                  {aiSuggestions.movement_recommendations && aiSuggestions.movement_recommendations.length > 0 && (
                    <motion.div initial={{ opacity: 0, x: 20 }} animate={{ opacity: 1, x: 0 }} transition={{ delay: 0.15 }} className="bg-white rounded-2xl p-5 shadow-lg">
                      <h3 className="text-lg font-bold text-green-600 mb-3 flex items-center gap-2">
                        <span>🏃</span> Movement & Exercise Optimization
                      </h3>
                      <ul className="space-y-2">
                        {aiSuggestions.movement_recommendations.map((rec: string, i: number) => (
                          <li key={i} className="flex items-start gap-2 text-sm text-gray-700">
                            <span className="text-green-500 font-bold">✓</span>
                            <span>{rec}</span>
                          </li>
                        ))}
                      </ul>
                    </motion.div>
                  )}

                  {/* 4. Meal Timing & Digestive Health */}
                  {aiSuggestions.meal_recommendations && aiSuggestions.meal_recommendations.length > 0 && (
                    <motion.div initial={{ opacity: 0, x: 20 }} animate={{ opacity: 1, x: 0 }} transition={{ delay: 0.2 }} className="bg-white rounded-2xl p-5 shadow-lg">
                      <h3 className="text-lg font-bold text-yellow-600 mb-3 flex items-center gap-2">
                        <span>🍽️</span> Meal Timing & Digestive Health
                      </h3>
                      <ul className="space-y-2">
                        {aiSuggestions.meal_recommendations.map((rec: string, i: number) => (
                          <li key={i} className="flex items-start gap-2 text-sm text-gray-700">
                            <span className="text-yellow-500 font-bold">✓</span>
                            <span>{rec}</span>
                          </li>
                        ))}
                      </ul>
                    </motion.div>
                  )}

                  {/* 5. Productivity Recommendations */}
                  {aiSuggestions.productivity_recommendations && aiSuggestions.productivity_recommendations.length > 0 && (
                    <motion.div initial={{ opacity: 0, x: 20 }} animate={{ opacity: 1, x: 0 }} transition={{ delay: 0.25 }} className="bg-white rounded-2xl p-5 shadow-lg">
                      <h3 className="text-lg font-bold text-blue-600 mb-3 flex items-center gap-2">
                        <span>📚</span> Study / Work Efficiency
                      </h3>
                      <ul className="space-y-2">
                        {aiSuggestions.productivity_recommendations.map((rec: string, i: number) => (
                          <li key={i} className="flex items-start gap-2 text-sm text-gray-700">
                            <span className="text-blue-500 font-bold">✓</span>
                            <span>{rec}</span>
                          </li>
                        ))}
                      </ul>
                    </motion.div>
                  )}

                  {/* 6. Stress & Mood Regulation */}
                  {aiSuggestions.stress_recommendations && aiSuggestions.stress_recommendations.length > 0 && (
                    <motion.div initial={{ opacity: 0, x: 20 }} animate={{ opacity: 1, x: 0 }} transition={{ delay: 0.3 }} className="bg-white rounded-2xl p-5 shadow-lg">
                      <h3 className="text-lg font-bold text-pink-600 mb-3 flex items-center gap-2">
                        <span>🧘</span> Stress & Mood Regulation
                      </h3>
                      <ul className="space-y-2">
                        {aiSuggestions.stress_recommendations.map((rec: string, i: number) => (
                          <li key={i} className="flex items-start gap-2 text-sm text-gray-700">
                            <span className="text-pink-500 font-bold">✓</span>
                            <span>{rec}</span>
                          </li>
                        ))}
                      </ul>
                    </motion.div>
                  )}

                  {/* 7. Ayurvedic Dosha Recommendations */}
                  {aiSuggestions.dosha_recommendations && aiSuggestions.dosha_recommendations.length > 0 && (
                    <motion.div initial={{ opacity: 0, x: 20 }} animate={{ opacity: 1, x: 0 }} transition={{ delay: 0.35 }} className="bg-white rounded-2xl p-5 shadow-lg">
                      <h3 className="text-lg font-bold text-purple-600 mb-3 flex items-center gap-2">
                        <span>🕉️</span> Ayurvedic Lifestyle (Dosha-Based)
                      </h3>
                      <ul className="space-y-2">
                        {aiSuggestions.dosha_recommendations.map((rec: string, i: number) => (
                          <li key={i} className="flex items-start gap-2 text-sm text-gray-700">
                            <span className="text-purple-500 font-bold">✓</span>
                            <span>{rec}</span>
                          </li>
                        ))}
                      </ul>
                    </motion.div>
                  )}

                  {/* 8. Rescheduling Suggestions */}
                  {aiSuggestions.rescheduling_suggestions && aiSuggestions.rescheduling_suggestions.length > 0 && (
                    <motion.div initial={{ opacity: 0, x: 20 }} animate={{ opacity: 1, x: 0 }} transition={{ delay: 0.4 }} className="bg-white rounded-2xl p-5 shadow-lg">
                      <h3 className="text-lg font-bold text-red-600 mb-3 flex items-center gap-2">
                        <span>📅</span> Smart Rescheduling Suggestions
                      </h3>
                      <div className="space-y-3">
                        {aiSuggestions.rescheduling_suggestions.map((sug: any, i: number) => (
                          <div key={i} className="bg-red-50 p-3 rounded-lg border-l-4 border-red-500">
                            <div className="font-semibold text-sm text-gray-800 mb-1">{sug.task}</div>
                            <div className="text-xs text-gray-600 flex items-center gap-2">
                              <span className="line-through">{sug.current_time}</span>
                              <span>→</span>
                              <span className="font-bold text-red-600">{sug.suggested_time}</span>
                            </div>
                            <div className="text-xs text-gray-500 mt-1 italic">{sug.reason}</div>
                          </div>
                        ))}
                      </div>
                    </motion.div>
                  )}

                  {/* Missing Elements */}
                  {aiSuggestions.missing_elements && aiSuggestions.missing_elements.length > 0 && (
                    <motion.div initial={{ opacity: 0, x: 20 }} animate={{ opacity: 1, x: 0 }} transition={{ delay: 0.45 }} className="bg-amber-50 rounded-2xl p-5 shadow-lg border-2 border-amber-300">
                      <h3 className="text-lg font-bold text-amber-700 mb-3 flex items-center gap-2">
                        <span>⚠️</span> Missing from Your Schedule
                      </h3>
                      <div className="flex flex-wrap gap-2">
                        {aiSuggestions.missing_elements.map((elem: string, i: number) => (
                          <span key={i} className="px-3 py-1 bg-amber-200 text-amber-800 rounded-full text-xs font-semibold">
                            {elem}
                          </span>
                        ))}
                      </div>
                    </motion.div>
                  )}

                  {/* Optimal Schedule */}
                  {aiSuggestions.optimal_schedule && Object.keys(aiSuggestions.optimal_schedule).length > 0 && (
                    <motion.div initial={{ opacity: 0, x: 20 }} animate={{ opacity: 1, x: 0 }} transition={{ delay: 0.5 }} className="bg-gradient-to-br from-cyan-50 to-blue-50 rounded-2xl p-6 shadow-lg border-2 border-cyan-200">
                      <h3 className="text-xl font-bold text-cyan-700 mb-4 flex items-center gap-2">
                        <span>⭐</span> Your Ideal Daily Schedule
                      </h3>
                      <div className="space-y-2">
                        {Object.entries(aiSuggestions.optimal_schedule).map(([activity, time]) => (
                          <div key={activity} className="flex items-center justify-between p-3 bg-white rounded-lg shadow-sm">
                            <span className="text-gray-700 font-medium capitalize">{activity.replace(/_/g, ' ')}</span>
                            <span className="font-bold text-cyan-600">{time as string}</span>
                          </div>
                        ))}
                      </div>
                    </motion.div>
                  )}
                </>
              ) : (
                <motion.div
                  initial={{ opacity: 0, x: 20 }}
                  animate={{ opacity: 1, x: 0 }}
                  className="bg-white rounded-2xl p-12 shadow-lg text-center"
                >
                  <Sparkles className="w-16 h-16 text-purple-300 mx-auto mb-4" />
                  <h3 className="text-xl font-semibold text-gray-700 mb-2">
                    Ready for AI Analysis
                  </h3>
                  <p className="text-gray-500">
                    Add your daily routines, then click "AI Analysis" to get personalized Ayurvedic suggestions powered by Google Gemini AI.
                  </p>
                  <div className="mt-4 p-3 bg-blue-50 rounded-lg text-sm text-blue-800">
                    <strong>Model:</strong> Google Gemini AI analyzes your routine based on Ayurvedic principles (Dinacharya) and your dosha type to provide personalized wellness suggestions.
                  </div>
                </motion.div>
              )}
            </div>
          </div>
        ) : (
          /* History View */
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="bg-white rounded-2xl p-6 shadow-lg"
          >
            <div className="flex items-center justify-between mb-6">
              <h2 className="text-2xl font-semibold">History</h2>
              <select
                value={historyDays}
                onChange={(e) => {
                  setHistoryDays(parseInt(e.target.value));
                  loadHistory();
                }}
                className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500"
                aria-label="History time range"
              >
                <option value={7}>Last 7 days</option>
                <option value={14}>Last 14 days</option>
                <option value={30}>Last 30 days</option>
              </select>
            </div>

            {loading ? (
              <div className="text-center py-12 text-gray-500">Loading history...</div>
            ) : historyData.length === 0 ? (
              <div className="text-center py-12">
                <Calendar className="w-16 h-16 mx-auto text-gray-300 mb-4" />
                <p className="text-gray-500">No history available</p>
              </div>
            ) : (
              <div className="space-y-4">
                {historyData.map((day) => (
                  <div key={day.date} className="border border-gray-200 rounded-lg p-4">
                    <h3 className="font-semibold text-lg mb-3">
                      {new Date(day.date).toLocaleDateString('en-US', {
                        weekday: 'long',
                        year: 'numeric',
                        month: 'long',
                        day: 'numeric'
                      })}
                    </h3>
                    
                    {day.routines && day.routines.length > 0 && (
                      <div className="mb-3">
                        <h4 className="text-sm font-semibold text-gray-600 mb-2">Routines:</h4>
                        <div className="space-y-1">
                          {day.routines.map((r: any, i: number) => (
                            <div key={i} className="text-sm text-gray-700">
                              {r.time} - {r.activity}
                            </div>
                          ))}
                        </div>
                      </div>
                    )}

                    {day.wellness && (
                      <div className="grid grid-cols-4 gap-4 text-sm">
                        <div>
                          <span className="text-gray-600">Stress:</span>
                          <span className="ml-1 font-semibold">{day.wellness.stress_level}/10</span>
                        </div>
                        <div>
                          <span className="text-gray-600">Energy:</span>
                          <span className="ml-1 font-semibold">{day.wellness.energy_level}/10</span>
                        </div>
                        <div>
                          <span className="text-gray-600">Sleep Quality:</span>
                          <span className="ml-1 font-semibold">{day.wellness.sleep_quality}/10</span>
                        </div>
                        <div>
                          <span className="text-gray-600">Sleep Hours:</span>
                          <span className="ml-1 font-semibold">{day.wellness.sleep_hours}h</span>
                        </div>
                      </div>
                    )}
                  </div>
                ))}
              </div>
            )}
          </motion.div>
        )}
      </div>
    </div>
  );
}
