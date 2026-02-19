import { useState, useEffect, useRef } from 'react';
import { motion, AnimatePresence } from 'motion/react';
import {
  Play,
  Pause,
  RotateCcw,
  CheckCircle2,
  Volume2,
  VolumeX,
  Clock,
  TrendingUp,
  BookOpen,
  Activity,
  X,
  Star,
  ChevronLeft
} from 'lucide-react';
import { Navigation } from './Navigation';
import { Button } from './ui/button';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { Badge } from './ui/badge';
import type { PageType } from '../App';
import type { User as UserType } from '../types/api.types';
import api from '../services/api';

interface PracticeDetailPageProps {
  user: UserType | null;
  recommendation: {
    id?: string;
    title: string;
    content: string;
    category?: string;
    source?: string;
  };
  onNavigate: (page: PageType) => void;
  onLogout?: () => void;
  onOpenNotifications?: () => void;
  onClose: () => void;
}

interface PracticeStep {
  instruction: string;
  duration_seconds?: number;
  duration_text?: string;
}

interface PracticeContent {
  practice_type: string;
  practice_name: string;
  sanskrit_name?: string;
  description: string;
  benefits: string[];
  difficulty: string;
  duration_min: number;
  duration_max: number;
  youtube_video_id?: string;
  youtube_title?: string;
  avatar_animation_steps?: any;
  tts_instructions: string[];
  steps?: PracticeStep[];
  dosha_tags: string[];
  emotion_tags: string[];
  category: string;
  icon: string;
}

