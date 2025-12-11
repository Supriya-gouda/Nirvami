import { useState, useEffect } from 'react';
import { motion } from 'motion/react';
import { UtensilsCrossed, TrendingUp, AlertCircle, ChefHat, Calendar, Clock, BarChart3 } from 'lucide-react';
import { Navigation } from './Navigation';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { Badge } from './ui/badge';
import { Button } from './ui/button';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogDescription } from './ui/dialog';
import { Input } from './ui/input';
import { Textarea } from './ui/textarea';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from './ui/select';
import { LineChart, Line, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import type { PageType } from '../App';
import type { User } from '../types/api.types';
import api from '../services/api';

interface DietMoodPageProps {
  user: User | null;
  onNavigate: (page: PageType) => void;
  onLogout?: () => void;
  onOpenNotifications?: () => void;
}

interface TodaysMeals {
  breakfast: any[];
  lunch: any[];
  dinner: any[];
  snack: any[];
}

interface MealMoodInsights {
  insights: string[];
  top_positive_foods: any[];
  foods_to_moderate: any[];
  recommendations: string[];
}

export function DietMoodPage({ user, onNavigate, onLogout, onOpenNotifications }: DietMoodPageProps) {
  // State for meal logging
  const [newMealType, setNewMealType] = useState<'breakfast' | 'lunch' | 'dinner' | 'snack'>('breakfast');
  const [newMealText, setNewMealText] = useState('');
  const [newMealNotes, setNewMealNotes] = useState('');
  const [savingMeal, setSavingMeal] = useState(false);
  const [mealSuccess, setMealSuccess] = useState<string | null>(null);
  const [mealError, setMealError] = useState<string | null>(null);

  // State for data
  const [todaysMeals, setTodaysMeals] = useState<TodaysMeals>({ 
    breakfast: [], lunch: [], dinner: [], snack: [] 
  });
  const [weeklyPattern, setWeeklyPattern] = useState<any[]>([]);
  const [weeklyCounts, setWeeklyCounts] = useState<any[]>([]);
  const [moodCorrelations, setMoodCorrelations] = useState<any[]>([]);
  const [moodInsights, setMoodInsights] = useState<MealMoodInsights>({
    insights: [], top_positive_foods: [], foods_to_moderate: [], recommendations: []
  });
  const [ayurvedaGuidelines, setAyurvedaGuidelines] = useState<any[]>([]);
  const [mealAnalysis, setMealAnalysis] = useState<any>(null);
  const [dailyAnalysis, setDailyAnalysis] = useState<any>(null);
  const [loading, setLoading] = useState(false);

  // Dialog states
  const [showMealDetails, setShowMealDetails] = useState(false);
  const [selectedMeal, setSelectedMeal] = useState<any>(null);

  // Load all data on component mount
  useEffect(() => {
    loadAllData();
  }, []);

  const loadAllData = async () => {
    try {
      setLoading(true);
      
      const [
        todaysData, 
        weeklyData, 
        weeklyCountsData,
        correlationsData, 
        insightsData, 
        guidelinesData,
        dailyAnalysisData
      ] = await Promise.all([
        api.getTodayMealsFormatted(),
        api.getWeeklyMealPattern(4),
        api.getWeeklyCounts(),
        api.getMoodCorrelationsWithDays(30),
        api.getMoodInsights(),
        api.getAyurvedaGuidelines(),
        api.getDailyMealAnalysis()
      ]);

      setTodaysMeals(todaysData.meals || { breakfast: [], lunch: [], dinner: [], snack: [] });
      setWeeklyPattern(weeklyData.pattern || []);
      setWeeklyCounts(weeklyCountsData || []);
      setMoodCorrelations(correlationsData.correlations || []);
      setMoodInsights(insightsData || { insights: [], top_positive_foods: [], foods_to_moderate: [], recommendations: [] });
      setAyurvedaGuidelines(guidelinesData || []);
      setDailyAnalysis(dailyAnalysisData || null);
      
    } catch (error) {
      console.error('Error loading data:', error);
      setMealError('Failed to load meal data');
    } finally {
      setLoading(false);
    }
  };

  const handleLogMeal = async () => {
    if (!newMealText.trim()) {
      setMealError('Please describe what you ate');
      return;
    }

    try {
      setSavingMeal(true);
      setMealError(null);

      const mealData = {
        meal_text: newMealText.trim(),
        meal_type: newMealType,
        meal_time: new Date().toISOString(),
        notes: newMealNotes.trim()
      };

      console.log('Logging meal:', mealData);
      const response = await api.logMeal(mealData);
      console.log('Meal log response:', response);
      
      // Backend returns an object with success, message, meal, and analysis
      // Store the analysis
      const analysisData = (response as any).analysis || null;
      if (analysisData) {
        setMealAnalysis(analysisData);
      }
      
      setMealSuccess('Meal logged and analyzed successfully! Check Ayurvedic Guidance below.');
      
      // Refresh all data including mood correlations and daily analysis
      const [todaysData, guidelinesData, weeklyCountsData, correlationsData, insightsData, dailyAnalysisData] = await Promise.all([
        api.getTodayMealsFormatted(),
        api.getAyurvedaGuidelines(),
        api.getWeeklyCounts(),
        api.getMoodCorrelationsWithDays(30),
        api.getMoodInsights(),
        api.getDailyMealAnalysis()
      ]);
      
      setTodaysMeals(todaysData.meals || { breakfast: [], lunch: [], dinner: [], snack: [] });
      setAyurvedaGuidelines(guidelinesData || []);
      setWeeklyCounts(weeklyCountsData || []);
      setMoodCorrelations(correlationsData.correlations || []);
      setMoodInsights(insightsData || { insights: [], top_positive_foods: [], foods_to_moderate: [], recommendations: [] });
      setDailyAnalysis(dailyAnalysisData || null);

      // Reset form
      setNewMealText('');
      setNewMealNotes('');
      
      setTimeout(() => setMealSuccess(null), 5000);
    } catch (error: any) {
      console.error('Failed to log meal:', error);
      const errorMsg = error.response?.data?.detail || error.message || 'Failed to log meal';
      setMealError(errorMsg);
    } finally {
      setSavingMeal(false);
    }
  };

  const handleMealClick = (meal: any) => {
    setSelectedMeal(meal);
    setShowMealDetails(true);
  };

  const getMealTypeIcon = (type: string) => {
    switch (type) {
      case 'breakfast': return '🌅';
      case 'lunch': return '☀️';
      case 'dinner': return '🌙';
      case 'snack': return '🍎';
      default: return '🍽️';
    }
  };

  const getMealEmoji = (type: string) => getMealTypeIcon(type);

  const isErrorMessage = (text: string) => {
    if (!text) return false;
    return text.includes('apologize') || 
           text.includes('unable to connect') || 
           text.includes('wellness knowledge base') ||
           text.toLowerCase().includes('error');
  };

  const getMealTypeColor = (mealType: string) => {
    switch (mealType) {
      case 'breakfast':
        return {
          bg: 'from-yellow-50 to-yellow-100',
          border: 'border-yellow-300',
          text: 'text-yellow-900',
          textLight: 'text-yellow-800',
          badge: 'bg-yellow-200 text-yellow-900'
        };
      case 'lunch':
        return {
          bg: 'from-orange-50 to-orange-100',
          border: 'border-orange-300',
          text: 'text-orange-900',
          textLight: 'text-orange-800',
          badge: 'bg-orange-200 text-orange-900'
        };
      case 'dinner':
        return {
          bg: 'from-indigo-50 to-indigo-100',
          border: 'border-indigo-300',
          text: 'text-indigo-900',
          textLight: 'text-indigo-800',
          badge: 'bg-indigo-200 text-indigo-900'
        };
      case 'snack':
        return {
          bg: 'from-green-50 to-green-100',
          border: 'border-green-300',
          text: 'text-green-900',
          textLight: 'text-green-800',
          badge: 'bg-green-200 text-green-900'
        };
      default:
        return {
          bg: 'from-gray-50 to-gray-100',
          border: 'border-gray-300',
          text: 'text-gray-900',
          textLight: 'text-gray-800',
          badge: 'bg-gray-200 text-gray-900'
        };
    }
  };

  const getCorrelationColor = (correlation: number) => {
    if (correlation > 0.7) return 'text-green-600';
    if (correlation > 0.3) return 'text-yellow-600';
    return 'text-red-600';
  };

  const generateWeeklyMealData = () => {
    const daysOfWeek = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'];
    
    if (!weeklyCounts || weeklyCounts.length === 0) {
      // Return empty data for 7 days if no data available
      return Array.from({ length: 7 }, (_, i) => ({
        day: daysOfWeek[i],
        meals: 0,
        breakfast: 0,
        lunch: 0,
        dinner: 0,
        snack: 0
      }));
    }
    
    return weeklyCounts.map(dayData => ({
      day: daysOfWeek[new Date(dayData.date).getDay()],
      meals: dayData.total_meals,
      date: dayData.date,
      breakfast: dayData.breakfast,
      lunch: dayData.lunch,
      dinner: dayData.dinner,
      snack: dayData.snack
    }));
  };

  const getWeeklyMealTotal = () => {
    const weekData = generateWeeklyMealData();
    return weekData.reduce((total, day) => total + day.meals, 0);
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-purple-50 via-white to-pink-50">
        <Navigation 
          currentPage="diet-mood" 
          onNavigate={onNavigate}
          onLogout={onLogout}
          onOpenNotifications={onOpenNotifications}
        />
        <div className="flex items-center justify-center h-screen">
          <div className="text-center">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-purple-600 mx-auto mb-4"></div>
            <p className="text-gray-600">Loading your meal data...</p>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-purple-50 via-white to-pink-50">
      <Navigation 
        currentPage="diet-mood" 
        onNavigate={onNavigate}
        onLogout={onLogout}
        onOpenNotifications={onOpenNotifications}
      />

      <div className="container mx-auto px-4 py-8 pt-20">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6 }}
          className="max-w-7xl mx-auto"
        >
          {/* Header */}
          <div className="text-center mb-8">
            <h1 className="text-3xl font-bold text-gray-900 mb-2">Diet & Mood Sync</h1>
            <p className="text-gray-600">Track your meals and discover how food affects your wellbeing</p>
          </div>

          {/* Meal Logging Form */}
          <Card className="mb-8">
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <ChefHat className="w-5 h-5" />
                Log a Meal
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium mb-2">Meal Type</label>
                  <Select value={newMealType} onValueChange={(value: any) => setNewMealType(value)}>
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="breakfast">🌅 Breakfast</SelectItem>
                      <SelectItem value="lunch">☀️ Lunch</SelectItem>
                      <SelectItem value="dinner">🌙 Dinner</SelectItem>
                      <SelectItem value="snack">🍎 Snack</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
                
                <div>
                  <label className="block text-sm font-medium mb-2">What did you eat?</label>
                  <Input
                    placeholder="e.g., Grilled chicken with vegetables and rice"
                    value={newMealText}
                    onChange={(e) => setNewMealText(e.target.value)}
                  />
                </div>
                
                <div className="md:col-span-2">
                  <label className="block text-sm font-medium mb-2">Notes (optional)</label>
                  <Textarea
                    placeholder="How did you feel? Any observations?"
                    value={newMealNotes}
                    onChange={(e) => setNewMealNotes(e.target.value)}
                    rows={3}
                  />
                </div>
              </div>
              
              {mealError && (
                <div className="mt-4 p-3 bg-red-50 border border-red-200 rounded-md">
                  <p className="text-red-600 text-sm">{mealError}</p>
                </div>
              )}
              
              {mealSuccess && (
                <div className="mt-4 p-3 bg-green-50 border border-green-200 rounded-md">
                  <p className="text-green-600 text-sm">{mealSuccess}</p>
                </div>
              )}
              
              <Button 
                onClick={handleLogMeal}
                disabled={savingMeal}
                className="mt-4"
              >
                {savingMeal ? 'Analyzing...' : 'Log Meal & Analyze'}
              </Button>
            </CardContent>
          </Card>

          {/* Today's Meal Log */}
          <Card className="mb-8">
            <CardHeader>
              <CardTitle className="flex items-center gap-2 text-lg">
                <UtensilsCrossed className="w-6 h-6 text-green-600" />
                Today's Meal Log
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {Object.entries(todaysMeals).map(([mealType, meals]) => {
                  const colors = getMealTypeColor(mealType);
                  return meals.length > 0 && meals.map((meal: any) => {
                    const hasValidIngredients = meal.ingredients && meal.ingredients.length > 0 && !isErrorMessage(meal.ingredients[0]);
                    const hasValidMealText = meal.meal_text && !isErrorMessage(meal.meal_text);
                    
                    return (
                      <div 
                        key={meal.id} 
                        className={`p-5 bg-gradient-to-br ${colors.bg} rounded-lg border ${colors.border} hover:shadow-lg transition-shadow cursor-pointer`}
                        onClick={() => handleMealClick(meal)}
                      >
                        <div className="flex items-start justify-between mb-3">
                          <div className="flex-1">
                            <div className="flex items-center gap-2 mb-1">
                              <h3 className={`font-bold ${colors.text} text-base`}>
                                {getMealEmoji(mealType)} {mealType.charAt(0).toUpperCase() + mealType.slice(1)}
                              </h3>
                              <span className="text-sm text-gray-600">
                                {new Date(meal.meal_time).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                              </span>
                            </div>
                            <div className="space-y-1 mt-2">
                              {hasValidIngredients ? (
                                meal.ingredients.slice(0, 5).map((ingredient: string, idx: number) => (
                                  <p key={idx} className={`text-sm ${colors.textLight}`}>• {ingredient}</p>
                                ))
                              ) : hasValidMealText ? (
                                <p className={`text-sm ${colors.textLight}`}>{meal.meal_text}</p>
                              ) : (
                                <p className="text-sm text-gray-500 italic">Meal details unavailable</p>
                              )}
                            </div>
                          </div>
                        
                          {/* Dosha Badge */}
                          {meal.dosha_impact_tags && (
                            <div className="ml-3">
                              {meal.dosha_impact_tags.vata === 'increase' && (
                                <Badge className="bg-blue-100 text-blue-800 border border-blue-300">Vata balancing</Badge>
                              )}
                              {meal.dosha_impact_tags.pitta === 'increase' && (
                                <Badge className="bg-red-100 text-red-800 border border-red-300">Pitta cooling</Badge>
                              )}
                              {meal.dosha_impact_tags.kapha === 'increase' && (
                                <Badge className="bg-yellow-100 text-yellow-800 border border-yellow-300">Kapha reducing</Badge>
                              )}
                              {meal.dosha_impact_tags.vata === 'decrease' && (
                                <Badge className="bg-blue-100 text-blue-800 border border-blue-300">Vata balancing</Badge>
                              )}
                              {meal.dosha_impact_tags.pitta === 'decrease' && (
                                <Badge className="bg-red-100 text-red-800 border border-red-300">Pitta cooling</Badge>
                              )}
                              {meal.dosha_impact_tags.kapha === 'decrease' && (
                                <Badge className="bg-yellow-100 text-yellow-800 border border-yellow-300">Kapha reducing</Badge>
                              )}
                            </div>
                          )}
                        </div>
                        
                        {/* Mood Indicator */}
                        {meal.mood_after && (
                          <div className={`flex items-center justify-between mt-3 pt-3 border-t ${colors.border}`}>
                            <span className={`text-sm ${colors.textLight} font-medium`}>
                              Mood after: {meal.mood_after}
                            </span>
                            <div className="flex gap-1">
                              {[...Array(10)].map((_, i) => (
                                <div 
                                  key={i} 
                                  className={`w-2 h-2 rounded-full ${
                                    i < (meal.mood_intensity || 7) ? 'bg-green-500' : 'bg-gray-300'
                                  }`}
                                />
                              ))}
                            </div>
                          </div>
                        )}
                      </div>
                    );
                  });
                })}
                
                {Object.values(todaysMeals).every((meals: any) => meals.length === 0) && (
                  <div className="text-center py-8">
                    <p className="text-gray-500 text-base">No meals logged today</p>
                  </div>
                )}
              </div>
            </CardContent>
          </Card>

          <div className="mb-8">
            {/* Ayurveda Guidelines */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <AlertCircle className="w-5 h-5" />
                  Ayurvedic Guidance
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  <h3 className="font-bold text-xl text-purple-900 mb-4">Personalized Analysis</h3>
                  
                  {/* Latest Meal Analysis */}
                  {mealAnalysis && (
                    <div className="space-y-3 mb-6 pb-6 border-b-2 border-purple-200">
                      
                      {/* Show Logged Meal Info */}
                      {mealAnalysis.meal && (
                        <div className={`p-4 rounded-lg border-l-4 ${
                          mealAnalysis.meal.meal_type === 'breakfast' ? 'bg-gradient-to-r from-yellow-50 to-yellow-100 border-yellow-500' :
                          mealAnalysis.meal.meal_type === 'lunch' ? 'bg-gradient-to-r from-orange-50 to-orange-100 border-orange-500' :
                          mealAnalysis.meal.meal_type === 'dinner' ? 'bg-gradient-to-r from-indigo-50 to-indigo-100 border-indigo-500' :
                          'bg-gradient-to-r from-green-50 to-green-100 border-green-500'
                        }`}>
                          <div className="flex items-center justify-between mb-2">
                            <h4 className={`font-bold text-base ${
                              mealAnalysis.meal.meal_type === 'breakfast' ? 'text-yellow-900' :
                              mealAnalysis.meal.meal_type === 'lunch' ? 'text-orange-900' :
                              mealAnalysis.meal.meal_type === 'dinner' ? 'text-indigo-900' :
                              'text-green-900'
                            }`}>
                              {getMealEmoji(mealAnalysis.meal.meal_type)} {mealAnalysis.meal.meal_type.charAt(0).toUpperCase() + mealAnalysis.meal.meal_type.slice(1)}
                            </h4>
                            <span className={`text-xs ${
                              mealAnalysis.meal.meal_type === 'breakfast' ? 'text-yellow-700' :
                              mealAnalysis.meal.meal_type === 'lunch' ? 'text-orange-700' :
                              mealAnalysis.meal.meal_type === 'dinner' ? 'text-indigo-700' :
                              'text-green-700'
                            }`}>
                              {new Date(mealAnalysis.meal.meal_time).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                            </span>
                          </div>
                          <p className={`text-sm font-medium mb-1 ${
                            mealAnalysis.meal.meal_type === 'breakfast' ? 'text-yellow-800' :
                            mealAnalysis.meal.meal_type === 'lunch' ? 'text-orange-800' :
                            mealAnalysis.meal.meal_type === 'dinner' ? 'text-indigo-800' :
                            'text-green-800'
                          }`}>{mealAnalysis.meal.meal_text}</p>
                          {mealAnalysis.meal.ingredients && mealAnalysis.meal.ingredients.length > 0 && (
                            <div className="flex flex-wrap gap-1 mt-2">
                              {mealAnalysis.meal.ingredients.slice(0, 5).map((ingredient: string, i: number) => (
                                <Badge key={i} className={`text-xs ${
                                  mealAnalysis.meal.meal_type === 'breakfast' ? 'bg-yellow-200 text-yellow-900' :
                                  mealAnalysis.meal.meal_type === 'lunch' ? 'bg-orange-200 text-orange-900' :
                                  mealAnalysis.meal.meal_type === 'dinner' ? 'bg-indigo-200 text-indigo-900' :
                                  'bg-green-200 text-green-900'
                                }`}>{ingredient}</Badge>
                              ))}
                            </div>
                          )}
                        </div>
                      )}
                      
                      {/* Health Assessment */}
                      {mealAnalysis.health_assessment && (
                        <div className="p-4 bg-gradient-to-r from-blue-50 to-blue-100 border-l-4 border-blue-500 rounded-lg">
                          <div className="flex items-center justify-between mb-2">
                            <h4 className="font-bold text-base text-blue-900">
                              {mealAnalysis.health_assessment.is_healthy ? '✅' : '⚠️'} Health Assessment
                            </h4>
                            <Badge variant={mealAnalysis.health_assessment.is_healthy ? "default" : "destructive"} className="text-sm">
                              {mealAnalysis.health_assessment.health_score}/100
                            </Badge>
                          </div>
                          <p className="text-sm text-blue-800">{mealAnalysis.health_assessment.summary}</p>
                          <div className="grid grid-cols-2 gap-2 mt-2">
                            {mealAnalysis.health_assessment.strengths?.length > 0 && (
                              <div>
                                <p className="text-xs font-semibold text-green-700">Strengths:</p>
                                <ul className="text-xs text-green-600">
                                  {mealAnalysis.health_assessment.strengths.slice(0, 2).map((s: string, i: number) => (
                                    <li key={i}>• {s}</li>
                                  ))}
                                </ul>
                              </div>
                            )}
                            {mealAnalysis.health_assessment.concerns?.length > 0 && (
                              <div>
                                <p className="text-xs font-semibold text-orange-700">Areas to Improve:</p>
                                <ul className="text-xs text-orange-600">
                                  {mealAnalysis.health_assessment.concerns.slice(0, 2).map((c: string, i: number) => (
                                    <li key={i}>• {c}</li>
                                  ))}
                                </ul>
                              </div>
                            )}
                          </div>
                        </div>
                      )}

                      {/* Mood Recommendations */}
                      {mealAnalysis.mood_recommendations && (
                        <div className="p-4 bg-gradient-to-r from-pink-50 to-pink-100 border-l-4 border-pink-500 rounded-lg">
                          <h4 className="font-bold text-base text-pink-900 mb-1">🧠 Mood-Based Recommendations</h4>
                          <p className="text-sm text-pink-800 mb-2">{mealAnalysis.mood_recommendations.mood_impact}</p>
                          {mealAnalysis.mood_recommendations.foods_to_add?.length > 0 && (
                            <div>
                              <p className="text-xs font-semibold text-pink-700 mb-1">Foods to boost your mood:</p>
                              <div className="flex flex-wrap gap-1">
                                {mealAnalysis.mood_recommendations.foods_to_add.slice(0, 3).map((food: string, i: number) => (
                                  <Badge key={i} className="bg-pink-200 text-pink-900 text-xs px-2 py-0.5">{food}</Badge>
                                ))}
                              </div>
                            </div>
                          )}
                        </div>
                      )}

                      {/* Ayurvedic Analysis */}
                      {mealAnalysis.ayurvedic_analysis && (
                        <div className="p-4 bg-gradient-to-r from-purple-50 to-purple-100 border-l-4 border-purple-500 rounded-lg">
                          <h4 className="font-bold text-base text-purple-900 mb-1">🌿 Ayurvedic Analysis</h4>
                          <p className="text-sm text-purple-800">{mealAnalysis.ayurvedic_analysis.dosha_effects}</p>
                          {mealAnalysis.ayurvedic_analysis.timing_advice && (
                            <p className="text-xs text-purple-700 mt-1">⏰ {mealAnalysis.ayurvedic_analysis.timing_advice}</p>
                          )}
                        </div>
                      )}

                      {/* Better Alternatives */}
                      {mealAnalysis.alternatives && (mealAnalysis.alternatives.better_choices?.length > 0 || mealAnalysis.alternatives.complementary_foods?.length > 0) && (
                        <div className="p-4 bg-gradient-to-r from-green-50 to-green-100 border-l-4 border-green-500 rounded-lg">
                          <h4 className="font-bold text-base text-green-900 mb-2">💡 Better Alternatives</h4>
                          {mealAnalysis.alternatives.better_choices?.length > 0 && (
                            <div className="mb-2">
                              <p className="text-xs font-semibold text-green-700 mb-1">Healthier Options:</p>
                              <div className="flex flex-wrap gap-1">
                                {mealAnalysis.alternatives.better_choices.slice(0, 2).map((choice: string, i: number) => (
                                  <Badge key={i} variant="outline" className="bg-green-50 text-green-800 border-green-300 text-xs px-2 py-0.5">{choice}</Badge>
                                ))}
                              </div>
                            </div>
                          )}
                          {mealAnalysis.alternatives.complementary_foods?.length > 0 && (
                            <div>
                              <p className="text-xs font-semibold text-green-700 mb-1">Add for balance:</p>
                              <div className="flex flex-wrap gap-1">
                                {mealAnalysis.alternatives.complementary_foods.slice(0, 2).map((food: string, i: number) => (
                                  <Badge key={i} className="bg-green-200 text-green-900 text-xs px-2 py-0.5">{food}</Badge>
                                ))}
                              </div>
                            </div>
                          )}
                        </div>
                      )}

                      {/* Dietary Guidance */}
                      {mealAnalysis.guidance && (
                        <div className="p-4 bg-gradient-to-r from-yellow-50 to-yellow-100 border-l-4 border-yellow-500 rounded-lg">
                          <h4 className="font-bold text-base text-yellow-900 mb-2">📋 Dietary Guidance</h4>
                          <div className="grid grid-cols-2 gap-3">
                            {mealAnalysis.guidance.foods_to_favor?.length > 0 && (
                              <div>
                                <p className="text-xs font-semibold text-green-800 mb-1">✓ Foods to Favor:</p>
                                <ul className="text-xs text-green-700 space-y-0.5">
                                  {mealAnalysis.guidance.foods_to_favor.slice(0, 3).map((food: string, i: number) => (
                                    <li key={i}>• {food}</li>
                                  ))}
                                </ul>
                              </div>
                            )}
                            {mealAnalysis.guidance.foods_to_avoid?.length > 0 && (
                              <div>
                                <p className="text-xs font-semibold text-red-800 mb-1">✗ Foods to Avoid:</p>
                                <ul className="text-xs text-red-700 space-y-0.5">
                                  {mealAnalysis.guidance.foods_to_avoid.slice(0, 2).map((food: string, i: number) => (
                                    <li key={i}>• {food}</li>
                                  ))}
                                </ul>
                              </div>
                            )}
                          </div>
                          {mealAnalysis.guidance.lifestyle_tips?.length > 0 && (
                            <div className="mt-2 pt-2 border-t border-yellow-200">
                              <p className="text-xs font-semibold text-yellow-800 mb-1">Lifestyle Tips:</p>
                              <ul className="text-xs text-yellow-700">
                                {mealAnalysis.guidance.lifestyle_tips.slice(0, 2).map((tip: string, i: number) => (
                                  <li key={i}>• {tip}</li>
                                ))}
                              </ul>
                            </div>
                          )}
                        </div>
                      )}
                    </div>
                  )}

                  {/* Daily Analysis */}
                  <div>
                    {dailyAnalysis && dailyAnalysis.has_meals ? (
                      <div className="space-y-3">
                        {/* Dosha Impact Summary */}
                        {dailyAnalysis.dosha_impact && (
                          <div className="p-4 bg-gradient-to-r from-purple-50 to-purple-100 border-l-4 border-purple-500 rounded-lg">
                            <h4 className="font-bold text-base text-purple-900 mb-1 flex items-center gap-2">
                              🔮 Dosha Impact Summary
                            </h4>
                            <p className="text-sm text-purple-800 mb-1">{dailyAnalysis.dosha_impact.summary}</p>
                            <div className="flex gap-2 mt-2">
                              <Badge className={`text-xs ${
                                dailyAnalysis.dosha_impact.primary_dosha === 'vata' ? 'bg-blue-100 text-blue-800' :
                                dailyAnalysis.dosha_impact.primary_dosha === 'pitta' ? 'bg-red-100 text-red-800' :
                                'bg-yellow-100 text-yellow-800'
                              }`}>
                                {dailyAnalysis.dosha_impact.primary_dosha?.toUpperCase()} {dailyAnalysis.dosha_impact.effect}
                              </Badge>
                            </div>
                          </div>
                        )}

                        {/* Healthiness Assessment */}
                        {dailyAnalysis.healthiness && (
                          <div className="p-4 bg-gradient-to-r from-green-50 to-green-100 border-l-4 border-green-500 rounded-lg">
                            <div className="flex items-center justify-between mb-1">
                              <h4 className="font-bold text-base text-green-900">💚 Healthiness Assessment</h4>
                              <Badge className="bg-green-200 text-green-900 text-xs">
                                {dailyAnalysis.healthiness.overall_score}/100
                              </Badge>
                            </div>
                            <p className="text-sm text-green-800 mb-2">{dailyAnalysis.healthiness.assessment}</p>
                            {dailyAnalysis.healthiness.qualities && dailyAnalysis.healthiness.qualities.length > 0 && (
                              <div className="flex flex-wrap gap-1">
                                {dailyAnalysis.healthiness.qualities.map((quality: string, i: number) => (
                                  <Badge key={i} variant="outline" className="text-xs bg-green-50 text-green-700 border-green-300">
                                    {quality}
                                  </Badge>
                                ))}
                              </div>
                            )}
                          </div>
                        )}

                        {/* Ingredient Insights */}
                        {dailyAnalysis.ingredient_insights && (
                          <div className="p-4 bg-gradient-to-r from-blue-50 to-blue-100 border-l-4 border-blue-500 rounded-lg">
                            <h4 className="font-bold text-base text-blue-900 mb-2">🌿 Ingredient Insights</h4>
                            <div className="grid grid-cols-2 gap-3">
                              {dailyAnalysis.ingredient_insights.positive?.length > 0 && (
                                <div>
                                  <p className="text-xs font-semibold text-green-700 mb-1">✓ Beneficial:</p>
                                  <ul className="text-xs text-green-600 space-y-0.5">
                                    {dailyAnalysis.ingredient_insights.positive.slice(0, 2).map((item: string, i: number) => (
                                      <li key={i}>• {item}</li>
                                    ))}
                                  </ul>
                                </div>
                              )}
                              {dailyAnalysis.ingredient_insights.negative?.length > 0 && (
                                <div>
                                  <p className="text-xs font-semibold text-orange-700 mb-1">⚠ Watch out:</p>
                                  <ul className="text-xs text-orange-600 space-y-0.5">
                                    {dailyAnalysis.ingredient_insights.negative.slice(0, 2).map((item: string, i: number) => (
                                      <li key={i}>• {item}</li>
                                    ))}
                                  </ul>
                                </div>
                              )}
                            </div>
                          </div>
                        )}

                        {/* Mood Interpretation */}
                        {dailyAnalysis.mood_interpretation && (
                          <div className="p-4 bg-gradient-to-r from-pink-50 to-pink-100 border-l-4 border-pink-500 rounded-lg">
                            <h4 className="font-bold text-base text-pink-900 mb-1">🧠 Mood-Food Connection</h4>
                            <p className="text-sm text-pink-800">{dailyAnalysis.mood_interpretation}</p>
                          </div>
                        )}

                        {/* Recommended Adjustments */}
                        {dailyAnalysis.adjustments && (
                          <div className="p-4 bg-gradient-to-r from-yellow-50 to-yellow-100 border-l-4 border-yellow-500 rounded-lg">
                            <h4 className="font-bold text-base text-yellow-900 mb-3">📋 Recommended Adjustments</h4>
                            
                            {/* Next Meal Suggestions */}
                            {dailyAnalysis.adjustments.next_meal_suggestions?.length > 0 && (
                              <div className="mb-3 p-3 bg-white/50 rounded-md">
                                <p className="text-xs font-bold text-yellow-900 mb-2 flex items-center gap-1">
                                  <span className="text-base">🍽️</span> For Your Next Meals:
                                </p>
                                <ul className="text-xs text-yellow-800 space-y-1.5">
                                  {dailyAnalysis.adjustments.next_meal_suggestions.slice(0, 3).map((suggestion: string, i: number) => (
                                    <li key={i} className="flex items-start gap-2">
                                      <span className="text-yellow-600 font-bold mt-0.5">•</span>
                                      <span className="flex-1">{suggestion}</span>
                                    </li>
                                  ))}
                                </ul>
                              </div>
                            )}
                            
                            {/* Foods to Add and Reduce */}
                            <div className="grid grid-cols-1 gap-3">
                              {dailyAnalysis.adjustments.foods_to_add?.length > 0 && (
                                <div className="p-3 bg-green-50 border border-green-200 rounded-md">
                                  <p className="text-xs font-bold text-green-800 mb-2 flex items-center gap-1">
                                    <span className="text-base">✅</span> Foods to Add:
                                  </p>
                                  <div className="space-y-1.5">
                                    {dailyAnalysis.adjustments.foods_to_add.slice(0, 3).map((food: string, i: number) => {
                                      const [foodName, reason] = food.includes(' - ') ? food.split(' - ') : [food, ''];
                                      return (
                                        <div key={i} className="text-xs">
                                          <span className="font-semibold text-green-900">{foodName}</span>
                                          {reason && <span className="text-green-700 block ml-3 mt-0.5">→ {reason}</span>}
                                        </div>
                                      );
                                    })}
                                  </div>
                                </div>
                              )}
                              
                              {dailyAnalysis.adjustments.foods_to_reduce?.length > 0 && (
                                <div className="p-3 bg-red-50 border border-red-200 rounded-md">
                                  <p className="text-xs font-bold text-red-800 mb-2 flex items-center gap-1">
                                    <span className="text-base">⚠️</span> Foods to Reduce:
                                  </p>
                                  <div className="space-y-1.5">
                                    {dailyAnalysis.adjustments.foods_to_reduce.slice(0, 3).map((food: string, i: number) => {
                                      const [foodName, reason] = food.includes(' - ') ? food.split(' - ') : [food, ''];
                                      return (
                                        <div key={i} className="text-xs">
                                          <span className="font-semibold text-red-900">{foodName}</span>
                                          {reason && <span className="text-red-700 block ml-3 mt-0.5">→ {reason}</span>}
                                        </div>
                                      );
                                    })}
                                  </div>
                                </div>
                              )}
                            </div>
                          </div>
                        )}

                        {/* Daily Balance Recommendation */}
                        {dailyAnalysis.daily_balance && (
                          <div className="p-4 bg-gradient-to-r from-indigo-50 to-indigo-100 border-l-4 border-indigo-500 rounded-lg">
                            <h4 className="font-bold text-base text-indigo-900 mb-1">⚖️ Daily Balance Focus</h4>
                            <p className="text-sm text-indigo-800 font-medium">{dailyAnalysis.daily_balance}</p>
                          </div>
                        )}
                      </div>
                    ) : (
                      <div className="text-center py-6">
                        <p className="text-gray-500 text-sm">
                          {dailyAnalysis?.message || 'Log meals to receive personalized Ayurvedic guidance'}
                        </p>
                      </div>
                    )}
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>

          {/* Charts Section */}
          {(weeklyPattern.length > 0 || moodCorrelations.length > 0 || Object.values(todaysMeals).some(meals => meals.length > 0)) && (
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 mb-8">
              {/* Date vs Number of Meals Chart - Weekly View */}
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <Calendar className="w-5 h-5" />
                    Weekly Meal Count
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="h-64">
                    <ResponsiveContainer width="100%" height="100%">
                      <BarChart data={generateWeeklyMealData()}>
                        <CartesianGrid strokeDasharray="3 3" />
                        <XAxis dataKey="day" />
                        <YAxis />
                        <Tooltip />
                        <Legend />
                        <Bar dataKey="breakfast" fill="#FFA500" name="Breakfast" />
                        <Bar dataKey="lunch" fill="#32CD32" name="Lunch" />
                        <Bar dataKey="dinner" fill="#4169E1" name="Dinner" />
                        <Bar dataKey="snack" fill="#FF69B4" name="Snacks" />
                      </BarChart>
                    </ResponsiveContainer>
                  </div>
                  <div className="mt-4 text-center">
                    <p className="text-sm text-gray-600">
                      Total meals this week: {getWeeklyMealTotal()}
                    </p>
                  </div>
                </CardContent>
              </Card>

              {/* Mood-Meal Correlation Chart */}
              {moodCorrelations.length > 0 && (
                <Card>
                  <CardHeader>
                    <CardTitle className="flex items-center gap-2">
                      <TrendingUp className="w-5 h-5" />
                      Food-Mood Correlations
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="h-64">
                      <ResponsiveContainer width="100%" height="100%">
                        <BarChart data={moodCorrelations.slice(0, 6).map((corr: any) => ({
                          food: corr.food_item || corr.ingredient,
                          correlation: Math.round((corr.positive_correlation || corr.correlation_score || 0) * 100),
                          count: corr.meals_count || corr.frequency || 1
                        }))}>
                          <CartesianGrid strokeDasharray="3 3" />
                          <XAxis dataKey="food" angle={-45} textAnchor="end" height={80} />
                          <YAxis label={{ value: 'Mood Impact (%)', angle: -90, position: 'insideLeft' }} />
                          <Tooltip formatter={(value, name) => [`${value}%`, 'Mood Impact']} />
                          <Bar dataKey="correlation" fill="#8884d8" />
                        </BarChart>
                      </ResponsiveContainer>
                    </div>
                  </CardContent>
                </Card>
              )}
            </div>
          )}

          {/* Meal Details Dialog */}
          <Dialog open={showMealDetails} onOpenChange={setShowMealDetails}>
            <DialogContent className="max-w-md">
              <DialogHeader>
                <DialogTitle>Meal Details</DialogTitle>
              </DialogHeader>
              {selectedMeal && (
                <div className="space-y-4">
                  <div>
                    <h4 className="font-medium text-gray-800">What you ate:</h4>
                    <p className="text-gray-600">{selectedMeal.meal_text}</p>
                  </div>
                  
                  <div>
                    <h4 className="font-medium text-gray-800">Time:</h4>
                    <p className="text-gray-600">
                      {new Date(selectedMeal.meal_time).toLocaleString()}
                    </p>
                  </div>
                  
                  {selectedMeal.notes && (
                    <div>
                      <h4 className="font-medium text-gray-800">Notes:</h4>
                      <p className="text-gray-600">{selectedMeal.notes}</p>
                    </div>
                  )}
                  
                  {selectedMeal.extracted_ingredients && (
                    <div>
                      <h4 className="font-medium text-gray-800">Detected ingredients:</h4>
                      <div className="flex flex-wrap gap-1 mt-1">
                        {JSON.parse(selectedMeal.extracted_ingredients).slice(0, 10).map((ingredient: string, index: number) => (
                          <Badge key={index} variant="secondary" className="text-xs">
                            {ingredient}
                          </Badge>
                        ))}
                      </div>
                    </div>
                  )}
                </div>
              )}
            </DialogContent>
          </Dialog>
        </motion.div>
      </div>
    </div>
  );
}