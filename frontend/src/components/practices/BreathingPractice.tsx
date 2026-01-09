import { useState, useEffect, useRef } from 'react';
import { motion } from 'motion/react';
import { ChevronLeft, Volume2, VolumeX, CheckCircle2, Clock } from 'lucide-react';
import { Button } from '../ui/button';
import { Card, CardContent } from '../ui/card';
import MusicManager from '../../services/MusicManager';
import VoiceGuidanceService from '../../services/VoiceGuidanceService';
import api from '../../services/api';
import { PracticeLearnSection } from './PracticeLearnSection';

interface BreathingPracticeProps {
  recommendation: {
    id?: string;
    title: string;
    content: string;
    category?: string;
  };
  onComplete: () => void;
  onClose: () => void;
}

type BreathingPhase = 'preparation' | 'inhale' | 'hold' | 'exhale' | 'rest' | 'complete';

export function BreathingPractice({ recommendation, onComplete, onClose }: BreathingPracticeProps) {
  const [showLearnSection, setShowLearnSection] = useState(true);
  const [phase, setPhase] = useState<BreathingPhase>('preparation');
  const [cycle, setCycle] = useState(0);
  const [countdown, setCountdown] = useState(0);
  const [isMusicEnabled, setIsMusicEnabled] = useState(true);
  const [totalElapsed, setTotalElapsed] = useState(0);
  const [isCompleting, setIsCompleting] = useState(false);

  const totalCycles = 3; // Minimum 3 full cycles
  const inhaleSeconds = 4;
  const holdSeconds = 7;
  const exhaleSeconds = 8;

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
      await musicManager.current?.init('breathing');
      await musicManager.current?.play();
      setIsMusicEnabled(true);
      console.log('🎵 Started background music for breathing practice');
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

    // Begin practice
    await executePreparation();
  };

  const executePreparation = async () => {
    setPhase('preparation');
    
    // Universal preparation instruction
    await voiceService.current?.speak('Find a comfortable position. Take a moment to prepare yourself.');
    
    // Wait a few seconds
    let remaining = 10;
    setCountdown(remaining);
    
    phaseTimerRef.current = setInterval(() => {
      remaining--;
      setCountdown(remaining);
      
      if (remaining <= 0) {
        if (phaseTimerRef.current) clearInterval(phaseTimerRef.current);
        // Now provide breathing-specific instructions
        provideTechniqueInstructions();
      }
    }, 1000);
  };

  const provideTechniqueInstructions = async () => {
    // Detect breathing technique and provide specific instructions
    const title = recommendation.title.toLowerCase();
    let preparationInstructions = 'Sit comfortably in Sukhasana, or easy pose.';
    
    if (title.includes('shitali') || title.includes('sitali')) {
      preparationInstructions += ' For Shitali pranayama, roll your tongue inward to form a tube or pipe shape. You will inhale through this tongue tube and exhale through your nose.';
    } else if (title.includes('ujjayi')) {
      preparationInstructions += ' For Ujjayi breath, you will breathe through your nose with a slight constriction at the back of your throat, creating an ocean-like sound.';
    } else if (title.includes('bhramari')) {
      preparationInstructions += ' Place your thumbs on your ears, index fingers above your eyebrows, and remaining three fingers on your closed eyes. You will make a humming sound like a bee while exhaling.';
    } else if (title.includes('kapalbhati') || title.includes('kapalabhati')) {
      preparationInstructions += ' Sit with a straight spine. Place your hands on your knees in Gyan mudra. You will perform forceful exhalations with passive inhalations.';
    } else if (title.includes('anulom vilom') || title.includes('alternate nostril')) {
      preparationInstructions += ' Use your right hand in Vishnu mudra: fold your index and middle fingers. Use your thumb to close your right nostril and your ring finger to close your left nostril alternately.';
    } else if (title.includes('bhastrika') || title.includes('bellows')) {
      preparationInstructions += ' Sit with a straight spine, hands in Gyan mudra on your knees. You will perform rapid, forceful breathing through both nostrils.';
    } else {
      preparationInstructions += ' Place your hands in Gyan mudra: touch the tip of your index finger to the tip of your thumb, keeping other fingers straight.';
    }
    
    await voiceService.current?.speak(preparationInstructions);
    
    // Wait for instructions to finish, then start breathing
    let remaining = 25;
    setCountdown(remaining);
    
    phaseTimerRef.current = setInterval(() => {
      remaining--;
      setCountdown(remaining);
      
      if (remaining <= 0) {
        if (phaseTimerRef.current) clearInterval(phaseTimerRef.current);
        setCycle(1);
        executeBreathingCycle(1);
      }
    }, 1000);
  };

  const executeBreathingCycle = async (cycleNumber: number) => {
    console.log(`Starting breathing cycle ${cycleNumber}/${totalCycles}`);

    // Inhale phase
    await executePhase('inhale', inhaleSeconds, 'Breathe in slowly through your nose');

    // Hold phase
    await executePhase('hold', holdSeconds, 'Hold your breath gently');

    // Exhale phase
    await executePhase('exhale', exhaleSeconds, 'Exhale slowly through your mouth');

    // Rest phase (brief pause between cycles)
    await executePhase('rest', 3, 'Rest for a moment');

    // Check if more cycles needed
    if (cycleNumber < totalCycles) {
      setCycle(cycleNumber + 1);
      executeBreathingCycle(cycleNumber + 1);
    } else {
      // Final relaxation before completion
      await executePhase('rest', 10, 'Release and relax. Take a moment to notice how you feel.');
      completePractice();
    }
  };

  const executePhase = async (phaseName: BreathingPhase, duration: number, instruction: string): Promise<void> => {
    setPhase(phaseName);
    
    // Speak instruction first
    try {
      await voiceService.current?.speak(instruction);
    } catch (error) {
      console.warn('Voice guidance failed:', error);
    }

    // Then run countdown timer
    return new Promise((resolve) => {
      let remaining = duration;
      setCountdown(remaining);

      phaseTimerRef.current = setInterval(() => {
        remaining--;
        setCountdown(remaining);

        if (remaining <= 0) {
          if (phaseTimerRef.current) {
            clearInterval(phaseTimerRef.current);
            phaseTimerRef.current = null;
          }
          resolve();
        }
      }, 1000);
    });
  };

  const completePractice = async () => {
    setPhase('complete');
    setIsCompleting(true);
    
    await voiceService.current?.speak('Well done. Your breathing practice is complete. Take a moment to notice how you feel.');
    
    cleanup();

    try {
      const durationMinutes = Math.ceil(totalElapsed / 60);
      const payload = {
        practice_type: 'breathing',
        practice_name: recommendation.title,
        duration_minutes: durationMinutes,
        recommendation_id: recommendation.id || undefined,
        completion_status: 'completed'
      };

      console.log('📌 Practice logging payload:', JSON.stringify(payload, null, 2));
      const response = await api.createPracticeSession(payload);
      console.log('✅ Practice Stored - Backend response:', response);
      console.log('✅ Breathing practice completed and logged');
      
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
    
    if (newState && phase !== 'preparation') {
      musicManager.current?.init('breathing').then(() => {
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

  const getCircleSize = (): number => {
    if (phase === 'inhale') return 200; // Expand
    if (phase === 'exhale') return 80;  // Contract
    return 140; // Default/hold size
  };

  const getPhaseColor = (): string => {
    switch (phase) {
      case 'inhale': return '#10b981'; // green
      case 'hold': return '#f59e0b';   // amber
      case 'exhale': return '#3b82f6'; // blue
      case 'rest': return '#8b5cf6';   // purple
      default: return '#6b7280';       // gray
    }
  };

  const getPhaseInstruction = (): string => {
    switch (phase) {
      case 'preparation': return 'Get comfortable and prepare';
      case 'inhale': return 'Breathe in slowly';
      case 'hold': return 'Hold your breath';
      case 'exhale': return 'Breathe out slowly';
      case 'rest': return 'Rest and relax';
      case 'complete': return 'Practice complete!';
    }
  };

  if (isCompleting) {
    return (
      <div className="fixed inset-0 bg-gradient-to-br from-blue-50 to-cyan-100 flex items-center justify-center z-50">
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
            <CheckCircle2 className="w-24 h-24 text-blue-600" />
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
      <div className="fixed inset-0 bg-gradient-to-br from-blue-50 via-cyan-50 to-teal-50 z-40 overflow-hidden">
        <div className="h-full overflow-y-auto">
          <div className="container mx-auto px-4 py-6 max-w-4xl min-h-full">
            <div className="flex justify-between items-center mb-6">
              <Button variant="ghost" onClick={onClose} size="sm">
                <ChevronLeft className="w-5 h-5 mr-1" />
                Back
              </Button>
            </div>
            
            <PracticeLearnSection
              practiceName={recommendation.title}
              category="breathing"
              content={recommendation.content}
              onStartPractice={() => setShowLearnSection(false)}
            />
          </div>
        </div>
      </div>
    );
  }

  // Pre-practice screen after Learn
  if (phase === 'preparation' && countdown === 0) {
    return (
      <div className="fixed inset-0 bg-gradient-to-br from-blue-50 via-cyan-50 to-teal-50 z-40 overflow-hidden">
        <div className="h-full overflow-y-auto">
          <div className="container mx-auto px-4 py-6 max-w-4xl min-h-full">
            <div className="flex justify-between items-center mb-6">
              <Button variant="ghost" onClick={() => setShowLearnSection(true)} size="sm">
                <ChevronLeft className="w-5 h-5 mr-1" />
                Back to Learn
              </Button>
            </div>

            <Card>
              <CardContent className="p-12 text-center">
                <div className="text-6xl mb-6">🌬️</div>
                <h1 className="text-3xl font-bold text-gray-800 mb-4">{recommendation.title}</h1>
                <p className="text-gray-600 mb-8 max-w-2xl mx-auto">
                  This guided pranayama practice will take you through {totalCycles} breathing cycles.
                  Find a quiet space, sit comfortably, and follow the visual and voice guidance.
                </p>
                <Button onClick={startPractice} size="lg" className="px-8">
                  Begin Practice
                </Button>
              </CardContent>
            </Card>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="fixed inset-0 bg-gradient-to-br from-blue-50 via-cyan-50 to-teal-50 z-40 overflow-hidden">
      <div className="h-full overflow-y-auto">
        <div className="container mx-auto px-4 py-6 max-w-4xl min-h-full">
        {/* Header */}
        <div className="flex justify-between items-center mb-6">
          <Button variant="ghost" onClick={onClose} size="sm">
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
          <h1 className="text-3xl font-bold text-gray-800 mb-2">🌬️ {recommendation.title}</h1>
          <p className="text-gray-600">
            Cycle {cycle} of {totalCycles}
          </p>
        </div>

        {/* Breathing Circle Animation */}
        <div className="flex flex-col items-center justify-center min-h-[500px]">
          <motion.div
            className="rounded-full flex items-center justify-center shadow-2xl mb-8"
            animate={{
              width: getCircleSize(),
              height: getCircleSize(),
              backgroundColor: getPhaseColor()
            }}
            transition={{
              duration: phase === 'inhale' ? inhaleSeconds : phase === 'exhale' ? exhaleSeconds : 1,
              ease: "easeInOut"
            }}
          >
            <span className="text-4xl font-bold text-white">
              {countdown}
            </span>
          </motion.div>

          <motion.p
            key={phase}
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            className="text-2xl font-semibold text-gray-800 text-center mb-4"
          >
            {getPhaseInstruction()}
          </motion.p>

          <p className="text-gray-600 text-center">
            {phase === 'inhale' && 'Through your nose'}
            {phase === 'exhale' && 'Through your mouth'}
            {phase === 'hold' && 'Gently, without strain'}
            {phase === 'rest' && 'Natural breathing'}
          </p>
        </div>

        {/* Progress */}
        <div className="mt-8 bg-white/60 rounded-lg p-4">
          <div className="flex justify-between text-sm text-gray-600 mb-2">
            <span>Progress</span>
            <span>{Math.round((cycle / totalCycles) * 100)}%</span>
          </div>
          <div className="h-2 bg-gray-200 rounded-full overflow-hidden">
            <motion.div
              className="h-full bg-gradient-to-r from-blue-500 to-cyan-500"
              animate={{ width: `${(cycle / totalCycles) * 100}%` }}
              transition={{ duration: 0.5 }}
            />
          </div>
        </div>
      </div>
      </div>
    </div>
  );
}
