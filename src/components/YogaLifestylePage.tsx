import { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'motion/react';
import { Camera, Video, Play, Pause, Wind, Music, Volume2, Sparkles } from 'lucide-react';
import { Navigation } from './Navigation';
import { Button } from './ui/button';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogDescription } from './ui/dialog';
import { Badge } from './ui/badge';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from './ui/select';
import { Slider } from './ui/slider';
import type { PageType } from '../App';
import type { User } from '../types/api.types';
import api from '../services/api';
import type { WearableData } from '../types/api.types';

interface YogaLifestylePageProps {
  user: User | null;
  onNavigate: (page: PageType) => void;
  onLogout?: () => void;
  onOpenNotifications?: () => void;
}

interface YogaPose {
  id: string;
  name: string;
  sanskritName: string;
  duration: string;
  difficulty: 'Beginner' | 'Intermediate' | 'Advanced';
  benefits: string[];
  icon: string;
}

interface SoundTrack {
  id: string;
  title: string;
  duration: string;
  dosha: 'Vata' | 'Pitta' | 'Kapha';
  mood: string[];
  frequency: string;
  description: string;
  icon: string;
  gradient: string;
}

export function YogaLifestylePage({ user, onNavigate, onLogout, onOpenNotifications }: YogaLifestylePageProps) {
  const [showCamera, setShowCamera] = useState(false);
  const [selectedPose, setSelectedPose] = useState<YogaPose | null>(null);
  const [cameraFeedback, setCameraFeedback] = useState('');
  const [isPranayamaActive, setIsPranayamaActive] = useState(false);
  const [breathPhase, setBreathPhase] = useState<'inhale' | 'hold' | 'exhale'>('inhale');
  const [selectedMood, setSelectedMood] = useState<string>('none');
  const [playingTrack, setPlayingTrack] = useState<string | null>(null);
  const [volume, setVolume] = useState([70]);
  const [wearableData, setWearableData] = useState<WearableData | null>(null);
  const [currentUserDosha, setCurrentUserDosha] = useState<'Vata' | 'Pitta' | 'Kapha'>('Vata');

  // Fetch latest wearable data and dosha on mount
  useEffect(() => {
    const loadData = async () => {
      try {
        const [wearable, doshaData] = await Promise.all([
          api.getLatestWearable(),
          api.getCurrentDosha()
        ]);
        setWearableData(wearable);

        // Set user's dominant dosha
        if (doshaData?.dominant_dosha) {
          const dominantDosha = doshaData.dominant_dosha.charAt(0).toUpperCase() + doshaData.dominant_dosha.slice(1);
          setCurrentUserDosha(dominantDosha as 'Vata' | 'Pitta' | 'Kapha');
        }
      } catch (err) {
        console.warn('Failed to load user data', err);
      }
    };

    loadData();
  }, []);

  const yogaPoses: YogaPose[] = [
    {
      id: '1',
      name: 'Mountain Pose',
      sanskritName: 'Tadasana',
      duration: '1-2 min',
      difficulty: 'Beginner',
      benefits: ['Improves posture', 'Grounds Vata', 'Builds focus'],
      icon: '🧘',
    },
    {
      id: '2',
      name: 'Tree Pose',
      sanskritName: 'Vrksasana',
      duration: '30-60 sec',
      difficulty: 'Beginner',
      benefits: ['Improves balance', 'Strengthens legs', 'Calms mind'],
      icon: '🌳',
    },
    {
      id: '3',
      name: 'Warrior II',
      sanskritName: 'Virabhadrasana II',
      duration: '30-60 sec',
      difficulty: 'Intermediate',
      benefits: ['Builds strength', 'Increases stamina', 'Opens hips'],
      icon: '⚔️',
    },
    {
      id: '4',
      name: 'Child\'s Pose',
      sanskritName: 'Balasana',
      duration: '1-3 min',
      difficulty: 'Beginner',
      benefits: ['Releases tension', 'Calms nervous system', 'Gentle stretch'],
      icon: '🙏',
    },
    {
      id: '5',
      name: 'Downward Dog',
      sanskritName: 'Adho Mukha Svanasana',
      duration: '1-3 min',
      difficulty: 'Intermediate',
      benefits: ['Full body stretch', 'Energizes', 'Strengthens'],
      icon: '🐕',
    },
    {
      id: '6',
      name: 'Corpse Pose',
      sanskritName: 'Savasana',
      duration: '5-10 min',
      difficulty: 'Beginner',
      benefits: ['Deep relaxation', 'Reduces stress', 'Integrates practice'],
      icon: '😌',
    },
  ];

  const soundTracks: SoundTrack[] = [
    {
      id: '1',
      title: 'Ocean Waves & Tibetan Bowls',
      duration: '15:00',
      dosha: 'Vata',
      mood: ['anxious', 'stressed', 'restless'],
      frequency: '432 Hz',
      description: 'Grounding frequencies to calm Vata imbalance',
      icon: '🌊',
      gradient: 'from-blue-50 to-cyan-50',
    },
    {
      id: '2',
      title: 'Forest Rain & Flute',
      duration: '20:00',
      dosha: 'Pitta',
      mood: ['angry', 'frustrated', 'irritated'],
      frequency: '528 Hz',
      description: 'Cooling sounds to balance Pitta fire',
      icon: '🌧️',
      gradient: 'from-green-50 to-emerald-50',
    },
    {
      id: '3',
      title: 'Energizing Drum Rhythms',
      duration: '12:00',
      dosha: 'Kapha',
      mood: ['tired', 'lethargic', 'unmotivated'],
      frequency: '639 Hz',
      description: 'Uplifting beats to stimulate Kapha energy',
      icon: '🥁',
      gradient: 'from-orange-50 to-red-50',
    },
    {
      id: '4',
      title: 'Himalayan Singing Bowls',
      duration: '30:00',
      dosha: 'Vata',
      mood: ['calm', 'meditative', 'peaceful'],
      frequency: '528 Hz',
      description: 'Universal healing frequency for balance',
      icon: '🔮',
      gradient: 'from-purple-50 to-pink-50',
    },
    {
      id: '5',
      title: 'Morning Sunrise Ragas',
      duration: '18:00',
      dosha: 'Kapha',
      mood: ['energized', 'motivated', 'uplifted'],
      frequency: '396 Hz',
      description: 'Traditional ragas to enhance vitality',
      icon: '🎵',
      gradient: 'from-amber-50 to-yellow-50',
    },
    {
      id: '6',
      title: 'Moonlight Serenity',
      duration: '25:00',
      dosha: 'Pitta',
      mood: ['calm', 'relaxed', 'peaceful'],
      frequency: '174 Hz',
      description: 'Gentle evening sounds for deep rest',
      icon: '🌙',
      gradient: 'from-indigo-50 to-blue-50',
    },
  ];

  const moods = [
    { value: 'none', label: 'None', emoji: '—' },
    { value: 'calm', label: 'Calm', emoji: '😌' },
    { value: 'anxious', label: 'Anxious', emoji: '😰' },
    { value: 'angry', label: 'Angry', emoji: '😤' },
    { value: 'tired', label: 'Tired', emoji: '😴' },
    { value: 'stressed', label: 'Stressed', emoji: '😫' },
    { value: 'energized', label: 'Energized', emoji: '⚡' },
    { value: 'peaceful', label: 'Peaceful', emoji: '☮️' },
    { value: 'frustrated', label: 'Frustrated', emoji: '😣' },
  ];

  const filteredTracks = selectedMood === 'none'
    ? []
    : soundTracks.filter(track => track.dosha === currentUserDosha && track.mood.includes(selectedMood));

  const recommendedTracks = filteredTracks;

  const togglePlay = (trackId: string) => {
    setPlayingTrack(playingTrack === trackId ? null : trackId);
  };

  const dinacharya = [
    { time: '6:00 AM', activity: 'Wake up & tongue scraping', icon: '🌅' },
    { time: '6:15 AM', activity: 'Oil pulling & meditation', icon: '🧘‍♀️' },
    { time: '7:00 AM', activity: 'Yoga practice', icon: '🤸' },
    { time: '8:00 AM', activity: 'Healthy breakfast', icon: '🥗' },
    { time: '12:00 PM', activity: 'Midday meal', icon: '🍲' },
    { time: '6:00 PM', activity: 'Light dinner', icon: '🥙' },
    { time: '9:00 PM', activity: 'Evening relaxation', icon: '📖' },
    { time: '10:00 PM', activity: 'Sleep preparation', icon: '🌙' },
  ];

  const handleCameraStart = (pose: YogaPose) => {
    setSelectedPose(pose);
    setShowCamera(true);

    // Simulate pose detection feedback
    setTimeout(() => {
      setCameraFeedback('Good alignment! Try to straighten your back a bit more.');
    }, 3000);
  };

  const startPranayama = () => {
    setIsPranayamaActive(true);
    let phase: 'inhale' | 'hold' | 'exhale' = 'inhale';

    const breathingCycle = setInterval(() => {
      if (phase === 'inhale') {
        setBreathPhase('hold');
        phase = 'hold';
      } else if (phase === 'hold') {
        setBreathPhase('exhale');
        phase = 'exhale';
      } else {
        setBreathPhase('inhale');
        phase = 'inhale';
      }
    }, 4000);

    // Store interval ID for cleanup
    (window as any).breathingInterval = breathingCycle;
  };

  const stopPranayama = () => {
    setIsPranayamaActive(false);
    if ((window as any).breathingInterval) {
      clearInterval((window as any).breathingInterval);
    }
  };

  return (
    <div className="min-h-screen">
      <Navigation currentPage="yoga" onNavigate={onNavigate} onLogout={onLogout} user={user} onOpenNotifications={onOpenNotifications} />

      <div className="max-w-7xl mx-auto p-8">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="mb-8"
        >
          <h1 className="mb-2">Yoga & Lifestyle</h1>
          <p className="text-gray-600">Personalized practices for mind-body balance</p>
        </motion.div>

        <div className="grid md:grid-cols-3 gap-6 mb-8">
          {/* Today's Yoga Plan */}
          <motion.div
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: 0.1 }}
            className="md:col-span-2"
          >
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Play className="w-5 h-5 text-purple-600" />
                  Today's Yoga Plan
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="grid md:grid-cols-2 gap-4">
                  {yogaPoses.map((pose, index) => (
                    <motion.div
                      key={pose.id}
                      initial={{ opacity: 0, y: 20 }}
                      animate={{ opacity: 1, y: 0 }}
                      transition={{ delay: 0.2 + index * 0.1 }}
                      whileHover={{ scale: 1.02 }}
                      className="p-4 rounded-xl bg-gradient-to-br from-purple-50 to-blue-50 border border-purple-100"
                    >
                      <div className="flex items-start gap-3 mb-3">
                        <span className="text-3xl">{pose.icon}</span>
                        <div className="flex-1">
                          <h3 className="text-purple-900">{pose.name}</h3>
                          <p className="text-sm text-gray-600">{pose.sanskritName}</p>
                        </div>
                        <Badge variant="outline">{pose.difficulty}</Badge>
                      </div>

                      <div className="space-y-2 mb-3">
                        <p className="text-sm text-gray-600">⏱️ {pose.duration}</p>
                        <div className="text-xs text-gray-500 space-y-1">
                          {pose.benefits.map((benefit, i) => (
                            <div key={i}>• {benefit}</div>
                          ))}
                        </div>
                      </div>

                      <Button
                        onClick={() => handleCameraStart(pose)}
                        variant="outline"
                        size="sm"
                        className="w-full"
                      >
                        <Camera className="w-4 h-4 mr-2" />
                        Practice with Camera
                      </Button>
                    </motion.div>
                  ))}
                </div>
              </CardContent>
            </Card>
          </motion.div>

          {/* Pranayama Guide */}
          <motion.div
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: 0.2 }}
          >
            <Card className="h-full">
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Wind className="w-5 h-5 text-blue-600" />
                  Pranayama Guide
                </CardTitle>
              </CardHeader>
              <CardContent className="flex flex-col h-full">
                <p className="text-sm text-gray-600 mb-6">
                  Interactive breathing exercise to balance your doshas
                </p>

                <div className="flex-1 flex items-center justify-center mb-6">
                  <motion.div
                    className={`w-40 h-40 rounded-full flex items-center justify-center ${isPranayamaActive
                        ? 'bg-gradient-to-br from-blue-400 to-purple-400'
                        : 'bg-gradient-to-br from-gray-200 to-gray-300'
                      }`}
                    animate={
                      isPranayamaActive
                        ? {
                          scale: breathPhase === 'inhale' ? [1, 1.3] : breathPhase === 'exhale' ? [1.3, 1] : 1.3,
                          opacity: breathPhase === 'hold' ? [1, 0.7, 1] : 1,
                        }
                        : {}
                    }
                    transition={{ duration: 4, ease: "easeInOut" }}
                  >
                    <span className="text-white text-xl capitalize">
                      {isPranayamaActive ? breathPhase : 'Start'}
                    </span>
                  </motion.div>
                </div>

                {isPranayamaActive && (
                  <motion.div
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    className="text-center mb-4"
                  >
                    <p className="text-sm text-gray-600">
                      {breathPhase === 'inhale' && 'Breathe in slowly...'}
                      {breathPhase === 'hold' && 'Hold your breath...'}
                      {breathPhase === 'exhale' && 'Breathe out gently...'}
                    </p>
                  </motion.div>
                )}

                <Button
                  onClick={isPranayamaActive ? stopPranayama : startPranayama}
                  className={`w-full ${isPranayamaActive ? 'bg-red-500 hover:bg-red-600' : 'bg-blue-500 hover:bg-blue-600'}`}
                >
                  {isPranayamaActive ? (
                    <>
                      <Pause className="w-4 h-4 mr-2" />
                      Stop Practice
                    </>
                  ) : (
                    <>
                      <Play className="w-4 h-4 mr-2" />
                      Start Pranayama
                    </>
                  )}
                </Button>
              </CardContent>
            </Card>
          </motion.div>
        </div>

        {/* Dinacharya - Daily Routine */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.3 }}
        >
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Music className="w-5 h-5 text-purple-600" />
                AI Sound Therapy - Personalized for {currentUserDosha} Dosha
              </CardTitle>
            </CardHeader>
            <CardContent>
              {/* Mood Selection */}
              <div className="mb-6">
                <label className="text-sm text-gray-700 mb-2 block">How are you feeling right now?</label>
                <Select value={selectedMood} onValueChange={setSelectedMood}>
                  <SelectTrigger className="w-full md:w-64">
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    {moods.map(mood => (
                      <SelectItem key={mood.value} value={mood.value}>
                        {mood.emoji} {mood.label}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>

              {/* AI Recommendation Badge */}
              {selectedMood !== 'none' && (
                <div className="mb-4 p-3 rounded-lg bg-gradient-to-r from-purple-50 to-pink-50 border border-purple-100">
                  <div className="flex items-center gap-2">
                    <Sparkles className="w-4 h-4 text-purple-600" />
                    <p className="text-sm text-purple-900">
                      AI recommended {recommendedTracks.length} healing sound{recommendedTracks.length !== 1 ? 's' : ''} based on your mood and dosha
                    </p>
                  </div>
                </div>
              )}

              {/* Sound Tracks */}
              <div className="grid md:grid-cols-2 gap-4">
                {recommendedTracks.map((track, index) => {
                  const isPlaying = playingTrack === track.id;

                  return (
                    <motion.div
                      key={track.id}
                      initial={{ opacity: 0, y: 20 }}
                      animate={{ opacity: 1, y: 0 }}
                      transition={{ delay: 0.4 + index * 0.1 }}
                      className={`p-4 rounded-xl bg-gradient-to-br ${track.gradient} border border-purple-100 ${isPlaying ? 'ring-2 ring-purple-400' : ''}`}
                    >
                      <div className="flex items-start gap-3 mb-3">
                        <div className="text-3xl">{track.icon}</div>
                        <div className="flex-1">
                          <h3 className="text-gray-900 mb-1">{track.title}</h3>
                          <div className="flex items-center gap-2 flex-wrap">
                            <Badge variant="outline" className="text-xs">
                              {track.dosha}
                            </Badge>
                            <Badge variant="outline" className="text-xs">
                              {track.frequency}
                            </Badge>
                            <span className="text-xs text-gray-600">{track.duration}</span>
                          </div>
                        </div>
                      </div>

                      <p className="text-sm text-gray-700 mb-4">{track.description}</p>

                      {/* Controls */}
                      <div className="space-y-3">
                        <Button
                          onClick={() => togglePlay(track.id)}
                          size="sm"
                          className={`w-full ${isPlaying
                              ? 'bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-700 hover:to-pink-700'
                              : 'bg-gradient-to-r from-purple-500 to-pink-500 hover:from-purple-600 hover:to-pink-600'
                            } text-white`}
                        >
                          {isPlaying ? (
                            <>
                              <Pause className="w-4 h-4 mr-1" />
                              Pause
                            </>
                          ) : (
                            <>
                              <Play className="w-4 h-4 mr-1" />
                              Play
                            </>
                          )}
                        </Button>

                        {/* Volume Control */}
                        {isPlaying && (
                          <motion.div
                            initial={{ opacity: 0, height: 0 }}
                            animate={{ opacity: 1, height: 'auto' }}
                            exit={{ opacity: 0, height: 0 }}
                            className="flex items-center gap-2"
                          >
                            <Volume2 className="w-4 h-4 text-gray-600" />
                            <Slider
                              value={volume}
                              onValueChange={setVolume}
                              max={100}
                              step={1}
                              className="flex-1"
                            />
                            <span className="text-xs text-gray-600 w-8">{volume[0]}%</span>
                          </motion.div>
                        )}

                        {/* Playing Animation */}
                        {isPlaying && (
                          <div className="flex items-center gap-1 h-8">
                            {[...Array(15)].map((_, i) => (
                              <motion.div
                                key={i}
                                className="flex-1 bg-gradient-to-t from-purple-400 to-pink-400 rounded-full"
                                animate={{
                                  height: ['20%', '100%', '20%'],
                                }}
                                transition={{
                                  duration: 0.5 + Math.random() * 0.5,
                                  repeat: Infinity,
                                  ease: 'easeInOut',
                                }}
                              />
                            ))}
                          </div>
                        )}
                      </div>
                    </motion.div>
                  );
                })}
              </div>

              {/* No Results Message */}
              {recommendedTracks.length === 0 && (
                <div className="text-center py-8">
                  <p className="text-gray-600">Please select a mood to receive personalized sound therapy recommendations.</p>
                </div>
              )}
            </CardContent>
          </Card>
        </motion.div>
      </div>

      {/* Camera Dialog */}
      <Dialog open={showCamera} onOpenChange={setShowCamera}>
        <DialogContent className="max-w-4xl">
          <DialogHeader>
            <DialogTitle>Practice: {selectedPose?.name}</DialogTitle>
            <DialogDescription>{selectedPose?.sanskritName}</DialogDescription>
          </DialogHeader>
          <div className="space-y-4">
            {/* Simulated Camera Feed */}
            <div className="aspect-video bg-gradient-to-br from-gray-800 to-gray-900 rounded-lg flex items-center justify-center relative overflow-hidden">
              <motion.div
                className="absolute inset-0 bg-blue-500/20"
                animate={{ opacity: [0.2, 0.5, 0.2] }}
                transition={{ duration: 2, repeat: Infinity }}
              />
              <div className="text-white text-center z-10">
                <Camera className="w-16 h-16 mx-auto mb-4" />
                <p>Camera feed would appear here</p>
                <p className="text-sm text-gray-300 mt-2">Pose detection active...</p>
              </div>

              {/* Skeleton overlay simulation */}
              <motion.div
                className="absolute inset-0 flex items-center justify-center"
                initial={{ opacity: 0 }}
                animate={{ opacity: cameraFeedback ? 0.8 : 0 }}
              >
                <div className="w-32 h-64 border-4 border-green-400 rounded-full" />
              </motion.div>
            </div>

            {/* Feedback */}
            <AnimatePresence>
              {cameraFeedback && (
                <motion.div
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  exit={{ opacity: 0, y: -20 }}
                  className="p-4 bg-green-50 border border-green-200 rounded-lg"
                >
                  <p className="text-green-900">✓ {cameraFeedback}</p>
                </motion.div>
              )}
            </AnimatePresence>

            <div className="flex gap-2">
              <Button variant="outline" onClick={() => setShowCamera(false)} className="flex-1">
                End Practice
              </Button>
              <Button className="flex-1">
                <Video className="w-4 h-4 mr-2" />
                Record Session
              </Button>
            </div>
          </div>
        </DialogContent>
      </Dialog>
    </div>
  );
}