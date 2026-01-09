import { useState, useEffect, useRef } from 'react';
import { motion } from 'motion/react';
import { ChevronLeft, CheckCircle2, Clock, Volume2, VolumeX, Moon, Youtube, AlertCircle } from 'lucide-react';
import { Button } from '../ui/button';
import { Card, CardContent } from '../ui/card';
import MusicManager from '../../services/MusicManager';
import VoiceGuidanceService from '../../services/VoiceGuidanceService';
import api from '../../services/api';
import { useToast } from '../../hooks/use-toast';

interface SleepPracticeProps {
  recommendation: {
    id?: string;
    title: string;
    content: string;
    category?: string;
  };
  onComplete: () => void;
  onClose: () => void;
}

export function SleepPractice({ recommendation, onComplete, onClose }: SleepPracticeProps) {
  const { toast } = useToast();
  const [hasStarted, setHasStarted] = useState(false);
  const [isCompleting, setIsCompleting] = useState(false);
  const [isMusicEnabled, setIsMusicEnabled] = useState(true);
  const [totalElapsed, setTotalElapsed] = useState(0);
  const [videoId, setVideoId] = useState<string | null>(null);
  const [isLoadingVideo, setIsLoadingVideo] = useState(true);
  const [videoError, setVideoError] = useState(false);

  const musicManager = useRef<MusicManager | null>(null);
  const voiceService = useRef<VoiceGuidanceService | null>(null);
  const elapsedTimerRef = useRef<NodeJS.Timeout | null>(null);
  const startTimeRef = useRef<Date | null>(null);

  useEffect(() => {
    musicManager.current = new MusicManager();
    voiceService.current = new VoiceGuidanceService();

    // Fetch YouTube video
    const fetchVideo = async () => {
      try {
        const searchQuery = `${recommendation.title} sleep how to improve`;
        const response = await fetch(
          `https://www.googleapis.com/youtube/v3/search?part=snippet&maxResults=1&q=${encodeURIComponent(searchQuery)}&type=video&key=${import.meta.env.VITE_YOUTUBE_API_KEY}`
        );
        const data = await response.json();
        if (data.items && data.items.length > 0) {
          setVideoId(data.items[0].id.videoId);
          setVideoError(false);
          console.log('✅ YouTube video loaded:', data.items[0].snippet.title);
        } else {
          setVideoError(true);
          console.warn('⚠️ No YouTube video found for:', searchQuery);
        }
      } catch (error) {
        console.error('❌ Failed to fetch YouTube video:', error);
        setVideoError(true);
      } finally {
        setIsLoadingVideo(false);
      }
    };

    fetchVideo();
    
    return () => {
      cleanup();
    };
  }, [recommendation.title]);

  const cleanup = () => {
    if (elapsedTimerRef.current) clearInterval(elapsedTimerRef.current);
    if (musicManager.current) musicManager.current.stop();
    if (voiceService.current) voiceService.current.stop();
  };

  const startPractice = async () => {
    setHasStarted(true);
    startTimeRef.current = new Date();
    
    // Start music
    try {
      await musicManager.current?.init('sleep');
      await musicManager.current?.play();
      setIsMusicEnabled(true);
      console.log('🎵 Started sleep music');
    } catch (error) {
      console.warn('Music failed, continuing without');
      setIsMusicEnabled(false);
    }

    // Start elapsed timer
    elapsedTimerRef.current = setInterval(() => {
      if (startTimeRef.current) {
        const elapsed = Math.floor((Date.now() - startTimeRef.current.getTime()) / 1000);
        setTotalElapsed(elapsed);
      }
    }, 1000);

    // Speak introduction
    await voiceService.current?.speak(
      `Let's review sleep guidance for ${recommendation.title}. Good sleep is essential for wellness.`
    );
  };

  const markComplete = async () => {
    setIsCompleting(true);
    cleanup();

    try {
      const durationMinutes = Math.ceil(totalElapsed / 60);
      const payload = {
        practice_type: 'sleep',
        practice_name: recommendation.title,
        duration_minutes: Math.max(durationMinutes, 1),
        recommendation_id: recommendation.id || undefined,
        completion_status: 'completed'
      };

      console.log('📌 Practice logging payload:', JSON.stringify(payload, null, 2));
      
      const response = await api.createPracticeSession(payload);

      console.log('✅ Practice Stored - Backend response:', response);
      console.log('✅ Completion Summary Updated');
      
      toast({
        title: "Guidance Reviewed!",
        description: `${recommendation.title} has been acknowledged successfully.`,
        duration: 3000,
      });

      setTimeout(() => {
        onComplete();
      }, 1500);
    } catch (error: any) {
      console.error('❌ Failed to log practice:', error);
      console.error('❌ Error response:', error.response?.data);
      console.error('❌ Error status:', error.response?.status);
      console.error('❌ Error details:', error.message);
      
      toast({
        title: "Logging Failed",
        description: "Practice completed but couldn't save. Please try again.",
        variant: "destructive",
        duration: 4000,
      });
      
      // Still complete the flow
      setTimeout(() => {
        onComplete();
      }, 1500);
    }
  };

  const toggleMusic = () => {
    const newState = !isMusicEnabled;
    setIsMusicEnabled(newState);
    
    if (newState && hasStarted) {
      musicManager.current?.init('sleep').then(() => {
        musicManager.current?.play();
      });
    } else {
      musicManager.current?.stop();
    }
  };

  const formatTime = (seconds: number): string => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  if (isCompleting) {
    return (
      <div className="fixed inset-0 bg-gradient-to-br from-indigo-50 to-purple-100 flex items-center justify-center z-50">
        <motion.div
          initial={{ scale: 0.8, opacity: 0 }}
          animate={{ scale: 1, opacity: 1 }}
          className="text-center"
        >
          <motion.div
            animate={{ rotate: 360 }}
            transition={{ duration: 1, repeat: Infinity, ease: "linear" }}
            className="inline-block mb-4"
          >
            <CheckCircle2 className="w-24 h-24 text-indigo-600" />
          </motion.div>
          <h2 className="text-3xl font-bold text-gray-800">Guidance Reviewed!</h2>
          <p className="text-gray-600 mt-2">Redirecting...</p>
        </motion.div>
      </div>
    );
  }

  return (
    <div className="fixed inset-0 bg-gradient-to-br from-indigo-50 via-blue-50 to-purple-50 z-40 overflow-hidden">
      <div className="h-full overflow-y-auto">
        <div className="container mx-auto px-4 py-6 max-w-4xl min-h-full">
        <div className="flex justify-between items-center mb-6">
          <Button variant="ghost" onClick={onClose} size="sm">
            <ChevronLeft className="w-5 h-5 mr-1" />
            Back
          </Button>
          {hasStarted && (
            <div className="flex items-center gap-2">
              <Button variant="ghost" size="sm" onClick={toggleMusic}>
                {isMusicEnabled ? <Volume2 className="w-5 h-5" /> : <VolumeX className="w-5 h-5" />}
              </Button>
              <div className="flex items-center gap-1 text-gray-600">
                <Clock className="w-4 h-4" />
                <span>{formatTime(totalElapsed)}</span>
              </div>
            </div>
          )}
        </div>

        <div className="text-center mb-6">
          <h1 className="text-3xl font-bold text-gray-800 mb-2">🌙 {recommendation.title}</h1>
          <p className="text-gray-600">Sleep Guidance</p>
        </div>

        {/* YouTube Video Section */}
        {!hasStarted && (
          <Card className="mb-6">
            <CardContent className="pt-6">
              <div className="space-y-4">
                <div className="flex items-center justify-center gap-3 mb-4">
                  <div className="inline-flex items-center justify-center w-12 h-12 rounded-full bg-red-50">
                    <Youtube className="w-6 h-6 text-red-600" />
                  </div>
                  <h3 className="text-lg font-semibold text-gray-900">Tutorial Video</h3>
                </div>

                {isLoadingVideo && (
                  <div className="flex items-center justify-center py-8">
                    <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-red-600"></div>
                    <p className="ml-3 text-gray-600">Loading tutorial...</p>
                  </div>
                )}

                {!isLoadingVideo && videoId && (
                  <div className="relative w-full aspect-video min-h-[360px] bg-black rounded-lg">
                    <iframe
                      className="absolute top-0 left-0 w-full h-full rounded-lg shadow-lg"
                      src={`https://www.youtube.com/embed/${videoId}`}
                      title="Sleep Tutorial"
                      allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
                      allowFullScreen
                    ></iframe>
                  </div>
                )}

                {!isLoadingVideo && videoError && (
                  <div className="bg-amber-50 border border-amber-200 rounded-lg p-6">
                    <div className="flex items-center gap-2 text-amber-800 mb-2">
                      <AlertCircle className="w-5 h-5" />
                      <h4 className="font-semibold">Video Not Available</h4>
                    </div>
                    <p className="text-amber-700 text-sm">Showing text guidance instead.</p>
                  </div>
                )}
              </div>
            </CardContent>
          </Card>
        )}

        {/* Guidance Content */}
        <Card>
          <CardContent className="p-8">
            {!hasStarted ? (
              <div className="text-center space-y-6">
                <div className="text-6xl">🌙</div>
                <div className="prose prose-sm max-w-none">
                  <p className="text-gray-700 whitespace-pre-line">{recommendation.content}</p>
                </div>
                <Button onClick={startPractice} size="lg" className="mt-6">
                  View Guidance
                </Button>
              </div>
            ) : (
              <div className="space-y-6">
                <div className="prose prose-lg max-w-none">
                  <p className="text-gray-700 whitespace-pre-line leading-relaxed">{recommendation.content}</p>
                </div>
                <div className="text-center pt-8">
                  <Button onClick={markComplete} size="lg" className="px-8">
                    Mark as Complete
                  </Button>
                </div>
              </div>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  </div>
  );
}
