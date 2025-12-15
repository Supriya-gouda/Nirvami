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
  const speechSynthesisRef = useRef<SpeechSynthesisUtterance | null>(null);
  const timerRef = useRef<NodeJS.Timeout | null>(null);

  useEffect(() => {
    loadPracticeContent();
    return () => {
      // Cleanup
      stopSpeech();
      if (timerRef.current) clearInterval(timerRef.current);
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
      const dynamicPractice: PracticeContent = {
        practice_type: recommendation.category || 'lifestyle',
        practice_name: recommendation.title,
        description: recommendation.content,
        benefits: extractBenefitsFromContent(recommendation.content),
        difficulty: 'beginner',
        duration_min: 5,
        duration_max: 15,
        tts_instructions: splitIntoInstructions(recommendation.content),
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

  // Helper function to split content into TTS instructions
  const splitIntoInstructions = (content: string): string[] => {
    // Split by sentences and filter
    const instructions = content
      .split(/[.!?]+/)
      .map(s => s.trim())
      .filter(s => s.length > 20 && s.length < 200);
    
    return instructions.length > 0 ? instructions : [content];
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
  };

  const resumePractice = () => {
    setIsPracticing(true);
    speakInstruction(currentStep);
  };

  const resetPractice = () => {
    setIsPracticing(false);
    setCurrentStep(0);
    setElapsedTime(0);
    setPracticeStartTime(null);
    stopSpeech();
  };

  const nextStep = () => {
    if (!practice) return;
    
    stopSpeech();
    
    if (currentStep < practice.tts_instructions.length - 1) {
      const next = currentStep + 1;
      setCurrentStep(next);
      speakInstruction(next);
    } else {
      // Completed all steps
      completePractice();
    }
  };

  const speakInstruction = (stepIndex: number) => {
    if (!practice || stepIndex >= practice.tts_instructions.length) return;

    stopSpeech();

    const utterance = new SpeechSynthesisUtterance(practice.tts_instructions[stepIndex]);
    utterance.rate = 0.9; // Slightly slower for clarity
    utterance.pitch = 1.0;
    utterance.volume = 1.0;

    utterance.onstart = () => setIsSpeaking(true);
    utterance.onend = () => {
      setIsSpeaking(false);
      // Auto-advance to next step after speaking (with 2 second pause)
      if (isPracticing) {
        setTimeout(() => {
          if (stepIndex < practice.tts_instructions.length - 1) {
            nextStep();
          }
        }, 2000);
      }
    };
    utterance.onerror = () => setIsSpeaking(false);

    speechSynthesisRef.current = utterance;
    window.speechSynthesis.speak(utterance);
  };

  const stopSpeech = () => {
    window.speechSynthesis.cancel();
    setIsSpeaking(false);
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

                  <div className="space-y-4">
                    <h3 className="text-lg font-semibold">
                      {hasEnhancedContent ? 'Step-by-Step Instructions' : 'How to Practice'}
                    </h3>
                    <ol className="list-decimal list-inside space-y-2">
                      {practice.tts_instructions.map((instruction, index) => (
                        <li key={index} className="text-gray-700">{instruction}</li>
                      ))}
                    </ol>
                  </div>

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
                          {formatTime(elapsedTime)}
                        </div>
                      </div>
                    </div>
                  </CardHeader>
                  <CardContent>
                    {/* Avatar Display */}
                    <div className="bg-gradient-to-br from-purple-100 to-blue-100 rounded-lg p-8 mb-6 min-h-[300px] flex items-center justify-center">
                      <motion.div
                        key={currentStep}
                        initial={{ scale: 0.8, opacity: 0 }}
                        animate={{ scale: 1, opacity: 1 }}
                        transition={{ duration: 0.5 }}
                        className="text-center"
                      >
                        <div className="text-8xl mb-4">{practice.icon}</div>
                        <p className="text-xl font-semibold text-gray-800">
                          Step {currentStep + 1} of {practice.tts_instructions.length}
                        </p>
                      </motion.div>
                    </div>

                    {/* Current Instruction */}
                    <div className="bg-white border-2 border-purple-200 rounded-lg p-6 mb-6">
                      <p className="text-lg text-gray-800 leading-relaxed">
                        {practice.tts_instructions[currentStep]}
                      </p>
                    </div>

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
                          <Button
                            onClick={nextStep}
                            variant="outline"
                            size="lg"
                          >
                            Next
                          </Button>
                        </>
                      )}
                    </div>

                    {/* Progress */}
                    <div className="mt-6">
                      <div className="flex justify-between text-sm text-gray-600 mb-2">
                        <span>Progress</span>
                        <span>{Math.round((currentStep / practice.tts_instructions.length) * 100)}%</span>
                      </div>
                      <div className="w-full bg-gray-200 rounded-full h-2">
                        <motion.div
                          className="bg-purple-600 h-2 rounded-full"
                          initial={{ width: 0 }}
                          animate={{ width: `${(currentStep / practice.tts_instructions.length) * 100}%` }}
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
                                className={`w-10 h-10 ${
                                  rating <= satisfactionRating
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
