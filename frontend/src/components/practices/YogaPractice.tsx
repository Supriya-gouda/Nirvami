import { useState, useEffect, useRef } from 'react';
import { motion, AnimatePresence } from 'motion/react';
import { X, Play, Pause, Volume2, VolumeX, CheckCircle2, Clock, ChevronLeft } from 'lucide-react';
import { Button } from '../ui/button';
import { Card, CardContent } from '../ui/card';
import MusicManager from '../../services/MusicManager';
import VoiceGuidanceService from '../../services/VoiceGuidanceService';
import api from '../../services/api';
import { PracticeLearnSection } from './PracticeLearnSection';
import { useToast } from '../../hooks/use-toast';

interface YogaPracticeProps {
  recommendation: {
    id?: string;
    title: string;
    content: string;
    category?: string;
  };
  onComplete: () => void;
  onClose: () => void;
}

interface YogaStep {
  instruction: string;
  duration_seconds: number;
}

export function YogaPractice({ recommendation, onComplete, onClose }: YogaPracticeProps) {
  const { toast } = useToast();
  const [showLearnSection, setShowLearnSection] = useState(true);
  const [steps, setSteps] = useState<YogaStep[]>([]);
  const [currentStep, setCurrentStep] = useState(0);
  const [isPracticing, setIsPracticing] = useState(false);
  const [stepCountdown, setStepCountdown] = useState(0);
  const [isMusicEnabled, setIsMusicEnabled] = useState(true);
  const [totalElapsed, setTotalElapsed] = useState(0);
  const [isCompleting, setIsCompleting] = useState(false);
  
  const musicManager = useRef<MusicManager | null>(null);
  const voiceService = useRef<VoiceGuidanceService | null>(null);
  const stepTimerRef = useRef<NodeJS.Timeout | null>(null);
  const elapsedTimerRef = useRef<NodeJS.Timeout | null>(null);
  const startTimeRef = useRef<Date | null>(null);

  // Initialize services and parse steps
  useEffect(() => {
    // Initialize music manager
    musicManager.current = new MusicManager();
    
    // Initialize voice service
    voiceService.current = new VoiceGuidanceService();

    // Parse yoga steps from recommendation
    const parsedSteps = parseYogaSteps(recommendation.content);
    setSteps(parsedSteps);

    return () => {
      cleanup();
    };
  }, []);

  const cleanup = () => {
    if (stepTimerRef.current) clearInterval(stepTimerRef.current);
    if (elapsedTimerRef.current) clearInterval(elapsedTimerRef.current);
    if (musicManager.current) musicManager.current.stop();
    if (voiceService.current) voiceService.current.stop();
  };

  const parseYogaSteps = (content: string): YogaStep[] => {
    const parsed: YogaStep[] = [];

    // Try to parse structured steps from content
    // Handle both inline steps (1. First. 2. Second.) and multi-line steps
    let mainSteps: YogaStep[] = [];
    
    // First, try to split by numbered patterns like "1.", "2.", "Step 1:", etc.
    // This regex handles both inline and multi-line cases
    const stepPattern = /(?:^|(?:\.\s*))(?:Step\s*)?(\d+)[:.)]\s*([^.]+(?:\.[^0-9][^.]*)*?)(?=(?:\s*\d+[:.)]|\s*Step\s*\d+|$))/gi;
    const stepMatches = Array.from(content.matchAll(stepPattern));
    
    if (stepMatches && stepMatches.length > 0) {
      // Parse each numbered step individually
      stepMatches.forEach((match, idx) => {
        let instruction = match[2].trim();
        
        // Clean up instruction - remove leading/trailing periods, extra spaces
        instruction = instruction.replace(/^\.\s*/, '').replace(/\.\s*$/, '').trim();
        
        // Skip if instruction is too short (likely parsing error)
        if (instruction.length < 10) return;
        
        // Extract duration from text like "hold for 3 minutes", "30 seconds", "5-10 min"
        const durationMatch = instruction.match(/(?:hold|for|take)\s*(?:for)?\s*(\d+)\s*(?:to|-|–)?\s*(\d+)?\s*(min(?:ute)?s?|sec(?:ond)?s?)/i);
        let durationSeconds = 45; // default
        
        if (durationMatch) {
          const value1 = parseInt(durationMatch[1]);
          const value2 = durationMatch[2] ? parseInt(durationMatch[2]) : value1;
          const avgValue = Math.round((value1 + value2) / 2);
          const unit = durationMatch[3].toLowerCase();
          durationSeconds = unit.startsWith('min') ? avgValue * 60 : avgValue;
        } else {
          // Assign durations based on position
          if (idx === 0) durationSeconds = 30; // First step
          else if (idx === stepMatches.length - 1) durationSeconds = 30; // Last step
          else durationSeconds = 45; // Middle steps
        }
        
        // Add period if not present
        if (!instruction.endsWith('.') && !instruction.endsWith('!') && !instruction.endsWith('?')) {
          instruction += '.';
        }
        
        mainSteps.push({ instruction, duration_seconds: durationSeconds });
      });
    } else {
      // No numbered steps found, split by periods/sentences
      const sentences = content.split(/\.\s+/).filter(s => s.trim().length > 10);
      if (sentences.length > 1) {
        sentences.forEach((sentence, idx) => {
          mainSteps.push({ 
            instruction: sentence.trim() + (sentence.trim().endsWith('.') ? '' : '.'), 
            duration_seconds: idx === 0 ? 30 : idx === sentences.length - 1 ? 30 : 45
          });
        });
      } else {
        // Single instruction - use as is
        mainSteps.push({ 
          instruction: content.trim(), 
          duration_seconds: 60 
        });
      }
    }

    // Check if first step is already a preparation step (check for keywords)
    const firstStepLower = mainSteps[0]?.instruction.toLowerCase() || '';
    const isPrepStep = firstStepLower.includes('comfortable') || 
                       firstStepLower.includes('prepare') || 
                       firstStepLower.includes('sit') ||
                       firstStepLower.includes('position');

    // Add beginning step ONLY if first step is not already a prep step
    if (!isPrepStep) {
      parsed.push({ 
        instruction: "Get comfortable and prepare by sitting in a peaceful place.", 
        duration_seconds: 15 
      });
    }

    // Add all main steps
    parsed.push(...mainSteps);

    // Add ending relaxation step
    parsed.push({ 
      instruction: "Release slowly and relax. Take a moment to notice how you feel.", 
      duration_seconds: 15 
    });

    return parsed;
  };

  const startPractice = async () => {
    setIsPracticing(true);
    setCurrentStep(0);
    setTotalElapsed(0);
    startTimeRef.current = new Date();

    // Initialize and start music - MUST complete before starting practice
    if (isMusicEnabled && musicManager.current) {
      try {
        console.log('🎵 Initializing music for yoga practice...');
        await musicManager.current.init('yoga');
        console.log('🎵 Music initialized, now playing...');
        await musicManager.current.play();
        console.log('🎵 Background music playing successfully');
      } catch (error) {
        console.warn('⚠️ Could not start music:', error);
        // Continue without music
      }
    }

    // Start elapsed time tracker
    elapsedTimerRef.current = setInterval(() => {
      if (startTimeRef.current) {
        const elapsed = Math.floor((Date.now() - startTimeRef.current.getTime()) / 1000);
        setTotalElapsed(elapsed);
      }
    }, 1000);

    // Start first step
    executeStep(0);
  };

  const executeStep = async (stepIndex: number) => {
    if (stepIndex >= steps.length) {
      completePractice();
      return;
    }

    const step = steps[stepIndex];
    setStepCountdown(step.duration_seconds);

    // Speak the instruction
    const announcement = `Step ${stepIndex + 1}. ${step.instruction}`;
    await voiceService.current?.speak(announcement);

    // Start countdown
    let remaining = step.duration_seconds;
    stepTimerRef.current = setInterval(() => {
      remaining--;
      setStepCountdown(remaining);

      if (remaining <= 0) {
        if (stepTimerRef.current) clearInterval(stepTimerRef.current);
        
        // Auto-advance to next step
        const nextStep = stepIndex + 1;
        if (nextStep < steps.length) {
          setCurrentStep(nextStep);
          setTimeout(() => executeStep(nextStep), 500);
        } else {
          completePractice();
        }
      }
    }, 1000);
  };

  const pausePractice = () => {
    setIsPracticing(false);
    if (stepTimerRef.current) clearInterval(stepTimerRef.current);
    if (elapsedTimerRef.current) clearInterval(elapsedTimerRef.current);
    musicManager.current?.pause();
    voiceService.current?.pause();
  };

  const resumePractice = () => {
    setIsPracticing(true);
    
    // Resume music
    musicManager.current?.resume();
    
    // Resume elapsed timer
    if (!startTimeRef.current) {
      startTimeRef.current = new Date(Date.now() - totalElapsed * 1000);
    }
    
    elapsedTimerRef.current = setInterval(() => {
      if (startTimeRef.current) {
        const elapsed = Math.floor((Date.now() - startTimeRef.current.getTime()) / 1000);
        setTotalElapsed(elapsed);
      }
    }, 1000);

    // Resume step countdown
    if (stepCountdown > 0) {
      let remaining = stepCountdown;
      stepTimerRef.current = setInterval(() => {
        remaining--;
        setStepCountdown(remaining);

        if (remaining <= 0) {
          if (stepTimerRef.current) clearInterval(stepTimerRef.current);
          
          const nextStep = currentStep + 1;
          if (nextStep < steps.length) {
            setCurrentStep(nextStep);
            setTimeout(() => executeStep(nextStep), 500);
          } else {
            completePractice();
          }
        }
      }, 1000);
    }
  };

  const completePractice = async () => {
    setIsCompleting(true);
    cleanup();

    try {
      // Log completion
      const durationMinutes = Math.ceil(totalElapsed / 60);
      const payload = {
        practice_type: 'yoga',
        practice_name: recommendation.title,
        duration_minutes: durationMinutes,
        recommendation_id: recommendation.id || undefined, // Only send if exists
        completion_status: 'completed'
      };

      console.log('📌 Practice logging payload:', JSON.stringify(payload, null, 2));
      
      const response = await api.createPracticeSession(payload);

      console.log('✅ Practice Stored - Backend response:', response);
      console.log('✅ Completion Summary Updated');
      
      toast({
        title: "Practice Complete!",
        description: `${recommendation.title} has been completed successfully.`,
        duration: 3000,
      });
      
      // Small delay to show completion animation
      setTimeout(() => {
        onComplete();
      }, 1500);
    } catch (error: any) {
      console.error('❌ Failed to log practice completion:', error);
      console.error('❌ Error response:', error.response?.data);
      console.error('❌ Error status:', error.response?.status);
      console.error('❌ Error details:', error.message);
      
      toast({
        title: "Logging Failed",
        description: "Practice completed but couldn't save. Please try again.",
        variant: "destructive",
        duration: 4000,
      });
      
      // Still call onComplete even if logging fails
      setTimeout(() => {
        onComplete();
      }, 1500);
    }
  };

  const toggleMusic = () => {
    const newState = !isMusicEnabled;
    setIsMusicEnabled(newState);
    
    if (newState && isPracticing) {
      musicManager.current?.init('yoga').then(() => {
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
      <div className="fixed inset-0 bg-gradient-to-br from-green-50 to-emerald-100 flex items-center justify-center z-50">
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
            <CheckCircle2 className="w-24 h-24 text-green-600" />
          </motion.div>
          <h2 className="text-3xl font-bold text-gray-800">Practice Complete!</h2>
          <p className="text-gray-600 mt-2">Redirecting...</p>
        </motion.div>
      </div>
    );
  }

  return (
    <div className="fixed inset-0 bg-gradient-to-br from-purple-50 via-pink-50 to-orange-50 z-40 overflow-hidden">
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
          </div>
        </div>

        {/* Practice Title */}
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          className="text-center mb-8"
        >
          <h1 className="text-3xl font-bold text-gray-800 mb-2">🧘 {recommendation.title}</h1>
          <div className="flex justify-center items-center gap-4 text-gray-600">
            <div className="flex items-center gap-1">
              <Clock className="w-4 h-4" />
              <span>{formatTime(totalElapsed)}</span>
            </div>
          </div>
        </motion.div>

        {/* Show Learn Section First */}
        {showLearnSection && !isPracticing ? (
          <PracticeLearnSection
            practiceName={recommendation.title}
            category={recommendation.category || 'yoga'}
            content={recommendation.content}
            onStartPractice={() => setShowLearnSection(false)}
          />
        ) : !isPracticing ? (
          /* Pre-Practice */
          <Card>
            <CardContent className="p-8 text-center">
              <motion.div
                initial={{ scale: 0.9 }}
                animate={{ scale: 1 }}
                transition={{ duration: 0.5 }}
              >
                <div className="text-6xl mb-4">🧘‍♀️</div>
                <h2 className="text-2xl font-bold text-gray-800 mb-4">Ready to Practice?</h2>
                <p className="text-gray-600 mb-6">
                  This guided yoga session will take you through {steps.length} steps.
                  Follow the voice instructions and take your time.
                </p>
                <Button onClick={startPractice} size="lg" className="px-8">
                  <Play className="w-5 h-5 mr-2" />
                  Start Practice
                </Button>
              </motion.div>
            </CardContent>
          </Card>
        ) : (
          /* During Practice */
          <div className="space-y-6">
            {/* Current Step Card */}
            <Card className="bg-white/80 backdrop-blur">
              <CardContent className="p-8">
                <div className="text-center mb-4">
                  <div className="text-sm text-gray-500 mb-2">
                    Step {currentStep + 1} of {steps.length}
                  </div>
                  <motion.p
                    key={currentStep}
                    initial={{ opacity: 0, y: 10 }}
                    animate={{ opacity: 1, y: 0 }}
                    className="text-2xl font-semibold text-gray-800"
                  >
                    {steps[currentStep]?.instruction}
                  </motion.p>
                </div>

                {/* Countdown Circle */}
                <div className="flex justify-center my-8">
                  <div className="relative w-32 h-32">
                    <svg className="w-full h-full -rotate-90">
                      <circle
                        cx="64"
                        cy="64"
                        r="60"
                        stroke="#e5e7eb"
                        strokeWidth="8"
                        fill="none"
                      />
                      <motion.circle
                        cx="64"
                        cy="64"
                        r="60"
                        stroke="#10b981"
                        strokeWidth="8"
                        fill="none"
                        strokeLinecap="round"
                        strokeDasharray={377}
                        strokeDashoffset={377 * (1 - (stepCountdown / (steps[currentStep]?.duration_seconds || 1)))}
                        transition={{ duration: 1 }}
                      />
                    </svg>
                    <div className="absolute inset-0 flex items-center justify-center">
                      <span className="text-3xl font-bold text-gray-800">
                        {stepCountdown}
                      </span>
                    </div>
                  </div>
                </div>

                {/* Controls */}
                <div className="flex justify-center gap-4">
                  <Button onClick={pausePractice} variant="outline">
                    <Pause className="w-5 h-5 mr-2" />
                    Pause
                  </Button>
                </div>
              </CardContent>
            </Card>

            {/* Progress Bar */}
            <div className="bg-white/60 rounded-lg p-4">
              <div className="flex justify-between text-sm text-gray-600 mb-2">
                <span>Progress</span>
                <span>{Math.round((currentStep / steps.length) * 100)}%</span>
              </div>
              <div className="h-2 bg-gray-200 rounded-full overflow-hidden">
                <motion.div
                  className="h-full bg-gradient-to-r from-purple-500 to-pink-500"
                  initial={{ width: '0%' }}
                  animate={{ width: `${(currentStep / steps.length) * 100}%` }}
                  transition={{ duration: 0.5 }}
                />
              </div>
            </div>
          </div>
        )}

        {/* Paused State Overlay */}
        <AnimatePresence>
          {!isPracticing && totalElapsed > 0 && !isCompleting && (
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              className="fixed inset-0 bg-black/40 backdrop-blur-sm flex items-center justify-center z-50"
              onClick={(e) => e.stopPropagation()}
            >
              <Card className="max-w-md">
                <CardContent className="p-8 text-center">
                  <h3 className="text-2xl font-bold text-gray-800 mb-4">Practice Paused</h3>
                  <p className="text-gray-600 mb-6">Take your time. Resume when ready.</p>
                  <div className="flex gap-4 justify-center">
                    <Button onClick={resumePractice} size="lg">
                      <Play className="w-5 h-5 mr-2" />
                      Resume
                    </Button>
                    <Button onClick={onClose} variant="outline" size="lg">
                      <X className="w-5 h-5 mr-2" />
                      Exit
                    </Button>
                  </div>
                </CardContent>
              </Card>
            </motion.div>
          )}
        </AnimatePresence>
        </div>
      </div>
    </div>
  );
}
