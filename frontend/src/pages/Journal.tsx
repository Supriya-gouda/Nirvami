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
  joy: '😊',
  sadness: '😢',
  anger: '😠',
  fear: '😨',
  surprise: '😮',
  disgust: '🤢',
  neutral: '😐',
};

const emotionColors: { [key: string]: string } = {
  joy: 'bg-yellow-100 text-yellow-800 border-yellow-300',
  sadness: 'bg-blue-100 text-blue-800 border-blue-300',
  anger: 'bg-red-100 text-red-800 border-red-300',
  fear: 'bg-purple-100 text-purple-800 border-purple-300',
  surprise: 'bg-pink-100 text-pink-800 border-pink-300',
  disgust: 'bg-green-100 text-green-800 border-green-300',
  neutral: 'bg-gray-100 text-gray-800 border-gray-300',
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
      console.log('[Journal] Fetching entries...');
      const response = await fetch(`${API_BASE}/journal?days=30`, {
        headers: {
          Authorization: `Bearer ${localStorage.getItem('token')}`,
        },
      });

      if (!response.ok) {
        throw new Error('Failed to fetch journal entries');
      }

      const data = await response.json();
      const today = new Date().toISOString().split('T')[0];
      const todayEntries = data.filter((e: JournalEntry) => e.date === today);
      
      console.log(`[Journal] Loaded ${todayEntries.length} entries for today`);
      setEntries(data);

      // Load most recent entry of today if exists
      if (todayEntries.length > 0) {
        const latestToday = todayEntries[todayEntries.length - 1];
        setContent(latestToday.content);
        console.log('[Journal] Loaded latest today entry into editor');
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred');
      console.error('Error fetching entries:', err);
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
      const existingEntry = entries.find((e) => e.date === today);

      const url = existingEntry
        ? `${API_BASE}/journal/${existingEntry.id}`
        : `${API_BASE}/journal`;

      const method = existingEntry ? 'PUT' : 'POST';

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
      
      // Update entries list
      if (existingEntry) {
        setEntries(entries.map((e) => (e.id === savedEntry.id ? savedEntry : e)));
      } else {
        setEntries([savedEntry, ...entries]);
      }

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
        const existingEntry = entries.find((e) => e.date === today);
        
        // Only save if content has changed or no entry exists
        const needsSave = !existingEntry || existingEntry.content !== content;
        
        if (needsSave) {
          console.log('[Journal] Auto-saving journal before generating insights...');
          
          const url = existingEntry
            ? `${API_BASE}/journal/${existingEntry.id}`
            : `${API_BASE}/journal`;
          const method = existingEntry ? 'PUT' : 'POST';

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
          
          // Update entries list
          if (existingEntry) {
            setEntries(entries.map((e) => (e.id === savedEntry.id ? savedEntry : e)));
          } else {
            setEntries([savedEntry, ...entries]);
          }
          
          console.log('[Journal] Auto-save successful');
        }
      }

      // Now generate the insight
      console.log(`[Journal] Generating reflection for ${selectedDate}...`);
      const response = await fetch(`${API_BASE}/journal/summarize`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${localStorage.getItem('token')}`,
        },
        body: JSON.stringify({
          date: selectedDate,
          regenerate: false,
        }),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Failed to generate insight');
      }

      const insightData = await response.json();
      setInsight(insightData);
      console.log('[Journal] Reflection generated successfully');
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
            📚 Previous Entries
          </h2>

          {loading ? (
            <p className="text-gray-500">Loading entries...</p>
          ) : entries.length === 0 ? (
            <p className="text-gray-500">No journal entries yet. Start writing!</p>
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
