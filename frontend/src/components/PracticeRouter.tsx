/**
 * Dynamic Practice Router
 * Routes to the correct practice component based on recommendation category
 */

import { YogaPractice } from './practices/YogaPractice';
import { BreathingPractice } from './practices/BreathingPractice';
import { MeditationPractice } from './practices/MeditationPractice';
import { AyurvedaPractice } from './practices/AyurvedaPractice';
import { DietPractice } from './practices/DietPractice';
import { SleepPractice } from './practices/SleepPractice';
import { LifestylePractice } from './practices/LifestylePractice';

interface PracticeRouterProps {
  recommendation: {
    id?: string;
    title: string;
    content: string;
    category?: string;
    source?: string;
  };
  onComplete: () => void;
  onClose: () => void;
}

export function PracticeRouter({ recommendation, onComplete, onClose }: PracticeRouterProps) {
  // Determine the category
  const category = (recommendation.category || '').toLowerCase();

  console.log(`🎯 Routing to practice for category: ${category}`);

  // Route to appropriate practice component
  switch (category) {
    case 'yoga':
      return <YogaPractice recommendation={recommendation} onComplete={onComplete} onClose={onClose} />;
    
    case 'breathing':
      return <BreathingPractice recommendation={recommendation} onComplete={onComplete} onClose={onClose} />;
    
    case 'meditation':
      return <MeditationPractice recommendation={recommendation} onComplete={onComplete} onClose={onClose} />;
    
    case 'ayurveda':
      return <AyurvedaPractice recommendation={recommendation} onComplete={onComplete} onClose={onClose} />;
    
    case 'diet':
      return <DietPractice recommendation={recommendation} onComplete={onComplete} onClose={onClose} />;
    
    case 'sleep':
      return <SleepPractice recommendation={recommendation} onComplete={onComplete} onClose={onClose} />;
    
    case 'lifestyle':
      return <LifestylePractice recommendation={recommendation} onComplete={onComplete} onClose={onClose} />;
    
    default:
      // Fallback to lifestyle for unknown categories
      console.warn(`Unknown category: ${category}, defaulting to lifestyle practice`);
      return <LifestylePractice recommendation={recommendation} onComplete={onComplete} onClose={onClose} />;
  }
}
