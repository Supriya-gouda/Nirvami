import { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'motion/react';
import { 
  User,
  Calendar,
  Clock,
  MessageCircle,
  Activity,
  Sparkles,
  RefreshCw,
  Star,
  ChevronRight,
  Heart,
  Zap,
  Play
} from 'lucide-react';
import { Navigation } from './Navigation';
import { Button } from './ui/button';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { Badge } from './ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from './ui/tabs';
import type { PageType } from '../App';
import type { User as UserType } from '../types/api.types';
import type { Recommendation, RecommendationsBySource } from '../types/api.types';
import api from '../services/api';

interface YogaRecommendationPageProps {
  user: UserType | null;
  onNavigate: (page: PageType) => void;
  onLogout?: () => void;
  onOpenNotifications?: () => void;
  onOpenPractice?: (recommendation: {
    id?: string;
    title: string;
    content: string;
    category?: string;
    source?: string;
  }) => void;
}

export function YogaRecommendationPage({
  user,
  onNavigate,
  onLogout,
  onOpenNotifications,
  onOpenPractice
}: YogaRecommendationPageProps) {
  const [yogaRecommendations, setYogaRecommendations] = useState<Recommendation[]>([]);
  const [recommendationsBySource, setRecommendationsBySource] = useState<RecommendationsBySource>({
    chat: [],
    device: [],
    system: []
  });
  const [loading, setLoading] = useState(true);
  const [selectedDate, setSelectedDate] = useState<string>(new Date().toISOString().split('T')[0]);
  const [viewMode, setViewMode] = useState<'all' | 'by-source'>('all');

  // Load recommendations on mount and when date changes
  useEffect(() => {
    loadRecommendations();
  }, [selectedDate]);
  
  // Auto-refresh to current day when component mounts or becomes visible
  useEffect(() => {
    const today = new Date().toISOString().split('T')[0];
    if (selectedDate !== today) {
      console.log('📅 Updating to today\'s date:', today);
      setSelectedDate(today);
    }
    
    // Set up interval to check if date changed (for overnight usage)
    const checkDateInterval = setInterval(() => {
      const currentToday = new Date().toISOString().split('T')[0];
      if (selectedDate !== currentToday) {
        console.log('📅 Date changed, refreshing to:', currentToday);
        setSelectedDate(currentToday);
      }
    }, 60000); // Check every minute
    
    return () => clearInterval(checkDateInterval);
  }, []);

  const loadRecommendations = async () => {
    setLoading(true);
    try {
      console.log('🧘 Loading yoga recommendations for date:', selectedDate);
      
      // Load yoga-specific recommendations
      const yogaRecs = await api.getYogaRecommendations(selectedDate);
      
      // Deduplicate recommendations by content and title
      const deduplicatedYoga = deduplicateRecommendations(yogaRecs);
      setYogaRecommendations(deduplicatedYoga);
      console.log('🧘 Loaded', deduplicatedYoga.length, 'unique yoga recommendations');

      // Load recommendations grouped by source for better display
      try {
        const groupedRecs = await api.getRecommendationsGroupedBySource('yoga', selectedDate);
        
        // Deduplicate within each source group
        const deduplicatedGrouped = {
          chat: deduplicateRecommendations(groupedRecs.chat || []),
          device: deduplicateRecommendations(groupedRecs.device || []),
          system: deduplicateRecommendations(groupedRecs.system || [])
        };
        setRecommendationsBySource(deduplicatedGrouped);
        console.log('🧘 Grouped by source - Chat:', deduplicatedGrouped.chat.length, 'Device:', deduplicatedGrouped.device.length);
      } catch (groupError) {
        console.warn('⚠️ Grouped source loading failed, using individual recommendations:', groupError);
        // Fallback: group the individual recommendations by source
        const grouped = groupRecommendationsBySource(deduplicatedYoga);
        setRecommendationsBySource(grouped);
      }

    } catch (error) {
      console.error('❌ Error loading yoga recommendations:', error);
      // Set empty arrays on error
      setYogaRecommendations([]);
      setRecommendationsBySource({ chat: [], device: [], system: [] });
    } finally {
      setLoading(false);
    }
  };

  const handleRefresh = () => {
    loadRecommendations();
  };
  
  // Deduplicate recommendations by content similarity and title
  const deduplicateRecommendations = (recommendations: Recommendation[]) => {
    const seen = new Set();
    return recommendations.filter(rec => {
      // Create a key based on title and content (normalized)
      const normalizedTitle = rec.title.toLowerCase().trim();
      const normalizedContent = rec.content.toLowerCase().trim().substring(0, 100);
      const key = `${normalizedTitle}|${normalizedContent}`;
      
      if (seen.has(key)) {
        console.log('🔄 Skipping duplicate:', rec.title);
        return false;
      }
      seen.add(key);
      return true;
    });
  };
  
  // Group recommendations by source (fallback when API grouping fails)
  const groupRecommendationsBySource = (recommendations: Recommendation[]) => {
    const grouped = { chat: [], device: [], system: [] } as RecommendationsBySource;
    recommendations.forEach(rec => {
      const source = rec.source as keyof RecommendationsBySource;
      if (grouped[source]) {
        grouped[source].push(rec);
      }
    });
    return grouped;
  };

  const formatDate = (dateStr: string) => {
    const date = new Date(dateStr);
    const today = new Date();
    const isToday = date.toDateString() === today.toDateString();
    
    if (isToday) {
      return `Today, ${date.toLocaleDateString('en-US', { month: 'long', day: 'numeric', year: 'numeric' })}`;
    }
    
    return date.toLocaleDateString('en-US', {
      weekday: 'long',
      year: 'numeric',
      month: 'long',
      day: 'numeric'
    });
  };

  // Ensure we're showing current day by default
  const isToday = selectedDate === new Date().toISOString().split('T')[0];
  
  // Get source display info with proper icons and colors
  const getSourceIcon = (source: string) => {
    switch (source) {
      case 'chat':
        return <MessageCircle className="w-4 h-4 text-blue-500" />;
      case 'device':
        return <Activity className="w-4 h-4 text-green-500" />;
      case 'system':
        return <Sparkles className="w-4 h-4 text-purple-500" />;
      default:
        return <Star className="w-4 h-4 text-gray-500" />;
    }
  };
  
  const getSourceLabel = (source: string) => {
    switch (source) {
      case 'chat':
        return 'From AI Chat';
      case 'device':
        return 'From Wearable Device';
      case 'system':
        return 'System Generated';
      default:
        return source;
    }
  };

  const getSourceColor = (source: string) => {
    switch (source) {
      case 'chat':
        return 'bg-blue-50 text-blue-700 border-blue-200';
      case 'device':
        return 'bg-green-50 text-green-700 border-green-200';
      case 'system':
        return 'bg-purple-50 text-purple-700 border-purple-200';
      default:
        return 'bg-gray-50 text-gray-700 border-gray-200';
    }
  };

  const RecommendationCard = ({ recommendation }: { recommendation: Recommendation }) => (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
    >
      <Card className="hover:shadow-md transition-shadow duration-200 border-l-4 border-l-orange-400">
        <CardHeader className="pb-2">
          <div className="flex items-start justify-between">
            <div className="flex items-center gap-2">
              {getSourceIcon(recommendation.source)}
              <CardTitle className="text-lg font-semibold text-gray-900">
                {recommendation.title}
              </CardTitle>
            </div>
            <Badge className={`text-xs ${getSourceColor(recommendation.source)}`}>
              {recommendation.source}
            </Badge>
          </div>
          <div className="flex items-center gap-1 text-xs text-gray-500">
            <Clock className="w-3 h-3" />
            {new Date(recommendation.created_at).toLocaleTimeString('en-US', { 
              hour: '2-digit', 
              minute: '2-digit' 
            })}
          </div>
        </CardHeader>
        <CardContent>
          <p className="text-gray-700 leading-relaxed whitespace-pre-line mb-4">
            {recommendation.content}
          </p>
          {onOpenPractice && (
            <Button
              variant="outline"
              size="sm"
              onClick={() => onOpenPractice({
                id: recommendation.id,
                title: recommendation.title,
                content: recommendation.content,
                category: 'yoga',
                source: recommendation.source
              })}
              className="w-full bg-gradient-to-r from-orange-500 to-amber-500 text-white hover:from-orange-600 hover:to-amber-600 border-0"
            >
              <Play className="w-4 h-4 mr-2" />
              Start Practice
            </Button>
          )}
        </CardContent>
      </Card>
    </motion.div>
  );

  return (
    <div className="min-h-screen bg-gradient-to-br from-orange-50 via-white to-amber-50">
      <Navigation
        user={user}
        onNavigate={onNavigate}
        onLogout={onLogout}
        onOpenNotifications={onOpenNotifications}
      />

      <main className="max-w-4xl mx-auto px-4 py-8">
        {/* Header */}
        <div className="mb-8">
          <motion.div
            initial={{ opacity: 0, y: -20 }}
            animate={{ opacity: 1, y: 0 }}
            className="text-center"
          >
            <div className="flex items-center justify-center gap-2 mb-4">
              <div className="w-12 h-12 rounded-full bg-gradient-to-br from-orange-400 to-amber-500 flex items-center justify-center">
                <User className="w-6 h-6 text-white" />
              </div>
            </div>
            <h1 className="text-3xl font-bold text-gray-900 mb-2">
              Yoga Recommendations
            </h1>
            <p className="text-gray-600 max-w-2xl mx-auto">
              Personalized yoga practices and poses based on your conversations with the AI assistant and your device health data.
            </p>
            
            {/* Today's Summary */}
            {isToday && !loading && (yogaRecommendations.length > 0 || Object.keys(recommendationsBySource).some(key => recommendationsBySource[key as keyof typeof recommendationsBySource].length > 0)) && (
              <div className="mt-4 p-4 bg-orange-50 rounded-lg border border-orange-200 max-w-2xl mx-auto">
                <div className="flex items-center justify-center gap-4 text-sm">
                  <div className="flex items-center gap-1">
                    <MessageCircle className="w-4 h-4 text-blue-500" />
                    <span className="font-medium">{recommendationsBySource.chat?.length || 0}</span>
                    <span className="text-gray-600">from chat</span>
                  </div>
                  <div className="flex items-center gap-1">
                    <Activity className="w-4 h-4 text-green-500" />
                    <span className="font-medium">{recommendationsBySource.device?.length || 0}</span>
                    <span className="text-gray-600">from device</span>
                  </div>
                  <div className="text-gray-600">
                    • Total: <span className="font-medium text-gray-900">{yogaRecommendations.length}</span> today
                  </div>
                </div>
                <p className="text-xs text-gray-500 mt-2 text-center">
                  💾 These recommendations persist and remain available even after closing the chat
                </p>
              </div>
            )}
          </motion.div>
        </div>

        {/* Date Selector and Controls */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="mb-6 flex flex-col sm:flex-row items-center justify-between gap-4"
        >
          <div className="flex items-center gap-3">
            <Calendar className="w-5 h-5 text-gray-600" />
            <input
              type="date"
              value={selectedDate}
              onChange={(e) => setSelectedDate(e.target.value)}
              className="px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-orange-500 focus:border-orange-500"
            />
            {isToday && (
              <Badge variant="secondary" className="bg-orange-100 text-orange-800">
                Today
              </Badge>
            )}
          </div>

          <div className="flex items-center gap-2">
            <Button
              onClick={handleRefresh}
              disabled={loading}
              size="sm"
              variant="outline"
              className="flex items-center gap-2"
            >
              <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
              Refresh
            </Button>
          </div>
        </motion.div>

        {/* View Mode Tabs */}
        <Tabs value={viewMode} onValueChange={(value) => setViewMode(value as any)} className="mb-6">
          <TabsList className="grid w-full grid-cols-2">
            <TabsTrigger value="all">All Recommendations</TabsTrigger>
            <TabsTrigger value="by-source">By Source</TabsTrigger>
          </TabsList>

          <TabsContent value="all" className="mt-6">
            {loading ? (
              <div className="flex items-center justify-center py-12">
                <div className="animate-spin w-8 h-8 border-2 border-orange-500 border-t-transparent rounded-full"></div>
              </div>
            ) : yogaRecommendations.length > 0 ? (
              <div className="space-y-4">
                <div className="flex items-center gap-2 mb-4">
                  <Zap className="w-5 h-5 text-orange-500" />
                  <h2 className="text-xl font-semibold text-gray-900">
                    Yoga Practices for {formatDate(selectedDate)}
                  </h2>
                  <Badge variant="secondary">{yogaRecommendations.length} recommendations</Badge>
                </div>
                
                <AnimatePresence>
                  {yogaRecommendations.map((recommendation) => (
                    <RecommendationCard 
                      key={recommendation.id} 
                      recommendation={recommendation} 
                    />
                  ))}
                </AnimatePresence>
              </div>
            ) : (
              <motion.div
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                className="text-center py-12"
              >
                <div className="w-16 h-16 rounded-full bg-gray-100 flex items-center justify-center mx-auto mb-4">
                  <User className="w-8 h-8 text-gray-400" />
                </div>
                <h3 className="text-lg font-medium text-gray-900 mb-2">
                  No yoga recommendations yet
                </h3>
                <p className="text-gray-600 mb-4">
                  Chat with the AI assistant or log health data to receive personalized yoga recommendations.
                </p>
                <Button
                  onClick={() => onNavigate('chat')}
                  className="bg-orange-500 hover:bg-orange-600"
                >
                  Start Chat <ChevronRight className="w-4 h-4 ml-1" />
                </Button>
              </motion.div>
            )}
          </TabsContent>

          <TabsContent value="by-source" className="mt-6">
            {loading ? (
              <div className="flex items-center justify-center py-12">
                <div className="animate-spin w-8 h-8 border-2 border-orange-500 border-t-transparent rounded-full"></div>
              </div>
            ) : (
              <div className="space-y-8">
                {/* Chat Recommendations */}
                {recommendationsBySource.chat.length > 0 && (
                  <div>
                    <div className="flex items-center gap-2 mb-4">
                      <MessageCircle className="w-5 h-5 text-blue-600" />
                      <h3 className="text-lg font-semibold text-gray-900">From Chat with AI</h3>
                      <Badge className="bg-blue-100 text-blue-800">
                        {recommendationsBySource.chat.length}
                      </Badge>
                    </div>
                    <div className="space-y-4">
                      {recommendationsBySource.chat.map((rec) => (
                        <RecommendationCard key={rec.id} recommendation={rec} />
                      ))}
                    </div>
                  </div>
                )}

                {/* Device Recommendations */}
                {recommendationsBySource.device.length > 0 && (
                  <div>
                    <div className="flex items-center gap-2 mb-4">
                      <Activity className="w-5 h-5 text-green-600" />
                      <h3 className="text-lg font-semibold text-gray-900">From Device Analysis</h3>
                      <Badge className="bg-green-100 text-green-800">
                        {recommendationsBySource.device.length}
                      </Badge>
                    </div>
                    <div className="space-y-4">
                      {recommendationsBySource.device.map((rec) => (
                        <RecommendationCard key={rec.id} recommendation={rec} />
                      ))}
                    </div>
                  </div>
                )}

                {/* System Recommendations */}
                {recommendationsBySource.system.length > 0 && (
                  <div>
                    <div className="flex items-center gap-2 mb-4">
                      <Sparkles className="w-5 h-5 text-purple-600" />
                      <h3 className="text-lg font-semibold text-gray-900">System Generated</h3>
                      <Badge className="bg-purple-100 text-purple-800">
                        {recommendationsBySource.system.length}
                      </Badge>
                    </div>
                    <div className="space-y-4">
                      {recommendationsBySource.system.map((rec) => (
                        <RecommendationCard key={rec.id} recommendation={rec} />
                      ))}
                    </div>
                  </div>
                )}

                {/* No recommendations */}
                {recommendationsBySource.chat.length === 0 && 
                 recommendationsBySource.device.length === 0 && 
                 recommendationsBySource.system.length === 0 && (
                  <motion.div
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    className="text-center py-12"
                  >
                    <div className="w-16 h-16 rounded-full bg-gray-100 flex items-center justify-center mx-auto mb-4">
                      <Heart className="w-8 h-8 text-gray-400" />
                    </div>
                    <h3 className="text-lg font-medium text-gray-900 mb-2">
                      No recommendations available
                    </h3>
                    <p className="text-gray-600 mb-4">
                      Recommendations will appear here after you chat with the AI or log health data.
                    </p>
                    <div className="flex flex-col sm:flex-row gap-2 justify-center">
                      <Button
                        onClick={() => onNavigate('chat')}
                        className="bg-blue-500 hover:bg-blue-600"
                      >
                        <MessageCircle className="w-4 h-4 mr-2" />
                        Start Chat
                      </Button>
                      <Button
                        onClick={() => onNavigate('device')}
                        variant="outline"
                        className="border-green-500 text-green-600 hover:bg-green-50"
                      >
                        <Activity className="w-4 h-4 mr-2" />
                        Log Health Data
                      </Button>
                    </div>
                  </motion.div>
                )}
              </div>
            )}
          </TabsContent>
        </Tabs>
      </main>
    </div>
  );
}