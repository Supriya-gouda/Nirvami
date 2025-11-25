import { useState, useEffect } from 'react';
import { Music, Play, Pause, Volume2, Sparkles, Wind, Heart, Zap } from 'lucide-react';
import { Navigation } from './Navigation';
import { Button } from './ui/button';
import { Badge } from './ui/badge';
import { Slider } from './ui/slider';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from './ui/select';
import api from '../services/api';
import type { PageType, User } from '../App';

interface SoundTherapyPageProps {
  user: User | null;
  onNavigate: (page: PageType) => void;
}

interface SoundTrack {
  id: string;
  title: string;
  duration: string;
  dosha: 'Vata' | 'Pitta' | 'Kapha' | 'All';
  mood: string[];
  frequency: string;
  description: string;
  icon: string;
  gradient: string;
}

export function SoundTherapyPage({ user, onNavigate }: SoundTherapyPageProps) {
  const [selectedDosha, setSelectedDosha] = useState<'Vata' | 'Pitta' | 'Kapha' | 'All'>('All');
  const [selectedMood, setSelectedMood] = useState<string>('calm');
  const [playingTrack, setPlayingTrack] = useState<string | null>(null);
  const [volume, setVolume] = useState([70]);
  const [soundTracks, setSoundTracks] = useState<SoundTrack[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  // Fetch sound tracks on mount and when dosha changes
  useEffect(() => {
    const loadSoundTracks = async () => {
      setIsLoading(true);
      try {
        // Fetch from API
        const doshaFilter = selectedDosha === 'All' ? undefined : selectedDosha.toLowerCase();
        const response = await api.getSoundTracks({ dosha: doshaFilter }).catch(() => ({ success: false, tracks: [] }));
        
        if (response.success && response.tracks && response.tracks.length > 0) {
          // Transform database tracks to component format
          const transformedTracks = response.tracks.map((track: any) => ({
            id: track.id,
            title: track.title,
            duration: `${track.duration_minutes}:00`,
            dosha: selectedDosha,
            mood: track.emotion_tags || [],
            frequency: track.frequency_hz ? `${track.frequency_hz} Hz` : '432 Hz',
            description: track.description || '',
            icon: track.icon || '🎵',
            gradient: track.thumbnail_gradient || 'from-purple-400 to-pink-400',
          }));
          setSoundTracks(transformedTracks);
        } else {
          // Fallback to hardcoded tracks if API returns empty
          setSoundTracks(getDefaultSoundTracks());
        }
      } catch (err) {
        console.warn('Failed to load sound tracks from API, using fallback', err);
        setSoundTracks(getDefaultSoundTracks());
      } finally {
        setIsLoading(false);
      }
    };

    loadSoundTracks();
  }, [selectedDosha]);

  // Fallback data function
  const getDefaultSoundTracks = (): SoundTrack[] => [
    {
      id: '1',
      title: 'Ocean Waves & Tibetan Bowls',
      duration: '15:00',
      dosha: 'Vata',
      mood: ['anxious', 'stressed', 'restless'],
      frequency: '432 Hz',
      description: 'Grounding frequencies to calm Vata imbalance and reduce anxiety',
      icon: '🌊',
      gradient: 'from-blue-400 to-cyan-400'
    },
    {
      id: '2',
      title: 'Forest Rain & Flute Meditation',
      duration: '20:00',
      dosha: 'Pitta',
      mood: ['angry', 'frustrated', 'irritated'],
      frequency: '528 Hz',
      description: 'Cooling sounds to balance Pitta fire and promote emotional release',
      icon: '🌧️',
      gradient: 'from-green-400 to-emerald-400'
    },
    {
      id: '3',
      title: 'Energizing Drum Rhythms',
      duration: '12:00',
      dosha: 'Kapha',
      mood: ['tired', 'lethargic', 'unmotivated'],
      frequency: '639 Hz',
      description: 'Uplifting beats to stimulate Kapha energy and boost motivation',
      icon: '🥁',
      gradient: 'from-orange-400 to-red-400'
    },
    {
      id: '4',
      title: 'Himalayan Crystal Singing Bowls',
      duration: '30:00',
      dosha: 'All',
      mood: ['calm', 'meditative', 'balanced'],
      frequency: '528 Hz',
      description: 'Universal healing frequency for overall balance and chakra alignment',
      icon: '🔮',
      gradient: 'from-purple-400 to-pink-400'
    },
    {
      id: '5',
      title: 'Sunrise Ragas - Classical Indian',
      duration: '18:00',
      dosha: 'Vata',
      mood: ['anxious', 'scattered', 'confused'],
      frequency: '396 Hz',
      description: 'Traditional morning ragas to ground energy and enhance clarity',
      icon: '🎵',
      gradient: 'from-amber-400 to-orange-400'
    },
    {
      id: '6',
      title: 'Moonlight Serenity - Nature Sounds',
      duration: '25:00',
      dosha: 'Pitta',
      mood: ['angry', 'stressed', 'overwhelmed'],
      frequency: '174 Hz',
      description: 'Gentle evening sounds to cool inflammation and promote deep rest',
      icon: '🌙',
      gradient: 'from-indigo-400 to-blue-400'
    },
    {
      id: '7',
      title: 'Morning Sun Mantras',
      duration: '10:00',
      dosha: 'Kapha',
      mood: ['tired', 'sluggish', 'low energy'],
      frequency: '852 Hz',
      description: 'Powerful Sanskrit chants to awaken vitality and clear stagnation',
      icon: '☀️',
      gradient: 'from-yellow-400 to-orange-400'
    },
    {
      id: '8',
      title: 'Heart Chakra Meditation',
      duration: '22:00',
      dosha: 'All',
      mood: ['sad', 'lonely', 'heartbroken'],
      frequency: '639 Hz',
      description: 'Loving frequencies to heal emotional wounds and open the heart',
      icon: '💚',
      gradient: 'from-pink-400 to-rose-400'
    },
    {
      id: '9',
      title: 'Bamboo Forest Wind Chimes',
      duration: '16:00',
      dosha: 'Vata',
      mood: ['restless', 'anxious', 'insecure'],
      frequency: '432 Hz',
      description: 'Gentle harmonics to settle nervous system and restore peace',
      icon: '🎐',
      gradient: 'from-teal-400 to-cyan-400'
    },
    {
      id: '10',
      title: 'Fire Ceremony Drums',
      duration: '14:00',
      dosha: 'Kapha',
      mood: ['unmotivated', 'depressed', 'stuck'],
      frequency: '741 Hz',
      description: 'Rhythmic activation to break through mental fog and ignite passion',
      icon: '🔥',
      gradient: 'from-red-400 to-pink-400'
    },
    {
      id: '11',
      title: 'Garden of Tranquility',
      duration: '28:00',
      dosha: 'Pitta',
      mood: ['frustrated', 'irritated', 'tense'],
      frequency: '528 Hz',
      description: 'Soft nature soundscape to dissolve tension and restore harmony',
      icon: '🌸',
      gradient: 'from-green-400 to-lime-400'
    },
    {
      id: '12',
      title: 'Quantum Healing Frequencies',
      duration: '20:00',
      dosha: 'All',
      mood: ['balanced', 'mindful', 'grateful'],
      frequency: '963 Hz',
      description: 'Highest healing frequency for spiritual connection and enlightenment',
      icon: '✨',
      gradient: 'from-violet-400 to-purple-400'
    },
  ];

  const moods = [
    { value: 'calm', label: 'Calm', emoji: '😌' },
    { value: 'anxious', label: 'Anxious', emoji: '😰' },
    { value: 'angry', label: 'Angry', emoji: '😤' },
    { value: 'tired', label: 'Tired', emoji: '😴' },
    { value: 'stressed', label: 'Stressed', emoji: '😫' },
    { value: 'happy', label: 'Happy', emoji: '😊' },
    { value: 'sad', label: 'Sad', emoji: '😢' },
    { value: 'energized', label: 'Energized', emoji: '⚡' },
  ];

  const doshaIcons = {
    Vata: { icon: Wind, color: 'text-blue-600', bg: 'from-blue-100 to-cyan-100' },
    Pitta: { icon: Zap, color: 'text-orange-600', bg: 'from-orange-100 to-red-100' },
    Kapha: { icon: Heart, color: 'text-green-600', bg: 'from-green-100 to-emerald-100' },
    All: { icon: Sparkles, color: 'text-purple-600', bg: 'from-purple-100 to-pink-100' },
  };

  const filteredTracks = soundTracks.filter(track => {
    const doshaMatch = selectedDosha === 'All' || track.dosha === 'All' || track.dosha === selectedDosha;
    const moodMatch = track.mood.includes(selectedMood);
    return doshaMatch && moodMatch;
  });

  const allRecommendations = soundTracks.filter(track => {
    return selectedDosha === 'All' || track.dosha === 'All' || track.dosha === selectedDosha;
  });

  const togglePlay = (trackId: string) => {
    setPlayingTrack(playingTrack === trackId ? null : trackId);
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-purple-100 via-blue-50 to-cyan-100 relative overflow-hidden">
      <Navigation currentPage="yoga" onNavigate={onNavigate} user={user} />

      <div className="max-w-7xl mx-auto p-6 md:p-8 relative z-10">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl md:text-4xl text-gray-800 mb-2">Sound Therapy</h1>
          <p className="text-gray-600 text-lg">AI-curated healing sounds based on your dosha and mood</p>
        </div>

        {/* Filters */}
        <div className="grid md:grid-cols-2 gap-6 mb-8">
          {/* Dosha Selection */}
          <div className="relative bg-white/40 backdrop-blur-xl rounded-3xl p-6 border border-white/50 shadow-xl">
            <h2 className="text-lg text-gray-800 mb-4">Select Your Dosha</h2>
            <div className="grid grid-cols-2 gap-3">
              {(['Vata', 'Pitta', 'Kapha', 'All'] as const).map((dosha) => {
                const doshaInfo = doshaIcons[dosha];
                const Icon = doshaInfo.icon;
                return (
                  <button
                    key={dosha}
                    onClick={() => setSelectedDosha(dosha)}
                    className={`p-4 rounded-2xl transition-all ${
                      selectedDosha === dosha
                        ? `bg-gradient-to-br ${doshaInfo.bg} ring-4 ring-purple-400 scale-105`
                        : 'bg-white/60 hover:bg-white/80'
                    }`}
                  >
                    <Icon className={`w-6 h-6 mb-2 mx-auto ${doshaInfo.color}`} />
                    <p className="text-sm text-gray-800">{dosha}</p>
                  </button>
                );
              })}
            </div>
          </div>

          {/* Mood Selection */}
          <div className="relative bg-white/40 backdrop-blur-xl rounded-3xl p-6 border border-white/50 shadow-xl">
            <h2 className="text-lg text-gray-800 mb-4">How are you feeling?</h2>
            <Select value={selectedMood} onValueChange={setSelectedMood}>
              <SelectTrigger className="bg-white/60 backdrop-blur-sm border-white/50">
                <SelectValue />
              </SelectTrigger>
              <SelectContent className="bg-white/95 backdrop-blur-xl border-white/50">
                {moods.map(mood => (
                  <SelectItem key={mood.value} value={mood.value}>
                    {mood.emoji} {mood.label}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>

            <div className="mt-4 p-4 rounded-2xl bg-gradient-to-br from-purple-50/80 to-pink-50/80">
              <p className="text-sm text-purple-900">
                <Sparkles className="w-4 h-4 inline mr-1" />
                AI analyzing your selections...
              </p>
            </div>
          </div>
        </div>

        {/* AI Recommendations */}
        <div className="mb-8">
          <div className="relative bg-white/40 backdrop-blur-xl rounded-3xl p-6 border border-white/50 shadow-xl">
            <div className="flex items-center gap-2 mb-6">
              <Sparkles className="w-6 h-6 text-purple-600" />
              <h2 className="text-xl text-gray-800">
                AI Recommended for You
              </h2>
              <Badge className="bg-gradient-to-r from-purple-500 to-pink-500 text-white border-0">
                {filteredTracks.length} Tracks
              </Badge>
            </div>

            {filteredTracks.length === 0 ? (
              <div className="text-center py-8">
                <p className="text-gray-600 mb-4">No specific recommendations for this combination.</p>
                <p className="text-sm text-gray-500">Try selecting "All Doshas" or a different mood.</p>
              </div>
            ) : (
              <div className="grid md:grid-cols-2 gap-4">
                {filteredTracks.map((track) => {
                  const isPlaying = playingTrack === track.id;
                  const Icon = doshaIcons[track.dosha].icon;
                  
                  return (
                    <div
                      key={track.id}
                      className="relative bg-white/60 backdrop-blur-sm rounded-2xl p-5 border border-white/50 hover:shadow-lg transition-all"
                    >
                      {/* Track Header */}
                      <div className="flex items-start justify-between mb-4">
                        <div className="flex items-start gap-3 flex-1">
                          <div className={`w-12 h-12 rounded-xl bg-gradient-to-br ${track.gradient} flex items-center justify-center text-2xl`}>
                            {track.icon}
                          </div>
                          <div className="flex-1">
                            <h3 className="text-gray-800 mb-1">{track.title}</h3>
                            <div className="flex items-center gap-2 flex-wrap">
                              <Badge variant="outline" className="text-xs">
                                <Icon className="w-3 h-3 mr-1" />
                                {track.dosha}
                              </Badge>
                              <Badge variant="outline" className="text-xs">
                                {track.frequency}
                              </Badge>
                              <span className="text-xs text-gray-500">{track.duration}</span>
                            </div>
                          </div>
                        </div>
                      </div>

                      {/* Description */}
                      <p className="text-sm text-gray-600 mb-4">{track.description}</p>

                      {/* Controls */}
                      <div className="flex items-center gap-3">
                        <Button
                          onClick={() => togglePlay(track.id)}
                          size="sm"
                          className={`${
                            isPlaying
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

                        {isPlaying && (
                          <div className="flex items-center gap-2 flex-1">
                            <Volume2 className="w-4 h-4 text-gray-600" />
                            <Slider
                              value={volume}
                              onValueChange={setVolume}
                              max={100}
                              step={1}
                              className="flex-1"
                            />
                            <span className="text-xs text-gray-600 w-8">{volume[0]}%</span>
                          </div>
                        )}
                      </div>

                      {/* Playing Animation */}
                      {isPlaying && (
                        <div className="mt-3 flex items-center gap-1">
                          {[...Array(20)].map((_, i) => (
                            <div
                              key={i}
                              className={`w-1 bg-gradient-to-t ${track.gradient} rounded-full`}
                              style={{
                                height: `${Math.random() * 20 + 10}px`,
                                animation: `pulse ${Math.random() * 0.5 + 0.5}s ease-in-out infinite`,
                              }}
                            />
                          ))}
                        </div>
                      )}
                    </div>
                  );
                })}
              </div>
            )}
          </div>
        </div>

        {/* All Tracks Library */}
        {selectedDosha !== 'All' && allRecommendations.length > filteredTracks.length && (
          <div className="relative bg-white/40 backdrop-blur-xl rounded-3xl p-6 border border-white/50 shadow-xl">
            <h2 className="text-xl text-gray-800 mb-6">
              All {selectedDosha} Balancing Sounds
            </h2>
            
            <div className="grid md:grid-cols-3 gap-4">
              {allRecommendations.map((track) => (
                <div
                  key={track.id}
                  className="p-4 rounded-2xl bg-white/60 backdrop-blur-sm border border-white/50 hover:shadow-lg transition-all"
                >
                  <div className={`w-10 h-10 rounded-xl bg-gradient-to-br ${track.gradient} flex items-center justify-center text-xl mb-3`}>
                    {track.icon}
                  </div>
                  <h4 className="text-sm text-gray-800 mb-1">{track.title}</h4>
                  <p className="text-xs text-gray-600 mb-2">{track.duration} • {track.frequency}</p>
                  <Button
                    onClick={() => togglePlay(track.id)}
                    size="sm"
                    variant="outline"
                    className="w-full"
                  >
                    <Play className="w-3 h-3 mr-1" />
                    Preview
                  </Button>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>

      <style>{`
        @keyframes pulse {
          0%, 100% { transform: scaleY(1); }
          50% { transform: scaleY(1.5); }
        }
      `}</style>
    </div>
  );
}
