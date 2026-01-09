import { useState, useEffect, useRef } from 'react';
import { motion } from 'motion/react';
import { ChevronLeft, Volume2, VolumeX, CheckCircle2, Clock } from 'lucide-react';
import { Button } from '../ui/button';
import { Card, CardContent } from '../ui/card';
import MusicManager from '../../services/MusicManager';
import VoiceGuidanceService from '../../services/VoiceGuidanceService';
import api from '../../services/api';
import { PracticeLearnSection } from './PracticeLearnSection';

interface MeditationPracticeProps {
  recommendation: {
    id?: string;
    title: string;
    content: string;
    category?: string;
  };
  onComplete: () => void;
  onClose: () => void;
}

type MeditationPhase = 'intro' | 'preparation' | 'meditation' | 'closing' | 'rest' | 'complete';

export function MeditationPractice({ recommendation, onComplete, onClose }: MeditationPracticeProps) {
  const [showLearnSection, setShowLearnSection] = useState(true);
  const [phase, setPhase] = useState<MeditationPhase>('intro');
  const [countdown, setCountdown] = useState(0);
  const [isMusicEnabled, setIsMusicEnabled] = useState(true);
  const [totalElapsed, setTotalElapsed] = useState(0);
  const [isCompleting, setIsCompleting] = useState(false);

  const meditationDurationMinutes = 5; // Default meditation duration
  const meditationDurationSeconds = meditationDurationMinutes * 60;

  const musicManager = useRef<MusicManager | null>(null);
  const voiceService = useRef<VoiceGuidanceService | null>(null);
  const phaseTimerRef = useRef<NodeJS.Timeout | null>(null);
  const elapsedTimerRef = useRef<NodeJS.Timeout | null>(null);
  const startTimeRef = useRef<Date | null>(null);

  useEffect(() => {
    // Initialize services
    musicManager.current = new MusicManager();
    voiceService.current = new VoiceGuidanceService();
    voiceService.current.setCallbacks(() => {}, () => {});

    return () => {
      cleanup();
    };
  }, []);

  const cleanup = () => {
    if (phaseTimerRef.current) clearInterval(phaseTimerRef.current);
    if (elapsedTimerRef.current) clearInterval(elapsedTimerRef.current);
    if (musicManager.current) musicManager.current.stop();
    if (voiceService.current) voiceService.current.stop();
  };

  const startPractice = async () => {
    startTimeRef.current = new Date();
    
    // Start music
    try {
      await musicManager.current?.init('meditation');
      await musicManager.current?.play();
      setIsMusicEnabled(true);
      console.log('🎵 Started meditation music');
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

    // Begin meditation sequence
    await executePreparation();
  };

  const executePreparation = async () => {
    setPhase('preparation');
    
    await voiceService.current?.speak(
      'Find a comfortable seated position. You may sit cross-legged on the floor or in a chair with your feet flat on the ground.'
    );
    
    // Wait 30 seconds for settling
    await waitWithCountdown(30);

    await voiceService.current?.speak(
      'Close your eyes gently. Take a few deep breaths, allowing your body to relax with each exhale.'
    );
    
    await waitWithCountdown(20);

    // Start meditation phase with music
    executeMediation();
  };

  const executeMediation = async () => {
    setPhase('meditation');

    // Start meditation music
    if (isMusicEnabled) {
      try {
        await musicManager.current?.init('meditation');
        await musicManager.current?.play();
      } catch (error) {
        console.warn('Music failed, continuing without');
      }
    }

    await voiceService.current?.speak(
      `Now, simply rest in stillness for the next ${meditationDurationMinutes} minutes. Let your thoughts come and go like clouds in the sky. If your mind wanders, gently bring your attention back to your breath.`
    );

    // Main meditation period
    await waitWithCountdown(meditationDurationSeconds);

    executeClosing();
  };

  const executeClosing = async () => {
    setPhase('closing');

    await voiceService.current?.speak(
      'Slowly begin to deepen your breath. Gently wiggle your fingers and toes. When you are ready, softly open your eyes.'
    );

    await waitWithCountdown(20);

    await voiceService.current?.speak(
      'Take a moment to notice how you feel. Carry this sense of peace with you throughout your day.'
    );

    await waitWithCountdown(15);

    executeRest();
  };

  const executeRest = async () => {
    setPhase('rest');

    await waitWithCountdown(10);

    completePractice();
  };

  const waitWithCountdown = (seconds: number): Promise<void> => {
    return new Promise((resolve) => {
      let remaining = seconds;
      setCountdown(remaining);

      phaseTimerRef.current = setInterval(() => {
        remaining--;
        setCountdown(remaining);

        if (remaining <= 0) {
          if (phaseTimerRef.current) clearInterval(phaseTimerRef.current);
          resolve();
        }
      }, 1000);
    });
  };

  const completePractice = async () => {
    setPhase('complete');
    setIsCompleting(true);
    
    cleanup();

    try {
      const durationMinutes = Math.ceil(totalElapsed / 60);
      const payload = {
        practice_type: 'meditation',
        practice_name: recommendation.title,
        duration_minutes: durationMinutes,
        recommendation_id: recommendation.id || undefined,
        completion_status: 'completed'
      };

      console.log('📌 Practice logging payload:', JSON.stringify(payload, null, 2));
      const response = await api.createPracticeSession(payload);
      console.log('✅ Practice Stored - Backend response:', response);
      console.log('✅ Meditation practice completed and logged');
      
      setTimeout(() => {
        onComplete();
      }, 2000);
    } catch (error: any) {
      console.error('❌ Failed to log practice');
      console.error('❌ Error response:', error.response?.data);
      console.error('❌ Error status:', error.response?.status);
      console.error('❌ Error details:', error.message);
      setTimeout(() => {
        onComplete();
      }, 2000);
    }
  };

  const toggleMusic = () => {
    const newState = !isMusicEnabled;
    setIsMusicEnabled(newState);
    
    if (newState && phase === 'meditation') {
      musicManager.current?.init('meditation').then(() => {
        musicManager.current?.play();
      });
    } else if (!newState) {
      musicManager.current?.stop();
    }
  };

  const formatTime = (seconds: number): string => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  const getPhaseDescription = (): string => {
    switch (phase) {
      case 'intro': return 'Prepare to begin';
      case 'preparation': return 'Getting comfortable';
      case 'meditation': return 'In meditation';
      case 'closing': return 'Gently returning';
      case 'rest': return 'Final rest';
      case 'complete': return 'Complete';
    }
  };

  if (isCompleting) {
    return (
      <div className="fixed inset-0 bg-gradient-to-br from-purple-50 to-indigo-100 flex items-center justify-center z-50">
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
            <CheckCircle2 className="w-24 h-24 text-purple-600" />
          </motion.div>
          <h2 className="text-3xl font-bold text-gray-800">Practice Complete!</h2>
          <p className="text-gray-600 mt-2">Redirecting...</p>
        </motion.div>
      </div>
    );
  }

  // Show Learn Section first
  if (showLearnSection) {
    return (
      <PracticeLearnSection
        category="meditation"
        onClose={onClose}
        onReady={() => setShowLearnSection(false)}
      />
    );
  }

  if (phase === 'intro') {
    return (
      <div className="fixed inset-0 bg-gradient-to-br from-purple-50 via-indigo-50 to-pink-50 overflow-auto z-40">
        <div className="container mx-auto px-4 py-6 max-w-4xl">
          <div className="flex justify-between items-center mb-6">
            <Button variant="ghost" onClick={onClose} size="sm">
              <ChevronLeft className="w-5 h-5 mr-1" />
              Back
            </Button>
            <Button variant="outline" onClick={() => setShowLearnSection(true)} size="sm">
              Back to Learn
            </Button>
          </div>

          <Card>
            <CardContent className="p-12 text-center">
              <div className="text-6xl mb-6">🧘‍♀️</div>
              <h1 className="text-3xl font-bold text-gray-800 mb-4">{recommendation.title}</h1>
              <p className="text-gray-600 mb-6 max-w-2xl mx-auto">
                This guided meditation will help you find inner peace and clarity.
                Duration: approximately {meditationDurationMinutes + 2} minutes.
              </p>
              <p className="text-gray-500 text-sm mb-8">
                Find a quiet space where you won't be disturbed.
              </p>
              <Button onClick={startPractice} size="lg" className="px-8">
                Begin Meditation
              </Button>
            </CardContent>
          </Card>
        </div>
      </div>
    );
  }

  return (
    <div className="fixed inset-0 bg-gradient-to-br from-purple-50 via-indigo-50 to-pink-50 z-40 overflow-hidden">
      <div className="h-full overflow-y-auto">
        <div className="container mx-auto px-4 py-6 max-w-4xl min-h-full">
        {/* Header */}
        <div className="flex justify-between items-center mb-6">
          <Button variant="ghost" onClick={onClose} size="sm" disabled={phase === 'meditation'}>
            <ChevronLeft className="w-5 h-5 mr-1" />
            Back
          </Button>
          <div className="flex items-center gap-2">
            <Button variant="ghost" size="sm" onClick={toggleMusic}>
              {isMusicEnabled ? <Volume2 className="w-5 h-5" /> : <VolumeX className="w-5 h-5" />}
            </Button>
            <div className="flex items-center gap-1 text-gray-600">
              <Clock className="w-4 h-4" />
              <span>{formatTime(totalElapsed)}</span>
            </div>
          </div>
        </div>

        {/* Practice Title */}
        <div className="text-center mb-8">
          <h1 className="text-3xl font-bold text-gray-800 mb-2">🧘 {recommendation.title}</h1>
          <p className="text-gray-600">{getPhaseDescription()}</p>
        </div>

        {/* Meditation Visual */}
        <div className="flex flex-col items-center justify-center min-h-[500px]">
          {/* Pulsing Circle - calming visual */}
          <motion.div
            className="rounded-full bg-gradient-to-br from-purple-400 to-pink-400 shadow-2xl mb-12"
            animate={{
              scale: [1, 1.1, 1],
              opacity: [0.6, 0.8, 0.6]
            }}
            transition={{
              duration: 4,
              repeat: Infinity,
              ease: "easeInOut"
            }}
            style={{ width: 200, height: 200 }}
          >
            <div className="w-full h-full flex items-center justify-center">
              <span className="text-5xl font-bold text-white">
                {countdown > 0 ? countdown : '∞'}
              </span>
            </div>
          </motion.div>

          {/* Phase Instructions */}
          <motion.div
            key={phase}
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            className="text-center max-w-2xl"
          >
            {phase === 'preparation' && (
              <p className="text-xl text-gray-700">
                Settle into a comfortable position...
              </p>
            )}
            {phase === 'meditation' && (
              <div className="space-y-4">
                <p className="text-2xl font-semibold text-gray-800">
                  Rest in stillness
                </p>
                <p className="text-gray-600">
                  Let thoughts pass like clouds in the sky
                </p>
              </div>
            )}
            {phase === 'closing' && (
              <p className="text-xl text-gray-700">
                Gently returning to awareness...
              </p>
            )}
            {phase === 'rest' && (
              <p className="text-xl text-gray-700">
                Take a moment to rest...
              </p>
            )}
          </motion.div>
        </div>

        {/* Subtle Progress Indicator */}
        {phase === 'meditation' && (
          <div className="mt-8 bg-white/40 rounded-lg p-4">
            <div className="h-1 bg-gray-200 rounded-full overflow-hidden">
              <motion.div
                className="h-full bg-gradient-to-r from-purple-500 to-pink-500"
                initial={{ width: '0%' }}
                animate={{ 
                  width: `${((meditationDurationSeconds - countdown) / meditationDurationSeconds) * 100}%` 
                }}
                transition={{ duration: 0.5 }}
              />
            </div>
          </div>
        )}
        </div>
      </div>
    </div>
  );
}
