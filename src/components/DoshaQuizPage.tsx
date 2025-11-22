import { useState } from 'react';
import { motion, AnimatePresence } from 'motion/react';
import { ChevronLeft, ChevronRight, Check, Sparkles } from 'lucide-react';
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
    score: number;
  }[];
}

const questions: Question[] = [
  {
    id: 'q1',
    question: 'How would you describe your body frame?',
    category: 'vata',
    options: [
      { text: 'Thin, light, hard to gain weight', dosha: 'vata', score: 3 },
      { text: 'Medium, athletic build', dosha: 'pitta', score: 3 },
      { text: 'Large, solid, easy to gain weight', dosha: 'kapha', score: 3 }
    ]
  },
  {
    id: 'q2',
    question: 'What is your skin type?',
    category: 'pitta',
    options: [
      { text: 'Dry, rough, thin', dosha: 'vata', score: 3 },
      { text: 'Warm, soft, prone to rashes', dosha: 'pitta', score: 3 },
      { text: 'Thick, oily, smooth', dosha: 'kapha', score: 3 }
    ]
  },
  {
    id: 'q3',
    question: 'How is your appetite?',
    category: 'kapha',
    options: [
      { text: 'Irregular, varies throughout the day', dosha: 'vata', score: 3 },
      { text: 'Strong, I get angry when hungry', dosha: 'pitta', score: 3 },
      { text: 'Steady, can skip meals easily', dosha: 'kapha', score: 3 }
    ]
  },
  {
    id: 'q4',
    question: 'How do you handle stress?',
    category: 'vata',
    options: [
      { text: 'I get anxious and worried', dosha: 'vata', score: 3 },
      { text: 'I become irritable and angry', dosha: 'pitta', score: 3 },
      { text: 'I withdraw and become lethargic', dosha: 'kapha', score: 3 }
    ]
  },
  {
    id: 'q5',
    question: 'What is your sleep pattern like?',
    category: 'pitta',
    options: [
      { text: 'Light sleeper, difficulty falling asleep', dosha: 'vata', score: 3 },
      { text: 'Moderate, I sleep soundly but lightly', dosha: 'pitta', score: 3 },
      { text: 'Heavy sleeper, love long sleep', dosha: 'kapha', score: 3 }
    ]
  },
  {
    id: 'q6',
    question: 'How would you describe your energy levels?',
    category: 'kapha',
    options: [
      { text: 'Quick bursts of energy, then fatigue', dosha: 'vata', score: 3 },
      { text: 'Steady, intense energy', dosha: 'pitta', score: 3 },
      { text: 'Slow to start, then steady endurance', dosha: 'kapha', score: 3 }
    ]
  },
  {
    id: 'q7',
    question: 'What is your typical body temperature?',
    category: 'vata',
    options: [
      { text: 'Cold hands and feet', dosha: 'vata', score: 3 },
      { text: 'Warm, I sweat easily', dosha: 'pitta', score: 3 },
      { text: 'Cool, but comfortable', dosha: 'kapha', score: 3 }
    ]
  },
  {
    id: 'q8',
    question: 'How do you learn best?',
    category: 'pitta',
    options: [
      { text: 'Quick to learn, quick to forget', dosha: 'vata', score: 3 },
      { text: 'Sharp intellect, good retention', dosha: 'pitta', score: 3 },
      { text: 'Slow to learn, excellent retention', dosha: 'kapha', score: 3 }
    ]
  },
  {
    id: 'q9',
    question: 'How is your digestion?',
    category: 'kapha',
    options: [
      { text: 'Irregular, gas, bloating', dosha: 'vata', score: 3 },
      { text: 'Strong, fast metabolism', dosha: 'pitta', score: 3 },
      { text: 'Slow, heavy feeling after meals', dosha: 'kapha', score: 3 }
    ]
  },
  {
    id: 'q10',
    question: 'What is your decision-making style?',
    category: 'vata',
    options: [
      { text: 'Quick, sometimes impulsive', dosha: 'vata', score: 3 },
      { text: 'Decisive, analytical', dosha: 'pitta', score: 3 },
      { text: 'Slow, methodical, thoughtful', dosha: 'kapha', score: 3 }
    ]
  }
];

