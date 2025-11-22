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
  Check
} from 'lucide-react';
import { Navigation } from './Navigation';
import { Button } from './ui/button';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from './ui/card';
import { Input } from './ui/input';
import { Label } from './ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from './ui/select';
import { Alert, AlertDescription } from './ui/alert';
import { toast } from 'sonner';
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
  const [loading, setLoading] = useState(false);
  const [syncing, setSyncing] = useState(false);
  const [showManualInput, setShowManualInput] = useState(false);
  
  // Manual input fields
  const [heartRate, setHeartRate] = useState('');
  const [hrv, setHrv] = useState('');
  const [sleepHours, setSleepHours] = useState('');
  const [sleepQuality, setSleepQuality] = useState<string>('good');
  const [steps, setSteps] = useState('');
  const [stressLevel, setStressLevel] = useState<string>('low');
  const [activeCalories, setActiveCalories] = useState('');
  
  // Ayurveda recommendations
  const [recommendations, setRecommendations] = useState<any>(null);
  const [generatingRecs, setGeneratingRecs] = useState(false);

  useEffect(() => {
    fetchLatestData();
  }, []);

  const fetchLatestData = async () => {
    if (!api.isAuthenticated()) return;
    
    try {
      setLoading(true);
      const data = await api.getLatestWearable();
      setLatestData(data);
    } catch (error) {
      console.error('Failed to fetch wearable data:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleManualSubmit = async () => {
    if (!heartRate || !sleepHours || !steps) {
      toast.error('Please fill in required fields');
      return;
    }

    try {
      setSyncing(true);
      
      const wearableData: SyncWearableRequest = {
        device_type: 'manual',
        heart_rate: parseInt(heartRate),
        hrv: hrv ? parseFloat(hrv) : undefined,
        sleep_hours: parseFloat(sleepHours),
        sleep_quality: sleepQuality,
        steps: parseInt(steps),
        stress_level: stressLevel,
        active_calories: activeCalories ? parseInt(activeCalories) : undefined,
        recorded_at: new Date().toISOString()
      };

      await api.syncWearableData(wearableData);
      
      toast.success('Wearable data synced successfully!');
      setShowManualInput(false);
      
      // Clear form
      setHeartRate('');
      setHrv('');
      setSleepHours('');
      setSteps('');
      setActiveCalories('');
      
      // Refresh latest data
      await fetchLatestData();
      
    } catch (error) {
      console.error('Failed to sync data:', error);
      toast.error('Failed to sync wearable data');
    } finally {
      setSyncing(false);
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
                  <Alert>
                    <AlertCircle className="h-4 w-4" />
                    <AlertDescription>
                      Apple Watch integration requires iOS app. Use manual input for now.
                    </AlertDescription>
                  </Alert>
                  <Button 
                    onClick={handleAppleWatchSync}
                    className="w-full"
                    variant="outline"
                    disabled
                  >
                    <Watch className="w-4 h-4 mr-2" />
                    Connect Apple Watch
                  </Button>
                </div>
              </CardContent>
            </Card>
          </motion.div>

          {/* Manual Input */}
          <motion.div
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
          >
            <Card className="h-full">
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Plus className="w-5 h-5 text-gray-700" />
                  Manual Input
                </CardTitle>
                <CardDescription>Enter your health metrics manually</CardDescription>
              </CardHeader>
              <CardContent>
                <Button 
                  onClick={() => setShowManualInput(!showManualInput)}
                  className="w-full"
                  variant={showManualInput ? "outline" : "default"}
                >
                  <Plus className="w-4 h-4 mr-2" />
                  {showManualInput ? 'Cancel' : 'Add Manual Entry'}
                </Button>
              </CardContent>
            </Card>
          </motion.div>
        </div>

        {/* Manual Input Form */}
        {showManualInput && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="mb-8"
          >
            <Card>
              <CardHeader>
                <CardTitle>Enter Health Metrics</CardTitle>
                <CardDescription>Fill in your current health data</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="grid md:grid-cols-2 gap-6">
                  <div className="space-y-2">
                    <Label htmlFor="heartRate">Heart Rate (bpm) *</Label>
                    <div className="relative">
                      <Heart className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
                      <Input
                        id="heartRate"
                        type="number"
                        placeholder="e.g., 72"
                        value={heartRate}
                        onChange={(e) => setHeartRate(e.target.value)}
                        className="pl-10"
                      />
                    </div>
                  </div>

                  <div className="space-y-2">
                    <Label htmlFor="hrv">HRV (ms)</Label>
                    <div className="relative">
                      <Activity className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
                      <Input
                        id="hrv"
                        type="number"
                        step="0.1"
                        placeholder="e.g., 50.5"
                        value={hrv}
                        onChange={(e) => setHrv(e.target.value)}
                        className="pl-10"
                      />
                    </div>
                  </div>

                  <div className="space-y-2">
                    <Label htmlFor="sleepHours">Sleep Hours *</Label>
                    <div className="relative">
                      <Bed className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
                      <Input
                        id="sleepHours"
                        type="number"
                        step="0.5"
                        placeholder="e.g., 7.5"
                        value={sleepHours}
                        onChange={(e) => setSleepHours(e.target.value)}
                        className="pl-10"
                      />
                    </div>
                  </div>

                  <div className="space-y-2">
                    <Label htmlFor="sleepQuality">Sleep Quality</Label>
                    <Select value={sleepQuality} onValueChange={setSleepQuality}>
                      <SelectTrigger>
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="excellent">Excellent</SelectItem>
                        <SelectItem value="good">Good</SelectItem>
                        <SelectItem value="fair">Fair</SelectItem>
                        <SelectItem value="poor">Poor</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>

                  <div className="space-y-2">
                    <Label htmlFor="steps">Steps *</Label>
                    <div className="relative">
                      <Footprints className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
                      <Input
                        id="steps"
                        type="number"
                        placeholder="e.g., 8000"
                        value={steps}
                        onChange={(e) => setSteps(e.target.value)}
                        className="pl-10"
                      />
                    </div>
                  </div>

                  <div className="space-y-2">
                    <Label htmlFor="stressLevel">Stress Level</Label>
                    <Select value={stressLevel} onValueChange={setStressLevel}>
                      <SelectTrigger>
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="low">Low</SelectItem>
                        <SelectItem value="moderate">Moderate</SelectItem>
                        <SelectItem value="high">High</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>

                  <div className="space-y-2 md:col-span-2">
                    <Label htmlFor="activeCalories">Active Calories</Label>
                    <div className="relative">
                      <TrendingUp className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
                      <Input
                        id="activeCalories"
                        type="number"
                        placeholder="e.g., 450"
                        value={activeCalories}
                        onChange={(e) => setActiveCalories(e.target.value)}
                        className="pl-10"
                      />
                    </div>
                  </div>
                </div>

                <div className="flex gap-4 mt-6">
                  <Button
                    onClick={handleManualSubmit}
                    disabled={syncing || !heartRate || !sleepHours || !steps}
                    className="flex-1"
                  >
                    {syncing ? (
                      <>
                        <RefreshCw className="w-4 h-4 mr-2 animate-spin" />
                        Syncing...
                      </>
                    ) : (
                      <>
                        <Check className="w-4 h-4 mr-2" />
                        Submit Data
                      </>
                    )}
                  </Button>
                  <Button variant="outline" onClick={() => setShowManualInput(false)}>
                    Cancel
                  </Button>
                </div>
              </CardContent>
            </Card>
          </motion.div>
        )}

        {/* Latest Data Display */}
        {latestData && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="mb-8"
          >
            <Card>
              <CardHeader>
                <div className="flex items-center justify-between">
                  <div>
                    <CardTitle>Latest Health Metrics</CardTitle>
                    <CardDescription>
                      Recorded: {new Date(latestData.recorded_at).toLocaleString()}
                    </CardDescription>
                  </div>
                  <Button variant="outline" size="sm" onClick={fetchLatestData}>
                    <RefreshCw className="w-4 h-4 mr-2" />
                    Refresh
                  </Button>
                </div>
              </CardHeader>
              <CardContent>
                <div className="grid md:grid-cols-3 gap-4">
                  <div className="bg-red-50 p-4 rounded-lg">
                    <div className="flex items-center gap-2 mb-2">
                      <Heart className="w-5 h-5 text-red-600" />
                      <span className="font-semibold text-gray-700">Heart Rate</span>
                    </div>
                    <p className="text-2xl font-bold text-red-600">{latestData.heart_rate} bpm</p>
                    {latestData.hrv && (
                      <p className="text-sm text-gray-600 mt-1">HRV: {latestData.hrv} ms</p>
                    )}
                  </div>

                  <div className="bg-blue-50 p-4 rounded-lg">
                    <div className="flex items-center gap-2 mb-2">
                      <Bed className="w-5 h-5 text-blue-600" />
                      <span className="font-semibold text-gray-700">Sleep</span>
                    </div>
                    <p className="text-2xl font-bold text-blue-600">{latestData.sleep_hours}h</p>
                    {typeof latestData.sleep_quality === 'string' && latestData.sleep_quality && (
                      <p className={`text-sm font-medium mt-1 px-2 py-1 rounded inline-block ${getSleepColor(latestData.sleep_quality)}`}>
                        {latestData.sleep_quality}
                      </p>
                    )}
                  </div>

                  <div className="bg-green-50 p-4 rounded-lg">
                    <div className="flex items-center gap-2 mb-2">
                      <Footprints className="w-5 h-5 text-green-600" />
                      <span className="font-semibold text-gray-700">Steps</span>
                    </div>
                    <p className="text-2xl font-bold text-green-600">{latestData.steps?.toLocaleString() || 0}</p>
                    {latestData.active_calories && (
                      <p className="text-sm text-gray-600 mt-1">{latestData.active_calories} cal</p>
                    )}
                  </div>

                  <div className={`p-4 rounded-lg ${typeof latestData.stress_level === 'string' && latestData.stress_level ? getStressColor(latestData.stress_level) : 'bg-gray-50'}`}>
                    <div className="flex items-center gap-2 mb-2">
                      <Brain className="w-5 h-5" />
                      <span className="font-semibold">Stress Level</span>
                    </div>
                    <p className="text-2xl font-bold capitalize">{latestData.stress_level || 'Unknown'}</p>
                  </div>
                </div>

                <div className="mt-6">
                  <Button 
                    onClick={generateAyurvedaRecommendations}
                    disabled={generatingRecs}
                    className="w-full"
                  >
                    {generatingRecs ? (
                      <>
                        <RefreshCw className="w-4 h-4 mr-2 animate-spin" />
                        Generating...
                      </>
                    ) : (
                      <>
                        <Sparkles className="w-4 h-4 mr-2" />
                        Get Ayurveda & Yoga Recommendations
                      </>
                    )}
                  </Button>
                </div>
              </CardContent>
            </Card>
          </motion.div>
        )}

        {/* Ayurveda Recommendations */}
        {recommendations && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
          >
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Sparkles className="w-5 h-5 text-purple-600" />
                  Personalized Recommendations
                </CardTitle>
                <CardDescription>Based on your wearable data and Ayurvedic profile</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {recommendations.wearable_insights?.map((insight: any, index: number) => (
                    <div key={index} className="border-l-4 border-purple-500 pl-4 py-2">
                      <h4 className="font-semibold text-gray-800 mb-1">{insight.category}</h4>
                      <p className="text-sm text-gray-600 mb-2">{insight.issue}</p>
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
