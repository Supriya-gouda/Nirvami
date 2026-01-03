import { useState, useEffect } from 'react';
import { Navigation } from '../components/Navigation';
import type { PageType } from '../App';

interface User {
  id: string;
  email: string;
  name?: string;
  full_name?: string;
}

interface JournalProps {
  user: User | null;
  onNavigate: (page: PageType) => void;
  onLogout: () => void;
  onOpenNotifications: () => void;
}

interface JournalEntry {
  id: string;
  date: string;
  content: string;
  emotion?: string;
  emotion_confidence?: number;
  created_at: string;
}

interface JournalInsight {
  id: string;
  date: string;
  summary: {
    summary: string;
    dominant_emotions: string[];
    patterns: string;
    positive_signals: string;
    gentle_suggestion: string;
  };
  created_at: string;
}

const emotionEmojis: { [key: string]: string } = {
  // Positive emotions
  admiration: '🌟',
  amusement: '😄',
  approval: '👍',
  caring: '🤗',
  excitement: '🎉',
  gratitude: '🙏',
  joy: '😊',
  love: '❤️',
  optimism: '🌈',
  pride: '💪',
  relief: '😌',
  
  // Negative emotions
  anger: '😠',
  annoyance: '😤',
  disappointment: '😞',
  disapproval: '👎',
  disgust: '🤢',
  embarrassment: '😳',
  fear: '😨',
  grief: '😭',
  nervousness: '😰',
  remorse: '😔',
  sadness: '😢',
  
  // Ambiguous/neutral
  confusion: '😕',
  curiosity: '🤔',
  desire: '😍',
  neutral: '😐',
  realization: '💡',
  surprise: '😮',
};

const emotionColors: { [key: string]: string } = {
  // Positive emotions
  admiration: 'bg-purple-100 text-purple-800 border-purple-300',
  amusement: 'bg-yellow-100 text-yellow-800 border-yellow-300',
  approval: 'bg-green-100 text-green-800 border-green-300',
  caring: 'bg-pink-100 text-pink-800 border-pink-300',
  excitement: 'bg-orange-100 text-orange-800 border-orange-300',
  gratitude: 'bg-teal-100 text-teal-800 border-teal-300',
  joy: 'bg-yellow-100 text-yellow-800 border-yellow-300',
  love: 'bg-red-100 text-red-800 border-red-300',
  optimism: 'bg-cyan-100 text-cyan-800 border-cyan-300',
  pride: 'bg-indigo-100 text-indigo-800 border-indigo-300',
  relief: 'bg-lime-100 text-lime-800 border-lime-300',
  
  // Negative emotions
  anger: 'bg-red-200 text-red-900 border-red-400',
  annoyance: 'bg-orange-200 text-orange-900 border-orange-400',
  disappointment: 'bg-gray-200 text-gray-900 border-gray-400',
  disapproval: 'bg-slate-200 text-slate-900 border-slate-400',
  disgust: 'bg-green-200 text-green-900 border-green-400',
  embarrassment: 'bg-pink-200 text-pink-900 border-pink-400',
  fear: 'bg-purple-200 text-purple-900 border-purple-400',
  grief: 'bg-blue-200 text-blue-900 border-blue-400',
  nervousness: 'bg-violet-200 text-violet-900 border-violet-400',
  remorse: 'bg-indigo-200 text-indigo-900 border-indigo-400',
  sadness: 'bg-blue-100 text-blue-800 border-blue-300',
  
  // Ambiguous/neutral
  confusion: 'bg-amber-100 text-amber-800 border-amber-300',
  curiosity: 'bg-sky-100 text-sky-800 border-sky-300',
  desire: 'bg-rose-100 text-rose-800 border-rose-300',
  neutral: 'bg-gray-100 text-gray-800 border-gray-300',
  realization: 'bg-emerald-100 text-emerald-800 border-emerald-300',
  surprise: 'bg-fuchsia-100 text-fuchsia-800 border-fuchsia-300',
};

