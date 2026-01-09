import { useState } from 'react';
import { motion, AnimatePresence } from 'motion/react';
import { ChevronLeft, ChevronRight, Check } from 'lucide-react';
import { Navigation } from './Navigation';
import { Button } from './ui/button';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { RadioGroup, RadioGroupItem } from './ui/radio-group';
import { Label } from './ui/label';
import { Progress } from './ui/progress';
import type { PageType } from '../App';
import type { User } from '../contexts/AuthContext';
import api from '../services/api';

interface DoshaQuizPageProps {
  user: User | null;
  onNavigate: (page: PageType) => void;
  onLogout?: () => void;
  onOpenNotifications?: () => void;
}

interface Question {
  id: string;
  question: string;
  category: 'vata' | 'pitta' | 'kapha';
  options: {
    text: string;
    dosha: 'vata' | 'pitta' | 'kapha';
  }[];
}

const questions: Question[] = [
  {
    id: 'q1',
    question: 'How would you describe your body frame?',
    category: 'vata',
    options: [
      { text: 'Thin, light, hard to gain weight', dosha: 'vata' },
      { text: 'Medium, athletic build', dosha: 'pitta' },
      { text: 'Large, solid, easy to gain weight', dosha: 'kapha' }
    ]
  },
  {
    id: 'q2',
    question: 'What is your skin type?',
    category: 'pitta',
    options: [
      { text: 'Dry, rough, thin', dosha: 'vata' },
      { text: 'Warm, soft, prone to rashes', dosha: 'pitta' },
      { text: 'Thick, oily, smooth', dosha: 'kapha' }
    ]
  },
  {
    id: 'q3',
    question: 'How is your appetite?',
    category: 'kapha',
    options: [
      { text: 'Irregular, varies throughout the day', dosha: 'vata' },
      { text: 'Strong, I get angry when hungry', dosha: 'pitta' },
      { text: 'Steady, can skip meals easily', dosha: 'kapha' }
    ]
  },
  {
    id: 'q4',
    question: 'How do you handle stress?',
    category: 'vata',
    options: [
      { text: 'I get anxious and worried', dosha: 'vata' },
      { text: 'I become irritable and angry', dosha: 'pitta' },
      { text: 'I withdraw and become lethargic', dosha: 'kapha' }
    ]
  },
  {
    id: 'q5',
    question: 'What is your sleep pattern like?',
    category: 'pitta',
    options: [
      { text: 'Light sleeper, difficulty falling asleep', dosha: 'vata' },
      { text: 'Moderate, I sleep soundly but lightly', dosha: 'pitta' },
      { text: 'Heavy sleeper, love long sleep', dosha: 'kapha' }
    ]
  },
  {
    id: 'q6',
    question: 'How would you describe your energy levels?',
    category: 'kapha',
    options: [
      { text: 'Quick bursts of energy, then fatigue', dosha: 'vata' },
      { text: 'Steady, intense energy', dosha: 'pitta' },
      { text: 'Slow to start, then steady endurance', dosha: 'kapha' }
    ]
  },
  {
    id: 'q7',
    question: 'What is your typical body temperature?',
    category: 'vata',
    options: [
      { text: 'Cold hands and feet', dosha: 'vata' },
      { text: 'Warm, I sweat easily', dosha: 'pitta' },
      { text: 'Cool, but comfortable', dosha: 'kapha' }
    ]
  },
  {
    id: 'q8',
    question: 'How do you learn best?',
    category: 'pitta',
    options: [
      { text: 'Quick to learn, quick to forget', dosha: 'vata' },
      { text: 'Sharp intellect, good retention', dosha: 'pitta' },
      { text: 'Slow to learn, excellent retention', dosha: 'kapha' }
    ]
  },
  {
    id: 'q9',
    question: 'How is your digestion?',
    category: 'kapha',
    options: [
      { text: 'Irregular, gas, bloating', dosha: 'vata' },
      { text: 'Strong, fast metabolism', dosha: 'pitta' },
      { text: 'Slow, heavy feeling after meals', dosha: 'kapha' }
    ]
  },
  {
    id: 'q10',
    question: 'What is your decision-making style?',
    category: 'vata',
    options: [
      { text: 'Quick, sometimes impulsive', dosha: 'vata' },
      { text: 'Decisive, analytical', dosha: 'pitta' },
      { text: 'Slow, methodical, thoughtful', dosha: 'kapha' }
    ]
  },
  {
    id: 'q11',
    question: 'How do you typically speak?',
    category: 'pitta',
    options: [
      { text: 'Fast, enthusiastic, sometimes rambling', dosha: 'vata' },
      { text: 'Sharp, clear, precise, sometimes argumentative', dosha: 'pitta' },
      { text: 'Slow, melodious, good listener', dosha: 'kapha' }
    ]
  },
  {
    id: 'q12',
    question: 'What is your walking pace?',
    category: 'kapha',
    options: [
      { text: 'Fast, irregular, light steps', dosha: 'vata' },
      { text: 'Medium, determined, purposeful', dosha: 'pitta' },
      { text: 'Slow, steady, heavy steps', dosha: 'kapha' }
    ]
  }
];