export function PracticeDetailPage({
  user,
  recommendation,
  onNavigate,
  onLogout,
  onOpenNotifications,
  onClose
}: PracticeDetailPageProps) {
  const [practice, setPractice] = useState<PracticeContent | null>(null);
  const [hasEnhancedContent, setHasEnhancedContent] = useState(false);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState<'learn' | 'practice'>('learn');
  const [isPracticing, setIsPracticing] = useState(false);
  const [currentStep, setCurrentStep] = useState(0);
  const [isSpeaking, setIsSpeaking] = useState(false);
  const [practiceStartTime, setPracticeStartTime] = useState<Date | null>(null);
  const [elapsedTime, setElapsedTime] = useState(0);
  const [isCompleted, setIsCompleted] = useState(false);
  const [satisfactionRating, setSatisfactionRating] = useState(0);
  const [stepCountdown, setStepCountdown] = useState(0); // Countdown timer for current step
  const speechSynthesisRef = useRef<SpeechSynthesisUtterance | null>(null);
  const timerRef = useRef<NodeJS.Timeout | null>(null);
  const autoAdvanceTimerRef = useRef<NodeJS.Timeout | null>(null);
  const stepCountdownRef = useRef<NodeJS.Timeout | null>(null);

  useEffect(() => {
    loadPracticeContent();
    return () => {
      // Cleanup
      stopSpeech();
      if (timerRef.current) clearInterval(timerRef.current);
      if (autoAdvanceTimerRef.current) clearTimeout(autoAdvanceTimerRef.current);
      if (stepCountdownRef.current) clearInterval(stepCountdownRef.current);
    };
  }, [recommendation]);

  useEffect(() => {
    // Update elapsed time every second when practicing
    if (isPracticing && practiceStartTime) {
      timerRef.current = setInterval(() => {
        const elapsed = Math.floor((Date.now() - practiceStartTime.getTime()) / 1000);
        setElapsedTime(elapsed);
      }, 1000);
    } else {
      if (timerRef.current) clearInterval(timerRef.current);
    }

    return () => {
      if (timerRef.current) clearInterval(timerRef.current);
    };
  }, [isPracticing, practiceStartTime]);

  const loadPracticeContent = async () => {
    try {
      setLoading(true);

      // Try to fetch enhanced content from database
      try {
        const response = await api.getPracticeContent(recommendation.title);
        if (response.success && response.practice) {
          setPractice(response.practice);
          setHasEnhancedContent(true);
          setLoading(false);
          return;
        }
      } catch (error) {
        console.log('No enhanced content found, using recommendation content');
      }

      // Fallback: Create dynamic practice from recommendation
      const parsedSteps = parseStepsFromContent(recommendation.content);

      // Check if first step is already a preparation step
      const firstStepLower = parsedSteps[0]?.instruction.toLowerCase() || '';
      const isPrepStep = firstStepLower.includes('comfortable') || 
                        firstStepLower.includes('prepare') || 
                        firstStepLower.includes('sit') ||
                        firstStepLower.includes('position') ||
                        firstStepLower.includes('find a quiet');

      // Add preparation step at the beginning ONLY if not already present
      if (!isPrepStep) {
        parsedSteps.unshift({
          instruction: 'Get comfortable and prepare by sitting in a peaceful place.',
          duration_seconds: 15,
          duration_text: 'for 15 seconds'
        });
      }

      // Add relaxation step at the end
      parsedSteps.push({
        instruction: 'Release slowly and relax. Take a moment to notice how you feel.',
        duration_seconds: 15,
        duration_text: 'for 15 seconds'
      });

      const dynamicPractice: PracticeContent = {
        practice_type: recommendation.category || 'lifestyle',
        practice_name: recommendation.title,
        description: recommendation.content,
        benefits: extractBenefitsFromContent(recommendation.content),
        difficulty: 'beginner',
        duration_min: 5,
        duration_max: 15,
        tts_instructions: parsedSteps.map(s => `${s.instruction} ${s.duration_text}`),
        steps: parsedSteps,
        dosha_tags: [],
        emotion_tags: [],
        category: recommendation.category || 'wellness',
        icon: '🧘'
      };

      setPractice(dynamicPractice);
      setHasEnhancedContent(false);
      setLoading(false);
    } catch (error) {
      console.error('Error loading practice content:', error);
      setLoading(false);
    }
  };

  // Helper function to extract benefits from recommendation text
  const extractBenefitsFromContent = (content: string): string[] => {
    // Look for bullet points, numbered lists, or sentences that suggest benefits
    const benefits: string[] = [];

    // Split by sentences
    const sentences = content.split(/[.!?]+/).filter(s => s.trim().length > 0);

    // Take first 3-4 substantial sentences as benefits
    sentences.slice(0, 4).forEach(sentence => {
      const trimmed = sentence.trim();
      if (trimmed.length > 20 && trimmed.length < 150) {
        benefits.push(trimmed);
      }
    });

    return benefits.length > 0 ? benefits : ['Promotes overall wellness', 'Supports mind-body balance'];
  };

  // Helper function to parse steps from recommendation content
  const parseStepsFromContent = (content: string): PracticeStep[] => {
    const steps: PracticeStep[] = [];

    // Try to parse numbered steps - handle both inline (1. First. 2. Second.) and multi-line
    const stepPattern = /(?:^|(?:\.\s*))(?:Step\s*)?(\d+)[:.)]\s*([^.]+(?:\.[^0-9][^.]*)*?)(?=(?:\s*\d+[:.)]|\s*Step\s*\d+|$))/gi;
    const stepMatches = Array.from(content.matchAll(stepPattern));

    if (stepMatches && stepMatches.length > 0) {
      stepMatches.forEach((match, idx) => {
        // Remove step numbering and clean up
        let instruction = match[2].trim();
        instruction = instruction.replace(/^\.\s*/, '').replace(/\.\s*$/, '').trim();
        
        // Skip if too short (parsing error)
        if (instruction.length < 10) return;

        // Extract duration if mentioned (including ranges like "5 to 15 min", "5-15 min")
        let durationText = '';
        let durationSeconds = 0;

        // First try to match ranges: "5 to 15 min", "5-15 minutes", "2 to 3 seconds"
        const rangeMatch = instruction.match(/(?:for|hold(?:\s+for)?|take)\s*(\d+)\s*(?:to|-|–)\s*(\d+)\s*(min(?:ute)?s?|sec(?:ond)?s?)/i);
        if (rangeMatch) {
          const minValue = parseInt(rangeMatch[1]);
          const maxValue = parseInt(rangeMatch[2]);
          const unit = rangeMatch[3].toLowerCase();

          // Calculate average for countdown
          const avgValue = Math.round((minValue + maxValue) / 2);
          durationSeconds = unit.startsWith('min') ? avgValue * 60 : avgValue;

          // Keep original range text for TTS (e.g., "for 5 to 15 minutes")
          const unitText = unit.startsWith('min') ? 'minute' : 'second';
          durationText = `for ${minValue} to ${maxValue} ${unitText}${maxValue > 1 ? 's' : ''}`;
        } else {
          // Try single duration: "for 5 minutes", "30 seconds", "hold 10 sec"
          const durationMatch = instruction.match(/(?:for|hold(?:\s+for)?|take)\s*(?:for)?\s*(\d+)\s*(min(?:ute)?s?|sec(?:ond)?s?)/i);
          if (durationMatch) {
            const value = parseInt(durationMatch[1]);
            const unit = durationMatch[2].toLowerCase();
            durationSeconds = unit.startsWith('min') ? value * 60 : value;
            durationText = `for ${value} ${unit.startsWith('min') ? 'minute' : 'second'}${value > 1 ? 's' : ''}`;
          } else {
            // Default durations based on step position
            durationSeconds = idx === 0 ? 30 : 45; // First step shorter, others 45s default
            durationText = `for ${durationSeconds} seconds`;
          }
        }
        
        // Add period if not present
        if (!instruction.endsWith('.') && !instruction.endsWith('!') && !instruction.endsWith('?')) {
          instruction += '.';
        }

        steps.push({
          instruction: instruction,
          duration_seconds: durationSeconds,
          duration_text: durationText
        });
      });
    } else {
      // Fallback: split by periods
      const sentences = content.split(/[.!?]+/).filter(s => s.trim().length > 20);
      sentences.forEach((sentence, idx) => {
        const durationSeconds = idx === 0 ? 30 : 45;
        steps.push({
          instruction: sentence.trim() + '.',
          duration_seconds: durationSeconds,
          duration_text: `for ${durationSeconds} seconds`
        });
      });
    }

    return steps.length > 0 ? steps : [{
      instruction: content,
      duration_seconds: 60,
      duration_text: 'for 1 minute'
    }];
  };

  // Helper function to get Indian female voice
  const getIndianFemaleVoice = (): SpeechSynthesisVoice | null => {
    const voices = window.speechSynthesis.getVoices();

    // Priority 1: Look for Google Hindi or Indian English female voices
    const preferredVoices = [
      'Google हिन्दी',
      'Microsoft Heera - English (India)',
      'Microsoft Heera Desktop - English (India)',
      'Google UK English Female',
      'Google US English Female'
    ];

    for (const voiceName of preferredVoices) {
      const voice = voices.find(v => v.name.includes(voiceName));
      if (voice) return voice;
    }

    // Priority 2: Any Indian English voice (en-IN)
    const indianVoice = voices.find(v => v.lang.startsWith('en-IN') || v.lang.startsWith('hi-IN'));
    if (indianVoice) return indianVoice;

    // Priority 3: Any voice with "Heera" or Indian-sounding names
    const indianNamedVoice = voices.find(v =>
      v.name.includes('Heera') ||
      v.name.includes('Ravi') ||
      v.name.includes('Swara')
    );
    if (indianNamedVoice) return indianNamedVoice;

    // Fallback: Use default voice
    return voices[0] || null;
  };

  // Helper function to split content into TTS instructions
  const splitIntoInstructions = (content: string): string[] => {
    const steps = parseStepsFromContent(content);
    return steps.map(step => `${step.instruction} ${step.duration_text}`);
  };

  const startPractice = () => {
    setActiveTab('practice');
    setIsPracticing(true);
    setPracticeStartTime(new Date());
    setCurrentStep(0);
    speakInstruction(0);
  };

  const pausePractice = () => {
    setIsPracticing(false);
    stopSpeech();

    // Clear timers when pausing
    if (autoAdvanceTimerRef.current) {
      clearTimeout(autoAdvanceTimerRef.current);
      autoAdvanceTimerRef.current = null;
    }
    if (stepCountdownRef.current) {
      clearInterval(stepCountdownRef.current);
      stepCountdownRef.current = null;
    }
  };

  const resumePractice = () => {
    setIsPracticing(true);
    speakInstruction(currentStep);
  };

  const resetPractice = () => {
    setIsPracticing(false);
    setCurrentStep(0);
    setElapsedTime(0);
    setStepCountdown(0);
    setPracticeStartTime(null);
    stopSpeech();

    // Clear timers
    if (autoAdvanceTimerRef.current) {
      clearTimeout(autoAdvanceTimerRef.current);
      autoAdvanceTimerRef.current = null;
    }
    if (stepCountdownRef.current) {
      clearInterval(stepCountdownRef.current);
      stepCountdownRef.current = null;
    }
  };

  const nextStep = () => {
    if (!practice) return;

    // Clear any pending timers before moving to next step
    if (autoAdvanceTimerRef.current) {
      clearTimeout(autoAdvanceTimerRef.current);
      autoAdvanceTimerRef.current = null;
    }
    if (stepCountdownRef.current) {
      clearInterval(stepCountdownRef.current);
      stepCountdownRef.current = null;
    }

    // Cancel any ongoing speech
    window.speechSynthesis.cancel();
    setIsSpeaking(false);
    setStepCountdown(0);

    if (currentStep < practice.tts_instructions.length - 1) {
      const next = currentStep + 1;
      setCurrentStep(next);
      // Use setTimeout to ensure state has updated before speaking
      setTimeout(() => {
        if (isPracticing) {
          speakInstruction(next);
        }
      }, 100);
    } else {
      // Completed all steps
      completePractice();
    }
  };

  const speakInstruction = (stepIndex: number) => {
    if (!practice || stepIndex >= practice.tts_instructions.length) return;

    stopSpeech();

    // Clear any existing timers
    if (autoAdvanceTimerRef.current) {
      clearTimeout(autoAdvanceTimerRef.current);
      autoAdvanceTimerRef.current = null;
    }
    if (stepCountdownRef.current) {
      clearInterval(stepCountdownRef.current);
      stepCountdownRef.current = null;
    }

    // Get the step duration in seconds (exact duration from the parsed step)
    let stepDurationSeconds = 30; // Default 30 seconds
    if (practice.steps && practice.steps[stepIndex]?.duration_seconds) {
      stepDurationSeconds = practice.steps[stepIndex].duration_seconds!;
    }

    // Get the full instruction with duration
    const fullInstruction = practice.tts_instructions[stepIndex];

    // Create utterance with step number announcement
    const stepAnnouncement = `Step ${stepIndex + 1}. ${fullInstruction}`;
    const utterance = new SpeechSynthesisUtterance(stepAnnouncement);

    // Set Indian female voice
    const indianVoice = getIndianFemaleVoice();
    if (indianVoice) {
      utterance.voice = indianVoice;
    }

    utterance.rate = 0.85; // Slower for better clarity with durations
    utterance.pitch = 1.0;
    utterance.volume = 1.0;

    utterance.onstart = () => setIsSpeaking(true);
    utterance.onend = () => {
      setIsSpeaking(false);

      // Start countdown timer for this step
      setStepCountdown(stepDurationSeconds);

      // Use interval to decrement countdown
      let timeRemaining = stepDurationSeconds;
      stepCountdownRef.current = setInterval(() => {
        timeRemaining--;
        setStepCountdown(timeRemaining);

        if (timeRemaining <= 0) {
          if (stepCountdownRef.current) {
            clearInterval(stepCountdownRef.current);
            stepCountdownRef.current = null;
          }
        }
      }, 1000);

      // Set auto-advance timer using exact step duration
      autoAdvanceTimerRef.current = setTimeout(() => {
        // Clear countdown timer before advancing
        if (stepCountdownRef.current) {
          clearInterval(stepCountdownRef.current);
          stepCountdownRef.current = null;
        }

        if (stepIndex < practice.tts_instructions.length - 1) {
          nextStep();
        } else {
          // Last step (relaxation) - complete the practice
          completePractice();
        }
      }, stepDurationSeconds * 1000);
    };
    utterance.onerror = (event) => {
      console.error('Speech synthesis error:', event);
      setIsSpeaking(false);
      // Still advance to next step even if speech fails
      if (!autoAdvanceTimerRef.current && stepIndex < practice.tts_instructions.length - 1) {
        setTimeout(() => nextStep(), 1000);
      }
    };

    speechSynthesisRef.current = utterance;

    // Ensure voices are loaded before speaking
    if (window.speechSynthesis.getVoices().length === 0) {
      window.speechSynthesis.addEventListener('voiceschanged', () => {
        const voice = getIndianFemaleVoice();
        if (voice) utterance.voice = voice;
        window.speechSynthesis.speak(utterance);
      }, { once: true });
    } else {
      window.speechSynthesis.speak(utterance);
    }
  };

  const stopSpeech = () => {
    window.speechSynthesis.cancel();
    setIsSpeaking(false);

    // Clear timers when speech is manually stopped
    if (autoAdvanceTimerRef.current) {
      clearTimeout(autoAdvanceTimerRef.current);
      autoAdvanceTimerRef.current = null;
    }
    if (stepCountdownRef.current) {
      clearInterval(stepCountdownRef.current);
      stepCountdownRef.current = null;
    }
  };

  const toggleSpeech = () => {
    if (isSpeaking) {
      stopSpeech();
    } else {
      speakInstruction(currentStep);
    }
  };

  const completePractice = async () => {
    setIsPracticing(false);
    setIsCompleted(true);
    stopSpeech();

    // Show completion UI
    // Will log session after user provides rating
  };

  const submitCompletion = async () => {
    if (!practice) return;

    try {
      const durationMinutes = Math.ceil(elapsedTime / 60);

      await api.createPracticeSession({
        practice_type: practice.practice_type,
        practice_name: practice.practice_name,
        duration_minutes: durationMinutes,
        recommendation_id: recommendation.id,
        completion_status: 'completed',
        satisfaction_rating: satisfactionRating
      });

      // Show success message and close
      setTimeout(() => {
        onClose();
      }, 2000);
    } catch (error) {
      console.error('Error logging practice session:', error);
    }
  };

  const formatTime = (seconds: number) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-purple-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Loading practice...</p>
        </div>
      </div>
    );
  }

  if (!practice) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <p className="text-gray-600">Practice not found</p>
          <Button onClick={onClose} className="mt-4">Go Back</Button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-purple-50 via-white to-blue-50">
      <Navigation
        currentPage="dashboard"
        onNavigate={onNavigate}
        onLogout={onLogout}
        user={user}
        onOpenNotifications={onOpenNotifications}
      />

      <div className="max-w-6xl mx-auto p-4 md:p-8">
        {/* Header */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="mb-6"
        >
          <div className="mb-4">
            <Button
              variant="ghost"
              onClick={onClose}
              className="mb-4 -ml-2"
            >
              <ChevronLeft className="h-5 w-5 mr-1" />
              Back to Recommendations
            </Button>
            <div className="flex items-center gap-3">
              <span className="text-4xl">{practice.icon}</span>
              <div>
                <h1 className="text-3xl font-bold text-gray-900">{practice.practice_name}</h1>
                {practice.sanskrit_name && (
                  <p className="text-lg text-gray-600 italic">{practice.sanskrit_name}</p>
                )}
              </div>
            </div>
          </div>

          <div className="flex flex-wrap gap-2 mb-4">
            <Badge variant="outline" className="capitalize">{practice.difficulty}</Badge>
            <Badge variant="outline">{practice.practice_type}</Badge>
            <Badge variant="outline">
              <Clock className="w-3 h-3 mr-1" />
              {practice.duration_min}-{practice.duration_max} min
            </Badge>
            {practice.dosha_tags.map(dosha => (
              <Badge key={dosha} variant="secondary">{dosha}</Badge>
            ))}
          </div>

          <p className="text-gray-700 text-lg">{practice.description}</p>

          {/* Benefits */}
          <div className="mt-4 grid grid-cols-2 md:grid-cols-4 gap-2">
            {practice.benefits.map((benefit, index) => (
              <div key={index} className="flex items-center gap-2 text-sm text-gray-600">
                <CheckCircle2 className="w-4 h-4 text-green-600" />
                {benefit}
              </div>
            ))}
          </div>
        </motion.div>

        {/* Tabs */}
        <div className="flex gap-4 mb-6">
          <Button
            variant={activeTab === 'learn' ? 'default' : 'outline'}
            onClick={() => setActiveTab('learn')}
            className="flex-1"
          >
            <BookOpen className="w-4 h-4 mr-2" />
            Learn
          </Button>
          <Button
            variant={activeTab === 'practice' ? 'default' : 'outline'}
            onClick={() => setActiveTab('practice')}
            className="flex-1"
          >
            <Activity className="w-4 h-4 mr-2" />
            Practice
          </Button>
        </div>

        {/* Content */}
        <AnimatePresence mode="wait">
          {activeTab === 'learn' ? (
            <motion.div
              key="learn"
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: 20 }}
            >
              <Card>
                <CardHeader>
                  <CardTitle>Learn {practice.practice_name}</CardTitle>
                </CardHeader>
                <CardContent>
                  {/* YouTube Video - only if enhanced content available */}
                  {hasEnhancedContent && practice.youtube_video_id ? (
                    <div className="aspect-video w-full mb-4">
                      <iframe
                        width="100%"
                        height="100%"
                        src={`https://www.youtube.com/embed/${practice.youtube_video_id}`}
                        title={practice.youtube_title || practice.practice_name}
                        frameBorder="0"
                        allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
                        allowFullScreen
                        className="rounded-lg"
                      ></iframe>
                    </div>
                  ) : (
                    <div className="bg-gradient-to-br from-purple-50 to-blue-50 rounded-lg p-6 mb-4">
                      <div className="flex items-center gap-3 mb-3">
                        <div className="text-4xl">{practice.icon}</div>
                        <div>
                          <h3 className="font-semibold text-gray-900">Personalized Recommendation</h3>
                          <p className="text-sm text-gray-600">Based on your wellness data</p>
                        </div>
                      </div>
                      <p className="text-gray-700 leading-relaxed">{practice.description}</p>
                    </div>
                  )}

                  {/* Step-by-step guide - only show if not already shown above */}
                  {!hasEnhancedContent && (
                    <div className="space-y-4 mt-6">
                      <h3 className="text-lg font-semibold flex items-center gap-2">
                        <Activity className="w-5 h-5 text-purple-600" />
                        How to Practice
                      </h3>
                      <ol className="space-y-3">
                        {practice.steps ? practice.steps.map((step, index) => (
                          <motion.li
                            key={index}
                            initial={{ opacity: 0, x: -20 }}
                            animate={{ opacity: 1, x: 0 }}
                            transition={{ delay: index * 0.1 }}
                            className="flex gap-3 p-3 bg-purple-50 rounded-lg border border-purple-100"
                          >
                            <span className="flex-shrink-0 w-8 h-8 bg-purple-500 text-white rounded-full flex items-center justify-center font-semibold">
                              {index + 1}
                            </span>
                            <div className="flex-1">
                              <p className="text-gray-800">{step.instruction}</p>
                              {step.duration_text && (
                                <p className="text-sm text-purple-600 mt-1 flex items-center gap-1">
                                  <Clock className="w-3 h-3" />
                                  {step.duration_text}
                                </p>
                              )}
                            </div>
                          </motion.li>
                        )) : practice.tts_instructions.map((instruction, index) => (
                          <li key={index} className="flex gap-2 text-gray-700">
                            <span className="font-semibold text-purple-600">{index + 1}.</span>
                            {instruction}
                          </li>
                        ))}
                      </ol>
                    </div>
                  )}


                  {/* Show benefits if available */}
                  {practice.benefits && practice.benefits.length > 0 && (
                    <div className="mt-6">
                      <h3 className="text-lg font-semibold mb-3">Benefits</h3>
                      <div className="grid gap-2">
                        {practice.benefits.map((benefit, index) => (
                          <div key={index} className="flex items-start gap-2 text-gray-700">
                            <CheckCircle2 className="w-5 h-5 text-green-600 mt-0.5 flex-shrink-0" />
                            <span>{benefit}</span>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}

                  <Button
                    onClick={startPractice}
                    className="w-full mt-6"
                    size="lg"
                  >
                    <Play className="w-5 h-5 mr-2" />
                    Start Practicing
                  </Button>
                </CardContent>
              </Card>
            </motion.div>
          ) : (
            <motion.div
              key="practice"
              initial={{ opacity: 0, x: 20 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: -20 }}
            >
              {!isCompleted ? (
                <Card>
                  <CardHeader>
                    <div className="flex items-center justify-between">
                      <CardTitle>Practice Session</CardTitle>
                      <div className="flex items-center gap-4">
                        <div className="flex items-center gap-2 text-lg font-semibold">
                          <Clock className="w-5 h-5" />
                          {stepCountdown > 0 ? (
                            <span className="text-purple-600">
                              {Math.floor(stepCountdown / 60)}:{String(stepCountdown % 60).padStart(2, '0')}
                            </span>
                          ) : (
                            <span className="text-gray-500">0:00</span>
                          )}
                        </div>
                      </div>
                    </div>
                  </CardHeader>
                  <CardContent>
                    {/* Enhanced Practice Display */}
                    <div className="relative">
                      {/* Animated Background */}
                      <motion.div
                        className="absolute inset-0 bg-gradient-to-br from-purple-400/20 via-blue-400/20 to-cyan-400/20 rounded-2xl blur-xl"
                        animate={{
                          opacity: isPracticing ? [0.3, 0.6, 0.3] : 0.3,
                          scale: isPracticing ? [1, 1.05, 1] : 1
                        }}
                        transition={{
                          duration: 3,
                          repeat: isPracticing ? Infinity : 0,
                          ease: "easeInOut"
                        }}
                      />

                      <div className="relative bg-gradient-to-br from-white/90 to-purple-50/90 backdrop-blur-sm rounded-2xl p-8 mb-6 min-h-[280px] shadow-lg border border-purple-200/50">
                        <AnimatePresence mode="wait">
                          <motion.div
                            key={currentStep}
                            initial={{ scale: 0.9, opacity: 0, y: 20 }}
                            animate={{ scale: 1, opacity: 1, y: 0 }}
                            exit={{ scale: 0.9, opacity: 0, y: -20 }}
                            transition={{ duration: 0.4, ease: "easeOut" }}
                            className="text-center"
                          >
                            {/* Step Counter Badge */}
                            <motion.div
                              initial={{ scale: 0 }}
                              animate={{ scale: 1 }}
                              transition={{ delay: 0.2, type: "spring" }}
                              className="inline-block mb-4"
                            >
                              <Badge className="text-lg px-4 py-2 bg-gradient-to-r from-purple-500 to-blue-500 text-white">
                                Step {currentStep + 1} of {practice.tts_instructions.length}
                              </Badge>
                            </motion.div>

                            {/* Large Icon */}
                            <motion.div
                              animate={{
                                scale: isSpeaking ? [1, 1.1, 1] : 1,
                                rotate: isSpeaking ? [0, 5, -5, 0] : 0
                              }}
                              transition={{
                                duration: 2,
                                repeat: isSpeaking ? Infinity : 0
                              }}
                              className="text-9xl mb-6 filter drop-shadow-lg"
                            >
                              {practice.icon}
                            </motion.div>

                            {/* Duration Display */}
                            {practice.steps && practice.steps[currentStep]?.duration_text && (
                              <motion.div
                                initial={{ opacity: 0 }}
                                animate={{ opacity: 1 }}
                                transition={{ delay: 0.3 }}
                                className="flex items-center justify-center gap-2 text-purple-600 mb-4"
                              >
                                <Clock className="w-5 h-5" />
                                <span className="text-lg font-semibold">
                                  {practice.steps[currentStep].duration_text}
                                </span>
                              </motion.div>
                            )}

                            {/* Current Instruction */}
                            <motion.div
                              initial={{ opacity: 0 }}
                              animate={{ opacity: 1 }}
                              transition={{ delay: 0.4 }}
                              className="bg-white/80 backdrop-blur-sm rounded-xl p-6 shadow-md border-2 border-purple-300/50"
                            >
                              <p className="text-xl text-gray-800 leading-relaxed font-medium">
                                {practice.steps ? practice.steps[currentStep]?.instruction : practice.tts_instructions[currentStep].replace(/for \d+ \w+$/, '')}
                              </p>
                            </motion.div>
                          </motion.div>
                        </AnimatePresence>
                      </div>
                    </div>

                    {/* Auto-advance indicator with countdown */}
                    {isPracticing && (
                      <motion.div
                        initial={{ opacity: 0, scale: 0.9 }}
                        animate={{ opacity: 1, scale: 1 }}
                        exit={{ opacity: 0, scale: 0.9 }}
                        className="flex items-center justify-center gap-3 mb-6 bg-gradient-to-r from-purple-500/10 to-blue-500/10 rounded-xl p-4 border border-purple-300/30"
                      >
                        <motion.div
                          animate={{ scale: [1, 1.2, 1] }}
                          transition={{ duration: 1.5, repeat: Infinity }}
                        >
                          <Activity className="w-5 h-5 text-purple-600" />
                        </motion.div>
                        <div className="text-center">
                          <p className="text-sm font-semibold text-purple-700">
                            {isSpeaking ? '🔊 Listening to instruction...' : `⏳ Practicing step... ${stepCountdown}s remaining`}
                          </p>
                          <p className="text-xs text-purple-600 mt-1">
                            {isSpeaking ? 'Get ready...' : 'Auto-advancing when complete'}
                          </p>
                        </div>
                      </motion.div>
                    )}

                    {/* Controls */}
                    <div className="flex gap-4">
                      {!isPracticing ? (
                        <>
                          <Button
                            onClick={resumePractice}
                            className="flex-1"
                            size="lg"
                          >
                            <Play className="w-5 h-5 mr-2" />
                            {currentStep === 0 ? 'Start' : 'Resume'}
                          </Button>
                          <Button
                            onClick={resetPractice}
                            variant="outline"
                            size="lg"
                          >
                            <RotateCcw className="w-5 h-5" />
                          </Button>
                        </>
                      ) : (
                        <>
                          <Button
                            onClick={pausePractice}
                            className="flex-1"
                            size="lg"
                            variant="secondary"
                          >
                            <Pause className="w-5 h-5 mr-2" />
                            Pause
                          </Button>
                          <Button
                            onClick={toggleSpeech}
                            variant="outline"
                            size="lg"
                          >
                            {isSpeaking ? (
                              <VolumeX className="w-5 h-5" />
                            ) : (
                              <Volume2 className="w-5 h-5" />
                            )}
                          </Button>
                        </>
                      )}
                    </div>

                    {/* Progress */}
                    <div className="mt-6">
                      <div className="flex justify-between text-sm text-gray-600 mb-2">
                        <span>Progress</span>
                        <span>{Math.round(((currentStep + 1) / practice.tts_instructions.length) * 100)}%</span>
                      </div>
                      <div className="w-full bg-gray-200 rounded-full h-2">
                        <motion.div
                          className="bg-purple-600 h-2 rounded-full"
                          initial={{ width: 0 }}
                          animate={{ width: `${((currentStep + 1) / practice.tts_instructions.length) * 100}%` }}
                          transition={{ duration: 0.5 }}
                        />
                      </div>
                    </div>
                  </CardContent>
                </Card>
              ) : (
                <Card>
                  <CardHeader>
                    <CardTitle className="text-center">🎉 Practice Complete!</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="text-center space-y-6">
                      <div>
                        <div className="text-5xl mb-4">✨</div>
                        <p className="text-2xl font-semibold text-gray-800">
                          Great job on completing {practice.practice_name}!
                        </p>
                        <p className="text-gray-600 mt-2">
                          Duration: {formatTime(elapsedTime)}
                        </p>
                      </div>

                      <div className="bg-purple-50 rounded-lg p-6">
                        <p className="text-lg font-semibold mb-4">How was your practice?</p>
                        <div className="flex justify-center gap-2">
                          {[1, 2, 3, 4, 5].map((rating) => (
                            <button
                              key={rating}
                              onClick={() => setSatisfactionRating(rating)}
                              className="transition-transform hover:scale-110"
                              aria-label={`Rate ${rating} stars`}
                            >
                              <Star
                                className={`w-10 h-10 ${rating <= satisfactionRating
                                    ? 'fill-yellow-400 text-yellow-400'
                                    : 'text-gray-300'
                                  }`}
                              />
                            </button>
                          ))}
                        </div>
                      </div>

                      <Button
                        onClick={submitCompletion}
                        disabled={satisfactionRating === 0}
                        className="w-full"
                        size="lg"
                      >
                        <CheckCircle2 className="w-5 h-5 mr-2" />
                        Complete & Track Progress
                      </Button>

                      <div className="flex items-center justify-center gap-2 text-sm text-gray-600">
                        <TrendingUp className="w-4 h-4" />
                        This will be added to your wellness score!
                      </div>
                    </div>
                  </CardContent>
                </Card>
              )}
            </motion.div>
          )}
        </AnimatePresence>
      </div>
    </div>
  );
}
