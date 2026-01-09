/**
 * Voice Guidance Service
 * Provides text-to-speech narration for practice sessions
 * Uses system-generated TTS with calm female voice
 */

class VoiceGuidanceService {
  private synthesis: SpeechSynthesis;
  private currentUtterance: SpeechSynthesisUtterance | null = null;
  private isSpeaking: boolean = false;
  private selectedVoice: SpeechSynthesisVoice | null = null;
  private onSpeakStart: (() => void) | null = null;
  private onSpeakEnd: (() => void) | null = null;

  constructor() {
    this.synthesis = window.speechSynthesis;
    this.initVoices();
  }

  /**
   * Initialize and select appropriate voice
   */
  private initVoices(): void {
    // Wait for voices to be loaded
    if (this.synthesis.getVoices().length === 0) {
      this.synthesis.addEventListener('voiceschanged', () => {
        this.selectOptimalVoice();
      }, { once: true });
    } else {
      this.selectOptimalVoice();
    }
  }

  /**
   * Select the best available female voice
   * Priority: Indian female > UK female > US female > Default
   */
  private selectOptimalVoice(): void {
    const voices = this.synthesis.getVoices();
    
    if (voices.length === 0) {
      console.warn('⚠️ No TTS voices available');
      return;
    }

    // Priority 1: Indian English female voices
    const preferredVoices = [
      'Microsoft Heera - English (India)',
      'Microsoft Heera Desktop - English (India)',
      'Google हिन्दी',
      'Raveena', // Indian English (Amazon Polly style)
      'Aditi'    // Indian English (Amazon Polly style)
    ];

    for (const voiceName of preferredVoices) {
      const voice = voices.find(v => v.name.includes(voiceName));
      if (voice) {
        this.selectedVoice = voice;
        console.log(`🎙️ Selected voice: ${voice.name}`);
        return;
      }
    }

    // Priority 2: Any Indian locale voice (en-IN, hi-IN)
    const indianVoice = voices.find(v => 
      v.lang.startsWith('en-IN') || v.lang.startsWith('hi-IN')
    );
    if (indianVoice) {
      this.selectedVoice = indianVoice;
      console.log(`🎙️ Selected Indian voice: ${indianVoice.name}`);
      return;
    }

    // Priority 3: UK female voice
    const ukFemaleVoice = voices.find(v => 
      v.lang.startsWith('en-GB') && v.name.toLowerCase().includes('female')
    );
    if (ukFemaleVoice) {
      this.selectedVoice = ukFemaleVoice;
      console.log(`🎙️ Selected UK female voice: ${ukFemaleVoice.name}`);
      return;
    }

    // Priority 4: US female voice
    const usFemaleVoice = voices.find(v => 
      v.lang.startsWith('en-US') && v.name.toLowerCase().includes('female')
    );
    if (usFemaleVoice) {
      this.selectedVoice = usFemaleVoice;
      console.log(`🎙️ Selected US female voice: ${usFemaleVoice.name}`);
      return;
    }

    // Priority 5: Any female voice
    const anyFemaleVoice = voices.find(v => 
      v.name.toLowerCase().includes('female') || 
      v.name.toLowerCase().includes('woman')
    );
    if (anyFemaleVoice) {
      this.selectedVoice = anyFemaleVoice;
      console.log(`🎙️ Selected female voice: ${anyFemaleVoice.name}`);
      return;
    }

    // Fallback: Use default voice
    this.selectedVoice = voices[0];
    console.log(`🎙️ Using default voice: ${voices[0].name}`);
  }

  /**
   * Speak the given text with calm, soothing settings
   */
  async speak(text: string): Promise<void> {
    return new Promise((resolve, reject) => {
      // Cancel any ongoing speech
      this.stop();

      const utterance = new SpeechSynthesisUtterance(text);
      
      // Apply voice settings
      if (this.selectedVoice) {
        utterance.voice = this.selectedVoice;
      }
      
      // Calm, soothing voice settings
      utterance.rate = 0.85;    // Slightly slower for clarity and calmness
      utterance.pitch = 1.0;     // Natural pitch
      utterance.volume = 1.0;    // Full volume

      utterance.onstart = () => {
        this.isSpeaking = true;
        if (this.onSpeakStart) {
          this.onSpeakStart();
        }
        console.log(`🎙️ Speaking: "${text.substring(0, 50)}..."`);
      };

      utterance.onend = () => {
        this.isSpeaking = false;
        this.currentUtterance = null;
        if (this.onSpeakEnd) {
          this.onSpeakEnd();
        }
        console.log('🎙️ Speech completed');
        resolve();
      };

      utterance.onerror = (event) => {
        console.error('❌ TTS error:', event);
        this.isSpeaking = false;
        this.currentUtterance = null;
        // Don't reject - continue gracefully without voice
        resolve();
      };

      this.currentUtterance = utterance;
      
      try {
        this.synthesis.speak(utterance);
      } catch (error) {
        console.error('❌ Failed to speak:', error);
        this.isSpeaking = false;
        this.currentUtterance = null;
        resolve(); // Continue gracefully
      }
    });
  }

  /**
   * Stop any ongoing speech
   */
  stop(): void {
    if (this.isSpeaking) {
      this.synthesis.cancel();
      this.isSpeaking = false;
      this.currentUtterance = null;
      console.log('⏹️ Speech stopped');
    }
  }

  /**
   * Pause ongoing speech
   */
  pause(): void {
    if (this.isSpeaking && !this.synthesis.paused) {
      this.synthesis.pause();
      console.log('⏸️ Speech paused');
    }
  }

  /**
   * Resume paused speech
   */
  resume(): void {
    if (this.synthesis.paused) {
      this.synthesis.resume();
      console.log('▶️ Speech resumed');
    }
  }

  /**
   * Set callbacks for speech events
   */
  setCallbacks(onStart: () => void, onEnd: () => void): void {
    this.onSpeakStart = onStart;
    this.onSpeakEnd = onEnd;
  }

  /**
   * Check if currently speaking
   */
  getIsSpeaking(): boolean {
    return this.isSpeaking;
  }

  /**
   * Get available voices for debugging
   */
  getAvailableVoices(): SpeechSynthesisVoice[] {
    return this.synthesis.getVoices();
  }

  /**
   * Get selected voice info
   */
  getSelectedVoice(): string {
    return this.selectedVoice ? this.selectedVoice.name : 'None';
  }
}

export default VoiceGuidanceService;