export function DoshaQuizPage({ user, onNavigate, onLogout, onOpenNotifications }: DoshaQuizPageProps) {
  const [currentQuestionIndex, setCurrentQuestionIndex] = useState(0);
  const [answers, setAnswers] = useState<Record<string, string>>(
    questions.reduce((acc, q) => ({ ...acc, [q.id]: '' }), {})
  );
  const [isSubmitting, setIsSubmitting] = useState(false);

  const currentQuestion = questions[currentQuestionIndex];
  const progress = ((currentQuestionIndex + 1) / questions.length) * 100;
  const isLastQuestion = currentQuestionIndex === questions.length - 1;
  const canGoNext = answers[currentQuestion.id] !== undefined && answers[currentQuestion.id] !== '';

  const handleAnswer = (optionIndex: number) => {
    setAnswers({
      ...answers,
      [currentQuestion.id]: String(optionIndex)
    });
  };

  const handleNext = () => {
    if (isLastQuestion && canGoNext) {
      handleSubmit();
    } else if (canGoNext) {
      setCurrentQuestionIndex(currentQuestionIndex + 1);
    }
  };

  const handlePrevious = () => {
    if (currentQuestionIndex > 0) {
      setCurrentQuestionIndex(currentQuestionIndex - 1);
    }
  };

  const handleSubmit = async () => {
    setIsSubmitting(true);
    try {
      // Convert answers to new API format with selected_dosha
      const quizAnswers = questions.map((q) => {
        const selectedOptionIndex = parseInt(answers[q.id] || '0');
        const selectedOption = q.options[selectedOptionIndex];
        
        return {
          question_id: q.id,  // Use question ID (e.g., 'q1')
          selected_dosha: selectedOption.dosha  // Which dosha was selected (vata/pitta/kapha)
        };
      });

      console.log('Submitting dosha quiz with answers:', quizAnswers);

      // Submit to backend
      const result = await api.submitDoshaAssessment({ answers: quizAnswers });
      
      console.log('Dosha assessment result:', result);
      
      // Navigate to dashboard
      onNavigate('dashboard');
    } catch (err: any) {
      console.error('Error submitting quiz:', err);
      console.error('Error details:', err.response?.data);
      const errorMsg = err.response?.data?.detail || 'Failed to submit quiz. Please try again.';
      alert(errorMsg);
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-purple-50 via-blue-50 to-pink-50">
      <Navigation currentPage="yoga" onNavigate={onNavigate} onLogout={onLogout} user={user} onOpenNotifications={onOpenNotifications} />
      
      <div className="max-w-3xl mx-auto p-8">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="mb-8"
        >
          <h1 className="text-4xl font-bold mb-2 bg-gradient-to-r from-purple-600 to-pink-600 bg-clip-text text-transparent text-center">
            Discover Your Dosha
          </h1>
          <p className="text-gray-600 text-center mb-6">
            Answer these questions to understand your Ayurvedic constitution
          </p>
          
          <div className="mb-4">
            <div className="flex justify-between text-sm text-gray-600 mb-2">
              <span>Question {currentQuestionIndex + 1} of {questions.length}</span>
              <span>{Math.round(progress)}%</span>
            </div>
            <Progress value={progress} className="h-2" />
          </div>
        </motion.div>

        <AnimatePresence mode="wait">
          <motion.div
            key={currentQuestionIndex}
            initial={{ opacity: 0, x: 50 }}
            animate={{ opacity: 1, x: 0 }}
            exit={{ opacity: 0, x: -50 }}
            transition={{ duration: 0.3 }}
          >
            <Card className="shadow-xl">
              <CardHeader>
                <CardTitle className="text-2xl">
                  {currentQuestion.question}
                </CardTitle>
              </CardHeader>
              <CardContent>
                <RadioGroup
                  value={answers[currentQuestion.id]}
                  onValueChange={(value: string) => handleAnswer(parseInt(value))}
                >
                  <div className="space-y-4">
                    {currentQuestion.options.map((option, index) => (
                      <div
                        key={index}
                        className={`flex items-center space-x-3 p-4 rounded-lg border-2 transition-all cursor-pointer ${
                          answers[currentQuestion.id] === String(index)
                            ? 'border-purple-500 bg-purple-50'
                            : 'border-gray-200 hover:border-purple-300'
                        }`}
                        onClick={() => handleAnswer(index)}
                      >
                        <RadioGroupItem value={String(index)} id={`option-${index}`} />
                        <Label
                          htmlFor={`option-${index}`}
                          className="flex-1 cursor-pointer font-medium"
                        >
                          {option.text}
                        </Label>
                      </div>
                    ))}
                  </div>
                </RadioGroup>
              </CardContent>
            </Card>
          </motion.div>
        </AnimatePresence>

        <div className="flex justify-between mt-8">
          <Button
            variant="outline"
            onClick={handlePrevious}
            disabled={currentQuestionIndex === 0}
            className="flex items-center gap-2"
          >
            <ChevronLeft className="w-4 h-4" />
            Previous
          </Button>
          
          <Button
            onClick={handleNext}
            disabled={!canGoNext || isSubmitting}
            className="bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-700 hover:to-pink-700 flex items-center gap-2"
          >
            {isSubmitting ? (
              <>
                <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
                Submitting...
              </>
            ) : isLastQuestion ? (
              <>
                Finish Quiz
                <Check className="w-4 h-4" />
              </>
            ) : (
              <>
                Next
                <ChevronRight className="w-4 h-4" />
              </>
            )}
          </Button>
        </div>
      </div>
    </div>
  );
}
