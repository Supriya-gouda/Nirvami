import { useState, useEffect } from 'react';
import { motion } from 'motion/react';
import {
  Watch,
  Activity,
  Heart,
  Bed,
  Footprints,
  Brain,
  TrendingUp,
  Sparkles,
  RefreshCw,
  Plus,
  AlertCircle,
  Check,
  Upload
} from 'lucide-react';
import { Navigation } from './Navigation';
import { Button } from './ui/button';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from './ui/card';
import { Input } from './ui/input';
import { Label } from './ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from './ui/select';
import { Alert, AlertDescription } from './ui/alert';
import { toast } from 'sonner';
import { ManualHealthEntry } from './ManualHealthEntry';
import { WatchDataUpload } from './WatchDataUpload';
import api from '../services/api';
import type { PageType, User } from '../App';
import type { WearableSnapshot, SyncWearableRequest } from '../types/api.types';

interface DevicePageProps {
  user: User | null;
  onNavigate: (page: PageType) => void;
  onLogout?: () => void;
  onOpenNotifications?: () => void;
}

export function DevicePage({ user, onNavigate, onLogout, onOpenNotifications }: DevicePageProps) {
  const [latestData, setLatestData] = useState<WearableSnapshot | null>(null);
  const [wearableSummary, setWearableSummary] = useState<any>(null);
  const [loading, setLoading] = useState(false);
  const [showManualInput, setShowManualInput] = useState(false);
  const [analyzing, setAnalyzing] = useState(false);
  const [analysisResult, setAnalysisResult] = useState<any>(null);
  const [history, setHistory] = useState<any[]>([]);
  const [loadingHistory, setLoadingHistory] = useState(false);

  // Ayurveda recommendations
  const [recommendations, setRecommendations] = useState<any>(null);
  const [generatingRecs, setGeneratingRecs] = useState(false);

  useEffect(() => {
    fetchLatestData();
    fetchHistory();
  }, []);

  const fetchLatestData = async () => {
    if (!api.isAuthenticated()) return;

    try {
      setLoading(true);
      // Fetch the latest wearable data using new endpoint
      const latest = await api.getLatestWearableData().catch(() => null);
      
      if (latest && latest.hasData) {
        setWearableSummary(latest);
        setLatestData(latest.data);
        
        // Auto-fetch analysis if data exists
        await fetchLatestAnalysis();
      } else {
        setWearableSummary(null);
        setLatestData(null);
        setAnalysisResult(null);
      }
    } catch (error) {
      console.error('Failed to fetch wearable data:', error);
    } finally {
      setLoading(false);
    }
  };

  const fetchLatestAnalysis = async () => {
    if (!api.isAuthenticated()) return;

    try {
      // Silently fetch latest analysis without showing loading state
      const result = await api.analyzeWearableHealth();
      if (result?.analysis) {
        setAnalysisResult(result.analysis);
      }
    } catch (error) {
      console.error('Failed to fetch analysis:', error);
      // Don't show error to user - analysis is optional
    }
  };

  const fetchHistory = async () => {
    if (!api.isAuthenticated()) return;

    try {
      setLoadingHistory(true);
      const historyData = await api.getWearableHistory(30);
      setHistory(historyData.data || []);
    } catch (error) {
      console.error('Failed to fetch history:', error);
    } finally {
      setLoadingHistory(false);
    }
  };

  const handleAnalyze = async () => {
    if (!api.isAuthenticated()) return;

    try {
      setAnalyzing(true);
      setAnalysisResult(null);
      
      const result = await api.analyzeWearableHealth();
      setAnalysisResult(result.analysis);
      
      if (result.analysis.has_risks) {
        toast.warning(`${result.analysis.risks.length} health concern(s) detected. Check notifications.`);
      } else {
        toast.success('No health risks detected! Keep up the good work!');
      }
    } catch (error) {
      console.error('Failed to analyze health data:', error);
      toast.error('Failed to analyze health data');
    } finally {
      setAnalyzing(false);
    }
  };

  const handleAppleWatchSync = async () => {
    // This would integrate with Apple HealthKit
    // For now, show a placeholder message
    toast.info('Apple Watch integration coming soon! Use manual input for now.');

    // In production, this would:
    // 1. Request HealthKit permissions
    // 2. Fetch data from Apple Health
    // 3. Sync to backend
  };

  const generateAyurvedaRecommendations = async () => {
    if (!latestData) {
      toast.error('No wearable data available');
      return;
    }

    try {
      setGeneratingRecs(true);

      // Get dosha-based recommendations
      const doshaData = await api.getLatestDosha();
      const recommendations = await api.getDoshaRecommendations();

      // Combine with wearable insights
      const insights = {
        ...recommendations,
        wearable_insights: generateWearableInsights(latestData, doshaData)
      };

      setRecommendations(insights);
      toast.success('Recommendations generated!');

    } catch (error) {
      console.error('Failed to generate recommendations:', error);
      toast.error('Failed to generate recommendations');
    } finally {
      setGeneratingRecs(false);
    }
  };

  const generateWearableInsights = (data: WearableSnapshot, dosha: any) => {
    const insights = [];

    // Sleep analysis
    if (typeof data.sleep_hours === 'number' && data.sleep_hours < 7) {
      insights.push({
        category: 'Sleep',
        issue: 'Insufficient sleep detected',
        recommendation: dosha?.primary_dosha === 'vata'
          ? 'Practice Shavasana (Corpse Pose) before bed and drink warm milk with nutmeg'
          : 'Establish a calming bedtime routine with gentle yoga stretches'
      });
    }

    // Heart rate analysis
    if (typeof data.heart_rate === 'number' && data.heart_rate > 100) {
      insights.push({
        category: 'Heart Health',
        issue: 'Elevated resting heart rate',
        recommendation: 'Practice Nadi Shodhana (Alternate Nostril Breathing) to calm the nervous system'
      });
    }

    // Stress level analysis
    if (typeof data.stress_level === 'string' && data.stress_level === 'high') {
      insights.push({
        category: 'Stress Management',
        issue: 'High stress levels detected',
        recommendation: dosha?.primary_dosha === 'pitta'
          ? 'Practice cooling pranayama like Sheetali and avoid spicy foods'
          : 'Try meditation and gentle yoga like Yin or Restorative yoga'
      });
    }

    // Activity level
    if (typeof data.steps === 'number' && data.steps < 5000) {
      insights.push({
        category: 'Activity',
        issue: 'Low physical activity',
        recommendation: 'Start with gentle Sun Salutations (Surya Namaskar) to energize'
      });
    }

    return insights;
  };

  const getStressColor = (level: string) => {
    switch (level) {
      case 'low': return 'text-green-600 bg-green-50';
      case 'moderate': return 'text-yellow-600 bg-yellow-50';
      case 'high': return 'text-red-600 bg-red-50';
      default: return 'text-gray-600 bg-gray-50';
    }
  };

  const getSleepColor = (quality: string) => {
    switch (quality) {
      case 'excellent': return 'text-purple-600 bg-purple-50';
      case 'good': return 'text-green-600 bg-green-50';
      case 'fair': return 'text-yellow-600 bg-yellow-50';
      case 'poor': return 'text-red-600 bg-red-50';
      default: return 'text-gray-600 bg-gray-50';
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-purple-50 via-blue-50 to-pink-50">
      <Navigation currentPage="device" onNavigate={onNavigate} onLogout={onLogout} user={user} onOpenNotifications={onOpenNotifications} />

      <div className="container mx-auto px-4 py-8 max-w-6xl">
        {/* Header */}
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          className="text-center mb-8"
        >
          <div className="flex items-center justify-center gap-3 mb-4">
            <Watch className="w-12 h-12 text-purple-600" />
            <h1 className="text-4xl font-bold text-gray-800">Wearable Devices</h1>
          </div>
          <p className="text-gray-600 max-w-2xl mx-auto">
            Connect your fitness tracker or manually input your health metrics for personalized Ayurvedic recommendations
          </p>
        </motion.div>

        {/* Device Connection Cards */}
        <div className="grid md:grid-cols-2 gap-6 mb-8">
          {/* Apple Watch */}
          <motion.div
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
          >
            <Card className="h-full">
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Watch className="w-5 h-5 text-gray-700" />
                  Apple Watch
                </CardTitle>
                <CardDescription>Sync data from Apple Health</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {/* XML Upload Component */}
                  <WatchDataUpload onSuccess={fetchLatestData} />
                </div>
              </CardContent>
            </Card>
          </motion.div>

          {/* Manual Input */}
          <motion.div
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
          >
            <Card className="h-full border-purple-100 shadow-lg">
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Activity className="w-5 h-5 text-purple-600" />
                  Manual Input
                </CardTitle>
                <CardDescription>Enter your daily health metrics</CardDescription>
              </CardHeader>
              <CardContent>
                {!showManualInput ? (
                  <div className="text-center py-8">
                    <div className="w-16 h-16 bg-purple-100 rounded-full flex items-center justify-center mx-auto mb-4">
                      <Plus className="w-8 h-8 text-purple-600" />
                    </div>
                    <h3 className="text-lg font-medium text-gray-800 mb-2">
                      {wearableSummary?.hasData ? 'Add New Entry' : 'Log Daily Metrics'}
                    </h3>
                    <p className="text-gray-600 mb-6">
                      Track your sleep, heart rate, and activity levels for better insights
                    </p>
                      <button
                        onClick={() => {
                          console.log('Manual entry button clicked');
                          setShowManualInput(true);
                        }}
                        style={{
                          display: 'inline-flex',
                          alignItems: 'center',
                          justifyContent: 'center',
                          padding: '12px 24px',
                          backgroundColor: '#9333ea',
                          color: 'white',
                          fontWeight: '500',
                          fontSize: '16px',
                          borderRadius: '8px',
                          border: 'none',
                          boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06)',
                          cursor: 'pointer',
                          transition: 'all 0.2s ease-in-out',
                        }}
                        onMouseEnter={(e) => {
                          e.currentTarget.style.backgroundColor = '#7e22ce';
                          e.currentTarget.style.boxShadow = '0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05)';
                        }}
                        onMouseLeave={(e) => {
                          e.currentTarget.style.backgroundColor = '#9333ea';
                          e.currentTarget.style.boxShadow = '0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06)';
                        }}
                        onMouseDown={(e) => {
                          e.currentTarget.style.transform = 'scale(0.95)';
                        }}
                        onMouseUp={(e) => {
                          e.currentTarget.style.transform = 'scale(1)';
                        }}
                      >
                        <Plus className="w-4 h-4" style={{ marginRight: '8px' }} />
                        {wearableSummary?.hasData ? 'Log New Data' : 'Start Logging'}
                      </button>
                    </div>
                  ) : (
                    <ManualHealthEntry
                      onSuccess={() => {
                        console.log('Manual entry success callback');
                        setShowManualInput(false);
                        fetchLatestData();
                        fetchHistory();
                        toast.success('Health data saved successfully!');
                      }}
                      onCancel={() => {
                        console.log('Manual entry cancelled');
                        setShowManualInput(false);
                      }}
                    />
                  )}
                </CardContent>
              </Card>
            </motion.div>
          </div>

          {/* Centered Analyze Button */}
          {wearableSummary?.hasData && (
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              className="mt-8 flex justify-center"
            >
              <button
                onClick={handleAnalyze}
                disabled={analyzing}
                style={{
                  display: 'inline-flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  gap: '8px',
                  padding: '14px 32px',
                  background: 'linear-gradient(to right, #9333ea, #2563eb)',
                  color: 'white',
                  fontWeight: '600',
                  fontSize: '16px',
                  borderRadius: '8px',
                  border: 'none',
                  boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06)',
                  cursor: analyzing ? 'not-allowed' : 'pointer',
                  opacity: analyzing ? 0.7 : 1,
                  transition: 'all 0.2s ease-in-out',
                }}
                onMouseEnter={(e) => {
                  if (!analyzing) {
                    e.currentTarget.style.background = 'linear-gradient(to right, #7e22ce, #1d4ed8)';
                    e.currentTarget.style.boxShadow = '0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05)';
                    e.currentTarget.style.transform = 'translateY(-2px)';
                  }
                }}
                onMouseLeave={(e) => {
                  e.currentTarget.style.background = 'linear-gradient(to right, #9333ea, #2563eb)';
                  e.currentTarget.style.boxShadow = '0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06)';
                  e.currentTarget.style.transform = 'translateY(0)';
                }}
              >
                {analyzing ? (
                  <>
                    <RefreshCw className="w-5 h-5 mr-2 animate-spin" />
                    Analyzing Your Health Data...
                  </>
                ) : (
                  <>
                    <Sparkles className="w-5 h-5 mr-2" />
                    Analyze Health Data
                  </>
                )}
              </button>
            </motion.div>
          )}

          {/* Unified Health Analysis Results */}
          {analysisResult && (
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              className="mt-8"
            >
              <Card className="border-purple-100 shadow-lg">
                <CardHeader>
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-2">
                      <Brain className="w-6 h-6 text-purple-600" />
                      <CardTitle>Your Health Analysis</CardTitle>
                    </div>
                    {wearableSummary?.data && (
                      <span className="text-xs px-3 py-1 bg-purple-50 text-purple-700 rounded-full">
                        {wearableSummary.data.source === 'watch' ? '⌚ Apple Watch' : '✍️ Manual Entry'}
                      </span>
                    )}
                  </div>
                  <CardDescription>
                    Based on your latest synced data
                    {wearableSummary?.data?.date && ` • ${new Date(wearableSummary.data.date).toLocaleDateString()}`}
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="space-y-4">
                    {/* Risk Level Badge */}
                    <div className="flex items-center gap-3">
                      <span className="text-sm font-medium text-gray-700">Risk Level:</span>
                      <span className={`px-4 py-2 rounded-full text-sm font-semibold ${
                        analysisResult.risk_level === 'critical' ? 'bg-red-100 text-red-700 border border-red-300' :
                        analysisResult.risk_level === 'high' ? 'bg-orange-100 text-orange-700 border border-orange-300' :
                        analysisResult.risk_level === 'medium' ? 'bg-yellow-100 text-yellow-700 border border-yellow-300' :
                        'bg-green-100 text-green-700 border border-green-300'
                      }`}>
                        {analysisResult.risk_level.toUpperCase()}
                      </span>
                    </div>

                    {/* Risks or Success Message */}
                    {analysisResult.risks && analysisResult.risks.length > 0 ? (
                      <div className="bg-red-50 border border-red-200 rounded-lg p-4">
                        <h4 className="font-semibold text-base mb-3 text-red-900 flex items-center gap-2">
                          <AlertCircle className="w-5 h-5" />
                          Detected Concerns
                        </h4>
                        <ul className="space-y-2">
                          {analysisResult.risks.map((risk: string, idx: number) => (
                            <li key={idx} className="text-sm flex items-start gap-2 text-red-800">
                              <span className="text-red-600 mt-0.5">•</span>
                              <span>{risk}</span>
                            </li>
                          ))}
                        </ul>
                      </div>
                    ) : (
                      <div className="bg-green-50 border border-green-200 rounded-lg p-4">
                        <p className="text-base text-green-800 flex items-center gap-2">
                          <Check className="w-5 h-5" />
                          ✨ No health risks detected! Your metrics look good.
                        </p>
                      </div>
                    )}

                    {/* Recommendations */}
                    {analysisResult.recommendations && analysisResult.recommendations.length > 0 && (
                      <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
                        <h4 className="font-semibold text-base mb-3 text-blue-900 flex items-center gap-2">
                          <Check className="w-5 h-5" />
                          Recommendations
                        </h4>
                        <ul className="space-y-2">
                          {analysisResult.recommendations.map((rec: string, idx: number) => (
                            <li key={idx} className="text-sm flex items-start gap-2 text-blue-800">
                              <span className="text-blue-600 mt-0.5">✓</span>
                              <span>{rec}</span>
                            </li>
                          ))}
                        </ul>
                      </div>
                    )}

                    {analysisResult.has_risks && (
                      <Alert className="bg-purple-50 border-purple-200">
                        <AlertCircle className="h-4 w-4 text-purple-600" />
                        <AlertDescription className="text-purple-700 text-sm">
                          💬 Analysis results have been sent to your notifications
                        </AlertDescription>
                      </Alert>
                    )}
                  </div>
                </CardContent>
              </Card>
            </motion.div>
          )}

          {/* History Section */}
        {history.length > 0 && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="mt-8"
          >
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <TrendingUp className="w-5 h-5 text-blue-600" />
                  Entry History
                </CardTitle>
                <CardDescription>
                  Your latest 5 health data entries (showing {Math.min(5, history.length)} of {history.length} total)
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-3 max-h-96 overflow-y-auto">
                  {loadingHistory ? (
                    <div className="text-center py-8">
                      <RefreshCw className="w-8 h-8 text-gray-400 animate-spin mx-auto mb-2" />
                      <p className="text-gray-500">Loading history...</p>
                    </div>
                  ) : (
                    history.slice(0, 5).map((entry: any, index: number) => (
                      <div
                        key={entry.id || index}
                        className="p-4 bg-gray-50 rounded-lg border border-gray-200 hover:border-purple-300 transition-colors"
                      >
                        <div className="flex items-center justify-between mb-2">
                          <span className="font-semibold text-gray-800">
                            {new Date(entry.date).toLocaleDateString('en-US', {
                              weekday: 'short',
                              year: 'numeric',
                              month: 'short',
                              day: 'numeric'
                            })}
                          </span>
                          <span className="text-xs px-2 py-1 rounded-full bg-purple-100 text-purple-700">
                            {entry.source || 'manual'}
                          </span>
                        </div>
                        <div className="grid grid-cols-2 md:grid-cols-4 gap-3 text-sm">
                          {entry.sleep_hours !== null && entry.sleep_hours !== undefined && (
                            <div className="flex items-center gap-2">
                              <Bed className="w-4 h-4 text-indigo-500" />
                              <span className="text-gray-600">{entry.sleep_hours}h sleep</span>
                            </div>
                          )}
                          {entry.avg_heart_rate && (
                            <div className="flex items-center gap-2">
                              <Heart className="w-4 h-4 text-red-500" />
                              <span className="text-gray-600">{entry.avg_heart_rate} bpm</span>
                            </div>
                          )}
                          {entry.steps && (
                            <div className="flex items-center gap-2">
                              <Footprints className="w-4 h-4 text-orange-500" />
                              <span className="text-gray-600">{entry.steps.toLocaleString()} steps</span>
                            </div>
                          )}
                          {entry.stress_level !== null && entry.stress_level !== undefined && (
                            <div className="flex items-center gap-2">
                              <Activity className="w-4 h-4 text-blue-500" />
                              <span className="text-gray-600">Stress: {entry.stress_level}/10</span>
                            </div>
                          )}
                        </div>
                      </div>
                    ))
                  )}
                </div>
              </CardContent>
            </Card>
          </motion.div>
        )}

        {/* Latest Data & Recommendations */}
        {latestData && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="space-y-8"
          >
            <div className="flex items-center justify-between">
              <h2 className="text-2xl font-bold text-gray-800">Latest Health Insights</h2>
              <button
                onClick={generateAyurvedaRecommendations}
                disabled={generatingRecs}
                style={{
                  display: 'inline-flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  gap: '8px',
                  padding: '10px 16px',
                  background: 'linear-gradient(to right, #f97316, #ef4444)',
                  color: 'white',
                  fontWeight: '500',
                  fontSize: '14px',
                  borderRadius: '6px',
                  border: 'none',
                  cursor: generatingRecs ? 'not-allowed' : 'pointer',
                  opacity: generatingRecs ? 0.5 : 1,
                  transition: 'all 0.2s ease-in-out',
                }}
                onMouseEnter={(e) => {
                  if (!generatingRecs) {
                    e.currentTarget.style.background = 'linear-gradient(to right, #ea580c, #dc2626)';
                  }
                }}
                onMouseLeave={(e) => {
                  e.currentTarget.style.background = 'linear-gradient(to right, #f97316, #ef4444)';
                }}
              >
                {generatingRecs ? (
                  <>
                    <Sparkles className="w-4 h-4 mr-2 animate-spin" />
                    Analyzing...
                  </>
                ) : (
                  <>
                    <Brain className="w-4 h-4 mr-2" />
                    Generate Ayurvedic Insights
                  </>
                )}
              </button>
            </div>

            {/* Metrics Grid */}
            <div className="grid md:grid-cols-4 gap-4">
              <Card>
                <CardContent className="pt-6">
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-sm font-medium text-gray-500">Heart Rate</span>
                    <Heart className="w-4 h-4 text-red-500" />
                  </div>
                  <div className="text-2xl font-bold text-gray-800">
                    {latestData.heart_rate} <span className="text-sm font-normal text-gray-500">bpm</span>
                  </div>
                </CardContent>
              </Card>
              <Card>
                <CardContent className="pt-6">
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-sm font-medium text-gray-500">Sleep Quality</span>
                    <Bed className="w-4 h-4 text-purple-500" />
                  </div>
                  <div className={`text-2xl font-bold capitalize ${getSleepColor(latestData.sleep_quality || 'good').split(' ')[0]}`}>
                    {latestData.sleep_quality || 'Good'}
                  </div>
                </CardContent>
              </Card>
              <Card>
                <CardContent className="pt-6">
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-sm font-medium text-gray-500">Daily Steps</span>
                    <Footprints className="w-4 h-4 text-orange-500" />
                  </div>
                  <div className="text-2xl font-bold text-gray-800">
                    {latestData.steps?.toLocaleString()}
                  </div>
                </CardContent>
              </Card>
              <Card>
                <CardContent className="pt-6">
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-sm font-medium text-gray-500">Stress Level</span>
                    <Activity className="w-4 h-4 text-blue-500" />
                  </div>
                  <div className={`text-2xl font-bold capitalize ${getStressColor(latestData.stress_level || 'low').split(' ')[0]}`}>
                    {latestData.stress_level || 'Low'}
                  </div>
                </CardContent>
              </Card>
            </div>

            {/* Recommendations */}
            {recommendations && (
              <motion.div
                initial={{ opacity: 0, scale: 0.95 }}
                animate={{ opacity: 1, scale: 1 }}
                className="grid md:grid-cols-2 gap-6"
              >
                <Card className="bg-gradient-to-br from-purple-50 to-white border-purple-100">
                  <CardHeader>
                    <CardTitle className="flex items-center gap-2">
                      <Sparkles className="w-5 h-5 text-purple-600" />
                      Ayurvedic Recommendations
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-4">
                      {recommendations.wearable_insights?.map((insight: any, index: number) => (
                        <div key={index} className="border-l-4 border-purple-500 pl-4 py-2">
                          <h4 className="font-semibold text-gray-800 mb-1">{insight.category}</h4>
                          <p className="text-sm text-red-600 mb-2">{insight.issue}</p>
                          <p className="text-sm text-purple-700 font-medium">
                            💡 {insight.recommendation}
                          </p>
                        </div>
                      ))}

                      {recommendations.yoga_poses && (
                        <div className="mt-6">
                          <h4 className="font-semibold text-gray-800 mb-3">Recommended Yoga Poses</h4>
                          <div className="grid md:grid-cols-2 gap-3">
                            {recommendations.yoga_poses.slice(0, 4).map((pose: string, index: number) => (
                              <div key={index} className="bg-gradient-to-r from-purple-50 to-blue-50 p-3 rounded-lg">
                                <p className="text-sm font-medium text-gray-700">🧘‍♀️ {pose}</p>
                              </div>
                            ))}
                          </div>
                        </div>
                      )}
                    </div>
                  </CardContent>
                </Card>

                <Card className="bg-gradient-to-br from-orange-50 to-white border-orange-100">
                  <CardHeader>
                    <CardTitle className="flex items-center gap-2">
                      <TrendingUp className="w-5 h-5 text-orange-600" />
                      Lifestyle Adjustments
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <ul className="space-y-3">
                      <li className="flex items-start gap-2">
                        <div className="w-1.5 h-1.5 rounded-full bg-orange-400 mt-2" />
                        <span className="text-gray-600">Align your sleep schedule with circadian rhythms (10 PM - 6 AM)</span>
                      </li>
                      <li className="flex items-start gap-2">
                        <div className="w-1.5 h-1.5 rounded-full bg-orange-400 mt-2" />
                        <span className="text-gray-600">Practice grounding exercises in the morning</span>
                      </li>
                      <li className="flex items-start gap-2">
                        <div className="w-1.5 h-1.5 rounded-full bg-orange-400 mt-2" />
                        <span className="text-gray-600">Take short walking breaks every hour to maintain energy flow</span>
                      </li>
                    </ul>
                  </CardContent>
                </Card>
              </motion.div>
            )}
          </motion.div>
        )}

        {/* Empty State */}
        {!latestData && !loading && !showManualInput && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="text-center py-12"
          >
            <Watch className="w-16 h-16 text-gray-300 mx-auto mb-4" />
            <p className="text-gray-500 mb-4">No wearable data yet</p>
            <Button onClick={() => setShowManualInput(true)}>
              <Plus className="w-4 h-4 mr-2" />
              Add Your First Entry
            </Button>
          </motion.div>
        )}
      </div>
    </div>
  );
}