export default function Journal({ user, onNavigate, onLogout, onOpenNotifications }: JournalProps) {
  const [entries, setEntries] = useState<JournalEntry[]>([]);
  const [content, setContent] = useState('');
  const [loading, setLoading] = useState(false);
  const [saving, setSaving] = useState(false);
  const [insight, setInsight] = useState<JournalInsight | null>(null);
  const [generatingInsight, setGeneratingInsight] = useState(false);
  const [selectedDate, setSelectedDate] = useState(new Date().toISOString().split('T')[0]);
  const [error, setError] = useState<string | null>(null);
  const [saveFeedback, setSaveFeedback] = useState<{
    show: boolean;
    emotion?: string;
    confidence?: number;
  }>({ show: false });

  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  const API_BASE = (import.meta as any).env?.VITE_API_URL || 'http://localhost:8000/api/v1';

  useEffect(() => {
    fetchEntries();
  }, []);

  const fetchEntries = async () => {
    setLoading(true);
    setError(null);
    try {
      const token = localStorage.getItem('token');
      console.log('[Journal] Fetching entries...');
      console.log('[Journal] Token exists:', !!token);
      
      const response = await fetch(`${API_BASE}/journal?days=30`, {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });

      if (!response.ok) {
        console.error('[Journal] Fetch failed with status:', response.status);
        throw new Error('Failed to fetch journal entries');
      }

      const data = await response.json();
      console.log('[Journal] Raw data received:', data.length, 'entries');
      console.log('[Journal] All dates in response:', data.map((e: JournalEntry) => e.date));
      
      const today = new Date().toISOString().split('T')[0];
      console.log('[Journal] Today\'s date:', today);
      
      const todayEntries = data.filter((e: JournalEntry) => e.date === today);
      console.log(`[Journal] Filtered to ${todayEntries.length} entries for today`);
      
      if (todayEntries.length > 0) {
        console.log('[Journal] Today\'s entries:', todayEntries.map((e: JournalEntry) => ({
          id: e.id,
          emotion: e.emotion,
          content_preview: e.content.substring(0, 50)
        })));
      }
      
      setEntries(todayEntries); // Show only today's entries
      
      // Always start with a blank editor for new entry
      setContent('');
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred');
      console.error('[Journal] Error fetching entries:', err);
    } finally {
      setLoading(false);
    }
  };

  const saveEntry = async () => {
    if (!content.trim()) {
      setError('Journal entry cannot be empty');
      return;
    }

    if (content.length > 2000) {
      setError('Journal entry exceeds 2000 character limit');
      return;
    }

    setSaving(true);
    setError(null);

    try {
      const today = new Date().toISOString().split('T')[0];

      // Always create a new entry
      const url = `${API_BASE}/journal`;
      const method = 'POST';

      const response = await fetch(url, {
        method,
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${localStorage.getItem('token')}`,
        },
        body: JSON.stringify({
          content,
          date: today,
        }),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Failed to save journal entry');
      }

      const savedEntry = await response.json();
      
      console.log('[Journal] Save successful');
      console.log(`[Journal] Emotion from backend: ${savedEntry.emotion} (${savedEntry.emotion_confidence})`);
      console.log('[Journal] Full response:', savedEntry);
      
      // Verify emotion is not inappropriately neutral
      if (savedEntry.emotion === 'neutral' && savedEntry.emotion_confidence && savedEntry.emotion_confidence <= 0.55) {
        console.warn('[Journal] WARNING: Received neutral emotion with low confidence - may indicate ML fallback');
      }
      
      // Add new entry to the list
      setEntries([savedEntry, ...entries]);
      
      // Clear content for next entry
      setContent('');

      // Show inline feedback using BACKEND response values only
      setSaveFeedback({
        show: true,
        emotion: savedEntry.emotion,
        confidence: savedEntry.emotion_confidence,
      });

      // Auto-hide feedback after 10 seconds
      setTimeout(() => setSaveFeedback({ show: false }), 10000);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to save entry');
      console.error('[Journal] Error saving entry:', err);
    } finally {
      setSaving(false);
    }
  };

  const generateInsight = async () => {
    setGeneratingInsight(true);
    setError(null);
    setInsight(null);

    try {
      // CRITICAL: Auto-save journal before generating insights if there's content
      const today = new Date().toISOString().split('T')[0];
      if (selectedDate === today && content.trim().length > 0) {
        console.log('[Journal] Auto-saving journal before generating insights...');
        
        // Always create new entry
        const url = `${API_BASE}/journal`;
        const method = 'POST';

        const saveResponse = await fetch(url, {
          method,
          headers: {
            'Content-Type': 'application/json',
            Authorization: `Bearer ${localStorage.getItem('token')}`,
          },
          body: JSON.stringify({
            content,
            date: today,
          }),
        });

        if (!saveResponse.ok) {
          throw new Error('Please save your journal entry before generating insights.');
        }

        const savedEntry = await saveResponse.json();
        
        // Add to entries list and clear content
        setEntries([savedEntry, ...entries]);
        setContent('');
        
        console.log('[Journal] Auto-save successful');
      }

      // Now generate the insight
      console.log(`[Journal] Generating reflection for ${selectedDate}...`);
      console.log(`[Journal] Using regenerate=true to include all ${entries.length} entries from today`);
      
      const response = await fetch(`${API_BASE}/journal/summarize`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${localStorage.getItem('token')}`,
        },
        body: JSON.stringify({
          date: selectedDate,
          regenerate: true,  // Always regenerate to use latest entries
        }),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Failed to generate insight');
      }

      const insightData = await response.json();
      setInsight(insightData);
      
      // Enhanced logging for insight generation
      console.log('[Journal] ✅ Reflection generated successfully');
      console.log('[Journal] 📊 Insight Details:', {
        date: insightData.date,
        summary_length: insightData.summary?.summary?.length || 0,
        dominant_emotions: insightData.summary?.dominant_emotions || [],
        has_patterns: !!insightData.summary?.patterns,
        has_positive_signals: !!insightData.summary?.positive_signals,
        has_gentle_suggestion: !!insightData.summary?.gentle_suggestion
      });
      console.log('[Journal] 💡 Gentle Suggestion:', insightData.summary?.gentle_suggestion);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to generate insight');
      console.error('Error generating insight:', err);
    } finally {
      setGeneratingInsight(false);
    }
  };

  const formatDate = (dateStr: string) => {
    return new Date(dateStr).toLocaleDateString('en-US', {
      weekday: 'long',
      year: 'numeric',
      month: 'long',
      day: 'numeric',
    });
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-purple-50 via-white to-blue-50">
      <Navigation 
        currentPage="journal" 
        onNavigate={onNavigate} 
        onLogout={onLogout} 
        user={user} 
        onOpenNotifications={onOpenNotifications} 
      />
      
      <div className="max-w-4xl mx-auto p-6 pb-24">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-4xl font-bold text-gray-800 mb-2">📖 Daily Journal</h1>
          <p className="text-gray-600">
            Write your thoughts, track your emotions, and gain AI-powered insights
          </p>
        </div>

        {error && (
          <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-lg text-red-700">
            {error}
          </div>
        )}

        {/* Today's Entry */}
        <div className="mb-8 bg-white rounded-2xl shadow-lg p-6">
          <h2 className="text-2xl font-semibold text-gray-800 mb-4">
            Today's Entry
          </h2>
          <textarea
            className="w-full h-64 p-4 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent resize-none"
            placeholder="How was your day? What are you feeling? Share your thoughts here..."
            value={content}
            onChange={(e) => setContent(e.target.value)}
            maxLength={2000}
          />
          <div className="flex justify-between items-center mt-4">
            <span className="text-sm text-gray-500">
              {content.length} / 2000 characters
            </span>
            <button
              onClick={saveEntry}
              disabled={saving || !content.trim()}
              className="px-8 py-3 bg-gradient-to-r from-purple-600 to-violet-700 text-white font-bold text-lg rounded-lg hover:from-purple-700 hover:to-violet-800 disabled:from-gray-300 disabled:to-gray-400 disabled:cursor-not-allowed transition-all shadow-lg hover:shadow-xl"
            >
              {saving ? '💾 Saving...' : '💾 Save Entry'}
            </button>
          </div>

          {/* Inline Feedback Panel */}
          {saveFeedback.show && (
            <div className={`mt-4 p-4 rounded-lg border-2 animate-fade-in ${
              saveFeedback.emotion
                ? emotionColors[saveFeedback.emotion.toLowerCase()] || emotionColors.neutral
                : 'bg-green-50 border-green-300 text-green-800'
            }`}>
              <div className="flex items-center gap-3">
                <span className="text-2xl">✅</span>
                <div>
                  <div className="font-semibold">Saved successfully</div>
                  {saveFeedback.emotion && saveFeedback.confidence && (
                    <div className="text-sm mt-1">
                      Emotion detected: <span className="font-bold">{saveFeedback.emotion}</span>{' '}
                      {emotionEmojis[saveFeedback.emotion.toLowerCase()] || '😐'}{' '}
                      ({Math.round(saveFeedback.confidence * 100)}% confidence)
                    </div>
                  )}
                </div>
              </div>
            </div>
          )}
        </div>

        {/* Insights Section */}
        <div className="mb-8 bg-white rounded-2xl shadow-lg p-6">
          <h2 className="text-2xl font-semibold text-gray-800 mb-4">
            ✨ Daily Reflection
          </h2>
          <p className="text-gray-600 mb-4">
            Generate AI-powered insights from your journal entries and emotions
          </p>

          <div className="flex gap-4 mb-6">
            <input
              type="date"
              aria-label="Select date for journal insight"
              value={selectedDate}
              onChange={(e) => setSelectedDate(e.target.value)}
              className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500"
            />
            <button
              onClick={generateInsight}
              disabled={generatingInsight}
              className="px-6 py-2 bg-gradient-to-r from-purple-600 to-blue-600 text-white rounded-lg hover:from-purple-700 hover:to-blue-700 disabled:from-gray-300 disabled:to-gray-400 disabled:cursor-not-allowed transition-all"
            >
              {generatingInsight ? 'Generating...' : 'Generate Reflection'}
            </button>
          </div>

          {insight && (
            <div className="space-y-4 animate-fade-in">
              <div className="p-4 bg-purple-50 border border-purple-200 rounded-lg">
                <h3 className="font-semibold text-purple-900 mb-2">💭 Summary</h3>
                <p className="text-gray-700">{insight.summary.summary}</p>
              </div>

              <div className="p-4 bg-blue-50 border border-blue-200 rounded-lg">
                <h3 className="font-semibold text-blue-900 mb-2">😊 Dominant Emotions</h3>
                <div className="flex flex-wrap gap-2">
                  {insight.summary.dominant_emotions.map((emotion) => (
                    <span
                      key={emotion}
                      className={`px-3 py-1 rounded-full text-sm border ${
                        emotionColors[emotion.toLowerCase()] || emotionColors.neutral
                      }`}
                    >
                      {emotionEmojis[emotion.toLowerCase()] || emotionEmojis.neutral}{' '}
                      {emotion}
                    </span>
                  ))}
                </div>
              </div>

              <div className="p-4 bg-green-50 border border-green-200 rounded-lg">
                <h3 className="font-semibold text-green-900 mb-2">📈 Patterns</h3>
                <p className="text-gray-700">{insight.summary.patterns}</p>
              </div>

              <div className="p-4 bg-yellow-50 border border-yellow-200 rounded-lg">
                <h3 className="font-semibold text-yellow-900 mb-2">✨ Positive Signals</h3>
                <p className="text-gray-700">{insight.summary.positive_signals}</p>
              </div>

              <div className="p-4 bg-pink-50 border border-pink-200 rounded-lg">
                <h3 className="font-semibold text-pink-900 mb-2">💡 Gentle Suggestion</h3>
                <p className="text-gray-700">{insight.summary.gentle_suggestion}</p>
              </div>
            </div>
          )}
        </div>

        {/* Previous Entries */}
        <div className="bg-white rounded-2xl shadow-lg p-6">
          <h2 className="text-2xl font-semibold text-gray-800 mb-4">
            📚 Today's Entries
          </h2>

          {loading ? (
            <p className="text-gray-500">Loading entries...</p>
          ) : entries.length === 0 ? (
            <p className="text-gray-500">No journal entries for today yet. Start writing!</p>
          ) : (
            <div className="space-y-4">
              {entries.map((entry) => (
                <div
                  key={entry.id}
                  className="p-4 border border-gray-200 rounded-lg hover:border-purple-300 transition-colors"
                >
                  <div className="flex justify-between items-start mb-2">
                    <h3 className="font-semibold text-gray-800">
                      {formatDate(entry.date)}
                    </h3>
                    {entry.emotion && (
                      <span
                        className={`px-3 py-1 rounded-full text-sm border ${
                          emotionColors[entry.emotion.toLowerCase()] ||
                          emotionColors.neutral
                        }`}
                      >
                        {emotionEmojis[entry.emotion.toLowerCase()] ||
                          emotionEmojis.neutral}{' '}
                        {entry.emotion}
                        {entry.emotion_confidence && (
                          <span className="ml-1 text-xs">
                            ({Math.round(entry.emotion_confidence * 100)}%)
                          </span>
                        )}
                      </span>
                    )}
                  </div>
                  <p className="text-gray-700 whitespace-pre-wrap">
                    {entry.content.length > 200
                      ? entry.content.slice(0, 200) + '...'
                      : entry.content}
                  </p>
                  <p className="text-xs text-gray-400 mt-2">
                    Written on {new Date(entry.created_at).toLocaleString()}
                  </p>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
