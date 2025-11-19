import { useState } from 'react';
import { motion } from 'motion/react';
import { UtensilsCrossed, TrendingUp, AlertCircle, ChefHat } from 'lucide-react';
import { Navigation } from './Navigation';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { Badge } from './ui/badge';
import { Button } from './ui/button';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogDescription } from './ui/dialog';
import { LineChart, Line, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import type { PageType, User } from '../App';

interface DietMoodPageProps {
  user: User | null;
  onNavigate: (page: PageType) => void;
}

export function DietMoodPage({ user, onNavigate }: DietMoodPageProps) {
  const [showRecipe, setShowRecipe] = useState(false);
  const [selectedRecipe, setSelectedRecipe] = useState<any>(null);

  // Mock data for meal-mood correlation
  const correlationData = [
    { day: 'Mon', mood: 7, meals: 3, quality: 8 },
    { day: 'Tue', mood: 6, meals: 3, quality: 6 },
    { day: 'Wed', mood: 8, meals: 4, quality: 9 },
    { day: 'Thu', mood: 5, meals: 2, quality: 4 },
    { day: 'Fri', mood: 9, meals: 3, quality: 9 },
    { day: 'Sat', mood: 8, meals: 4, quality: 8 },
    { day: 'Sun', mood: 7, meals: 3, quality: 7 },
  ];

  const mealLogs = [
    {
      time: '8:00 AM',
      meal: 'Breakfast',
      items: ['Oatmeal with berries', 'Green tea', 'Almonds'],
      dosha: 'Vata balancing',
      mood: 'Energetic',
      moodScore: 8,
    },
    {
      time: '1:00 PM',
      meal: 'Lunch',
      items: ['Quinoa salad', 'Grilled vegetables', 'Lentil soup'],
      dosha: 'Pitta cooling',
      mood: 'Calm',
      moodScore: 7,
    },
    {
      time: '7:00 PM',
      meal: 'Dinner',
      items: ['Steamed fish', 'Brown rice', 'Cucumber raita'],
      dosha: 'Kapha reducing',
      mood: 'Satisfied',
      moodScore: 8,
    },
  ];

  const doshaFoods = {
    vata: {
      avoid: ['Cold drinks', 'Raw vegetables', 'Dry snacks'],
      favor: ['Warm soups', 'Cooked grains', 'Sweet fruits'],
      color: 'text-blue-700',
      bg: 'bg-blue-50',
    },
    pitta: {
      avoid: ['Spicy food', 'Fried items', 'Citrus fruits'],
      favor: ['Cooling foods', 'Sweet fruits', 'Coconut water'],
      color: 'text-orange-700',
      bg: 'bg-orange-50',
    },
    kapha: {
      avoid: ['Heavy foods', 'Dairy products', 'Oily items'],
      favor: ['Light meals', 'Spices', 'Leafy greens'],
      color: 'text-green-700',
      bg: 'bg-green-50',
    },
  };

  const recipes = [
    {
      id: 1,
      name: 'Ayurvedic Golden Milk',
      dosha: 'Vata',
      ingredients: ['Turmeric', 'Warm milk', 'Honey', 'Cinnamon'],
      benefits: 'Calming, anti-inflammatory, aids sleep',
      prepTime: '5 min',
    },
    {
      id: 2,
      name: 'Cooling Cucumber Raita',
      dosha: 'Pitta',
      ingredients: ['Cucumber', 'Yogurt', 'Mint', 'Cumin'],
      benefits: 'Cooling, digestive, refreshing',
      prepTime: '10 min',
    },
    {
      id: 3,
      name: 'Spiced Quinoa Bowl',
      dosha: 'Kapha',
      ingredients: ['Quinoa', 'Ginger', 'Vegetables', 'Black pepper'],
      benefits: 'Energizing, light, metabolism boost',
      prepTime: '20 min',
    },
  ];

  const handleRecipeClick = (recipe: any) => {
    setSelectedRecipe(recipe);
    setShowRecipe(true);
  };

  return (
    <div className="min-h-screen">
      <Navigation currentPage="diet" onNavigate={onNavigate} user={user} />

      <div className="max-w-7xl mx-auto p-8">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="mb-8"
        >
          <h1 className="mb-2">Diet & Mood Sync</h1>
          <p className="text-gray-600">Understand how your food affects your emotions</p>
        </motion.div>

        {/* Mood Correlation Chart */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1 }}
          className="mb-6"
        >
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <TrendingUp className="w-5 h-5 text-purple-600" />
                Meal-Mood Correlation
              </CardTitle>
            </CardHeader>
            <CardContent>
              <ResponsiveContainer width="100%" height={300}>
                <LineChart data={correlationData}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="day" />
                  <YAxis />
                  <Tooltip />
                  <Legend />
                  <Line type="monotone" dataKey="mood" stroke="#8b5cf6" strokeWidth={2} name="Mood Score" />
                  <Line type="monotone" dataKey="quality" stroke="#3b82f6" strokeWidth={2} name="Meal Quality" />
                </LineChart>
              </ResponsiveContainer>
              <p className="text-sm text-gray-600 mt-4">
                Your mood tends to improve on days when you eat balanced, quality meals
              </p>
            </CardContent>
          </Card>
        </motion.div>

        <div className="grid md:grid-cols-2 gap-6 mb-6">
          {/* Today's Meal Log */}
          <motion.div
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: 0.2 }}
          >
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <UtensilsCrossed className="w-5 h-5 text-green-600" />
                  Today's Meal Log
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                {mealLogs.map((log, index) => (
                  <motion.div
                    key={index}
                    initial={{ opacity: 0, y: 10 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: 0.3 + index * 0.1 }}
                    className="p-4 rounded-xl bg-gradient-to-br from-green-50 to-teal-50 border border-green-100"
                  >
                    <div className="flex items-start justify-between mb-2">
                      <div>
                        <p className="text-green-700">{log.meal}</p>
                        <p className="text-sm text-gray-600">{log.time}</p>
                      </div>
                      <Badge variant="outline">{log.dosha}</Badge>
                    </div>
                    <ul className="text-sm text-gray-700 space-y-1 mb-3">
                      {log.items.map((item, i) => (
                        <li key={i}>• {item}</li>
                      ))}
                    </ul>
                    <div className="flex items-center justify-between">
                      <span className="text-sm text-gray-600">Mood after: {log.mood}</span>
                      <div className="flex gap-1">
                        {Array.from({ length: 10 }, (_, i) => (
                          <div
                            key={i}
                            className={`w-2 h-2 rounded-full ${
                              i < log.moodScore ? 'bg-green-500' : 'bg-gray-300'
                            }`}
                          />
                        ))}
                      </div>
                    </div>
                  </motion.div>
                ))}
              </CardContent>
            </Card>
          </motion.div>

          {/* Dosha Food Guidelines */}
          <motion.div
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: 0.3 }}
          >
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <AlertCircle className="w-5 h-5 text-orange-600" />
                  Ayurvedic Food Guidelines
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="bg-orange-50 p-4 rounded-lg border border-orange-200">
                  <p className="text-orange-900 mb-2">
                    <strong>Pitta Imbalance Detected</strong>
                  </p>
                  <p className="text-sm text-orange-800">
                    Avoid spicy and fried foods today. Focus on cooling, sweet, and bitter foods.
                  </p>
                </div>

                {Object.entries(doshaFoods).map(([dosha, foods]) => (
                  <motion.div
                    key={dosha}
                    whileHover={{ scale: 1.02 }}
                    className={`p-4 rounded-xl ${foods.bg} border border-opacity-20`}
                  >
                    <h3 className={`${foods.color} capitalize mb-3`}>{dosha} Foods</h3>
                    <div className="space-y-2">
                      <div>
                        <p className="text-sm text-gray-600 mb-1">❌ Avoid:</p>
                        <p className="text-sm text-gray-700">{foods.avoid.join(', ')}</p>
                      </div>
                      <div>
                        <p className="text-sm text-gray-600 mb-1">✅ Favor:</p>
                        <p className="text-sm text-gray-700">{foods.favor.join(', ')}</p>
                      </div>
                    </div>
                  </motion.div>
                ))}
              </CardContent>
            </Card>
          </motion.div>
        </div>

        {/* Recipe Suggestions */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.4 }}
        >
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <ChefHat className="w-5 h-5 text-purple-600" />
                Personalized Recipe Suggestions
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid md:grid-cols-3 gap-4">
                {recipes.map((recipe, index) => (
                  <motion.div
                    key={recipe.id}
                    initial={{ opacity: 0, scale: 0.9 }}
                    animate={{ opacity: 1, scale: 1 }}
                    transition={{ delay: 0.5 + index * 0.1 }}
                    whileHover={{ scale: 1.05, y: -5 }}
                    onClick={() => handleRecipeClick(recipe)}
                    className="p-6 rounded-xl bg-gradient-to-br from-purple-50 to-pink-50 border border-purple-100 cursor-pointer"
                  >
                    <div className="text-4xl mb-3">🍲</div>
                    <h3 className="text-purple-900 mb-2">{recipe.name}</h3>
                    <Badge className="mb-3" variant="outline">
                      {recipe.dosha} Balancing
                    </Badge>
                    <p className="text-sm text-gray-600 mb-2">⏱️ {recipe.prepTime}</p>
                    <p className="text-xs text-gray-500">{recipe.benefits}</p>
                  </motion.div>
                ))}
              </div>
            </CardContent>
          </Card>
        </motion.div>

        {/* Weekly Pattern Chart */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.5 }}
          className="mt-6"
        >
          <Card>
            <CardHeader>
              <CardTitle>Weekly Meal Pattern</CardTitle>
            </CardHeader>
            <CardContent>
              <ResponsiveContainer width="100%" height={250}>
                <BarChart data={correlationData}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="day" />
                  <YAxis />
                  <Tooltip />
                  <Legend />
                  <Bar dataKey="meals" fill="#8b5cf6" name="Meals per Day" />
                </BarChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>
        </motion.div>
      </div>

      {/* Recipe Detail Dialog */}
      <Dialog open={showRecipe} onOpenChange={setShowRecipe}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>{selectedRecipe?.name}</DialogTitle>
            <DialogDescription>
              {selectedRecipe?.dosha} balancing recipe
            </DialogDescription>
          </DialogHeader>
          {selectedRecipe && (
            <div className="space-y-4 pt-4">
              <div className="flex gap-2 items-center">
                <Badge>{selectedRecipe.prepTime}</Badge>
                <Badge variant="outline">{selectedRecipe.dosha}</Badge>
              </div>
              
              <div>
                <h4 className="text-sm text-gray-900 mb-2">Ingredients:</h4>
                <ul className="list-disc list-inside text-sm text-gray-700 space-y-1">
                  {selectedRecipe.ingredients.map((ingredient: string, i: number) => (
                    <li key={i}>{ingredient}</li>
                  ))}
                </ul>
              </div>

              <div className="bg-purple-50 p-4 rounded-lg">
                <p className="text-sm text-purple-900">
                  <strong>Benefits:</strong> {selectedRecipe.benefits}
                </p>
              </div>

              <Button className="w-full" onClick={() => setShowRecipe(false)}>
                Got it!
              </Button>
            </div>
          )}
        </DialogContent>
      </Dialog>
    </div>
  );
}
