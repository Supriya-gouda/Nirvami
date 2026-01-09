/**
 * Music Manager for Practice Sessions
 * Manages background music playback with strict category-based rules
 */

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';
const API_VERSION = 'v1';

// Music track definitions with categorization
const MEDITATION_TRACK = '30 Minute Deep Meditation Music Relax Mind Body Healing Music 432Hz Positive Energy Music 57344.mp3';
const YOGA_TRACK = 'white-dwarf-261405.mp3';

const GENERAL_RELAXATION_TRACKS = [
  'beautiful-dream-piano-146718.mp3',
  'bliss-146707.mp3',
  'calm-beach-meditation-247449.mp3',
  'embrace-14593.mp3',
  'just-relax-11157.mp3',
  'meditation-healing-248683.mp3',
  'piano-moment-9835.mp3',
  'relaxing-145038.mp3',
  'slow-motion-191583.mp3',
  'tender-142833.mp3',
  'the-beat-of-nature-122841.mp3'
];

type PracticeCategory = 'yoga' | 'meditation' | 'breathing' | 'ayurveda' | 'lifestyle' | 'sleep' | 'diet';

class MusicManager {
  private audio: HTMLAudioElement | null = null;
  private currentTrack: string | null = null;
  private isPlaying: boolean = false;
  private volume: number = 0.5;
  private category: PracticeCategory | null = null;

  /**
   * Select appropriate music track based on practice category
   */
  private selectTrack(category: PracticeCategory): string {
    let allowedTracks: string[] = [];

    switch (category) {
      case 'meditation':
        // Meditation: Can use meditation track OR any general track
        // FORBIDDEN: yoga-exclusive track
        allowedTracks = [MEDITATION_TRACK, ...GENERAL_RELAXATION_TRACKS];
        break;

      case 'yoga':
        // Yoga: Can use yoga track OR any general track
        // FORBIDDEN: meditation-only track
        allowedTracks = [YOGA_TRACK, ...GENERAL_RELAXATION_TRACKS];
        break;

      case 'breathing':
      case 'ayurveda':
      case 'lifestyle':
      case 'sleep':
      case 'diet':
        // All other categories: ONLY general relaxation music
        // FORBIDDEN: meditation track, yoga track
        allowedTracks = [...GENERAL_RELAXATION_TRACKS];
        break;

      default:
        // Fallback to general tracks
        allowedTracks = [...GENERAL_RELAXATION_TRACKS];
    }

    // Randomly select from allowed tracks
    const randomIndex = Math.floor(Math.random() * allowedTracks.length);
    return allowedTracks[randomIndex];
  }

  /**
   * Initialize music for a practice session
   */
  async init(category: PracticeCategory): Promise<void> {
    try {
      this.category = category;
      const selectedTrack = this.selectTrack(category);
      
      // Build full URL to backend media endpoint
      const audioUrl = `${API_BASE_URL}/api/${API_VERSION}/media/music/${encodeURIComponent(selectedTrack)}`;

      console.log(`🎵 Music category: ${category}`);
      console.log(`🎵 Selected track: ${selectedTrack}`);
      console.log(`🎵 Music source: ${audioUrl}`);

      // Create audio element
      this.audio = new Audio();
      this.audio.src = audioUrl;
      this.audio.loop = true;
      this.audio.volume = this.volume;
      this.audio.preload = 'auto';
      this.currentTrack = selectedTrack;

      // Set up event listeners for debugging
      this.audio.addEventListener('loadedmetadata', () => {
        console.log('🎵 Audio metadata loaded OK');
      });

      this.audio.addEventListener('canplaythrough', () => {
        console.log('🎵 Audio ready to play - canplaythrough');
      });

      this.audio.addEventListener('error', (event) => {
        const error = this.audio?.error;
        console.error('❌ Music playback error:', {
          code: error?.code,
          message: error?.message,
          url: audioUrl
        });
        console.warn('⚠️ Continuing session without music');
        this.audio = null;
        this.currentTrack = null;
      });

      // Preload the audio
      this.audio.load();
      
      // Wait for audio to be ready
      await new Promise<void>((resolve, reject) => {
        if (!this.audio) {
          resolve();
          return;
        }

        const onCanPlay = () => {
          console.log('🎵 Audio loaded and ready');
          cleanup();
          resolve();
        };

        const onError = () => {
          console.error('❌ Failed to load audio');
          cleanup();
          reject(new Error('Failed to load audio'));
        };

        const cleanup = () => {
          this.audio?.removeEventListener('canplaythrough', onCanPlay);
          this.audio?.removeEventListener('error', onError);
        };

        this.audio.addEventListener('canplaythrough', onCanPlay, { once: true });
        this.audio.addEventListener('error', onError, { once: true });
      });

    } catch (error: any) {
      console.warn('⚠️ Failed to initialize music:', error.message || error);
      console.warn('⚠️ Continuing session without music');
      this.audio = null;
      this.currentTrack = null;
    }
  }

  /**
   * Start playing music
   */
  async play(): Promise<void> {
    if (!this.audio) {
      console.warn('⚠️ No audio initialized, continuing without music');
      return;
    }

    try {
      await this.audio.play();
      this.isPlaying = true;
      console.log('🎵 Music started playing');
    } catch (error) {
      console.warn('⚠️ Failed to play music, continuing without music:', error);
      this.isPlaying = false;
    }
  }

  /**
   * Pause music
   */
  pause(): void {
    if (this.audio && this.isPlaying) {
      this.audio.pause();
      this.isPlaying = false;
      console.log('⏸️ Music paused');
    }
  }

  /**
   * Resume music
   */
  async resume(): Promise<void> {
    if (this.audio && !this.isPlaying) {
      try {
        await this.audio.play();
        this.isPlaying = true;
        console.log('▶️ Music resumed');
      } catch (error) {
        console.warn('⚠️ Failed to resume music:', error);
      }
    }
  }

  /**
   * Stop and cleanup music
   */
  stop(): void {
    if (this.audio) {
      this.audio.pause();
      this.audio.currentTime = 0;
      this.audio = null;
      this.isPlaying = false;
      this.currentTrack = null;
      console.log('⏹️ Music stopped and cleaned up');
    }
  }

  /**
   * Set volume (0-1)
   */
  setVolume(volume: number): void {
    this.volume = Math.max(0, Math.min(1, volume));
    if (this.audio) {
      this.audio.volume = this.volume;
    }
  }

  /**
   * Get current playback status
   */
  getStatus() {
    return {
      isPlaying: this.isPlaying,
      currentTrack: this.currentTrack,
      volume: this.volume,
      category: this.category
    };
  }

  /**
   * Check if audio is available (not failed)
   */
  isAudioAvailable(): boolean {
    return this.audio !== null;
  }
}

export default MusicManager;