export function DoshaQuizPage({ user, onNavigate, onLogout, onOpenNotifications }: DoshaQuizPageProps) {
  const [currentQuestionIndex, setCurrentQuestionIndex] = useState(0);
  const [answers, setAnswers] = useState<Record<string, string>>({});
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [showResults, setShowResults] = useState(false);
  const [result, setResult] = useState<any>(null);
  const [recommendations, setRecommendations] = useState<any>(null);

  const currentQuestion = questions[currentQuestionIndex];
  const progress = ((currentQuestionIndex + 1) / questions.length) * 100;
  const isLastQuestion = currentQuestionIndex === questions.length - 1;
  const canGoNext = answers[currentQuestion.id] !== undefined;

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
      // Calculate dosha scores
      let vataScore = 0;
      let pittaScore = 0;
      let kaphaScore = 0;

      questions.forEach((q) => {
        const answerIndex = parseInt(answers[q.id] || '0');
        const selectedOption = q.options[answerIndex];
        
        if (selectedOption.dosha === 'vata') vataScore += selectedOption.score;
        else if (selectedOption.dosha === 'pitta') pittaScore += selectedOption.score;
        else if (selectedOption.dosha === 'kapha') kaphaScore += selectedOption.score;
      });

      // Submit to backend
      const doshaResult = await api.submitDoshaAssessment({
        answers: {
          ...answers,
          vata_score: vataScore,
          pitta_score: pittaScore,
          kapha_score: kaphaScore
        }
      });

      // Get recommendations
      const recs = await api.getDoshaRecommendations();

      setResult(doshaResult);
      setRecommendations(recs);
      setShowResults(true);
    } catch (err) {
      console.error('Failed to submit dosha quiz:', err);
      alert('Failed to submit quiz. Please try again.');
    } finally {
      setIsSubmitting(false);
    }
  };

  const getDoshaColor = (dosha: string) => {
    const colors = {
      vata: 'from-blue-400 to-cyan-400',
      pitta: 'from-orange-400 to-red-400',
      kapha: 'from-green-400 to-emerald-400'
    };
    return colors[dosha as keyof typeof colors] || 'from-purple-400 to-pink-400';
  };

  if (showResults && result) {
    const dominantDosha = result.primary_dosha || result.dominant_dosha || 'vata';
    
    return (
      <div className="min-h-screen bg-gradient-to-br from-purple-50 via-blue-50 to-pink-50">
        <Navigation currentPage="yoga" onNavigate={onNavigate} onLogout={onLogout} user={user} onOpenNotifications={onOpenNotifications} />
        
        <div className="max-w-4xl mx-auto p-8">
          <motion.div
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            className="text-center mb-8"
          >
            <Sparkles className="w-16 h-16 text-purple-600 mx-auto mb-4" />
            <h1 className="text-4xl font-bold mb-2 bg-gradient-to-r from-purple-600 to-pink-600 bg-clip-text text-transparent">
              Your Dosha Profile
            </h1>
            <p className="text-gray-600">Discover your Ayurvedic constitution</p>
          </motion.div>

          {/* Dosha Scores */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.2 }}
            className="mb-8"
          >
            <Card className={`bg-gradient-to-br ${getDoshaColor(dominantDosha)} text-white border-none shadow-2xl`}>
              <CardHeader>
                <CardTitle className="text-3xl text-center">
                  Your Primary Dosha: {dominantDosha.charAt(0).toUpperCase() + dominantDosha.slice(1)}
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  <div>
                    <div className="flex justify-between mb-2">
                      <span className="font-semibold">Vata</span>
                      <span>{result.vata_score || 0}%</span>
                    </div>
                    <Progress value={result.vata_score || 0} className="h-3 bg-white/30" />
                  </div>
                  <div>
                    <div className="flex justify-between mb-2">
                      <span className="font-semibold">Pitta</span>
                      <span>{result.pitta_score || 0}%</span>
                    </div>
                    <Progress value={result.pitta_score || 0} className="h-3 bg-white/30" />
                  </div>
                  <div>
                    <div className="flex justify-between mb-2">
                      <span className="font-semibold">Kapha</span>
                      <span>{result.kapha_score || 0}%</span>
                    </div>
                    <Progress value={result.kapha_score || 0} className="h-3 bg-white/30" />
                  </div>
                </div>
              </CardContent>
            </Card>
          </motion.div>

          {/* Recommendations */}
          {recommendations && (
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.4 }}
              className="grid md:grid-cols-2 gap-6 mb-8"
            >
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    🍽️ Diet Recommendations
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <ul className="space-y-2">
                    {recommendations.diet?.map((tip: string, index: number) => (
                      <li key={index} className="flex items-start gap-2">
                        <Check className="w-5 h-5 text-green-600 flex-shrink-0 mt-0.5" />
                        <span className="text-sm text-gray-700">{tip}</span>
                      </li>
                    ))}
                  </ul>
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    🧘 Lifestyle Tips
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <ul className="space-y-2">
                    {recommendations.lifestyle?.map((tip: string, index: number) => (
                      <li key={index} className="flex items-start gap-2">
                        <Check className="w-5 h-5 text-green-600 flex-shrink-0 mt-0.5" />
                        <span className="text-sm text-gray-700">{tip}</span>
                      </li>
                    ))}
                  </ul>
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    🕉️ Yoga Practices
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <ul className="space-y-2">
                    {recommendations.yoga?.map((tip: string, index: number) => (
                      <li key={index} className="flex items-start gap-2">
                        <Check className="w-5 h-5 text-green-600 flex-shrink-0 mt-0.5" />
                        <span className="text-sm text-gray-700">{tip}</span>
                      </li>
                    ))}
                  </ul>
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    🧠 Meditation
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <ul className="space-y-2">
                    {recommendations.meditation?.map((tip: string, index: number) => (
                      <li key={index} className="flex items-start gap-2">
                        <Check className="w-5 h-5 text-green-600 flex-shrink-0 mt-0.5" />
                        <span className="text-sm text-gray-700">{tip}</span>
                      </li>
                    ))}
                  </ul>
                </CardContent>
              </Card>
            </motion.div>
          )}

          <div className="text-center">
            <Button
              onClick={() => onNavigate('dashboard')}
              size="lg"
              className="bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-700 hover:to-pink-700"
            >
              Go to Dashboard
            </Button>
          </div>
        </div>
      </div>
    );
  }

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
