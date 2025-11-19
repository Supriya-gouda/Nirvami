import { useState } from 'react';
import { motion } from 'motion/react';
import { Sparkles, MessageCircle, Mic, FileText, Palette, Camera, Brain, Heart } from 'lucide-react';
import { Button } from './ui/button';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogDescription } from './ui/dialog';
import { Input } from './ui/input';
import type { User } from '../App';

interface LandingPageProps {
  onLogin: (user: User) => void;
}

export function LandingPage({ onLogin }: LandingPageProps) {
  const [showAbout, setShowAbout] = useState(false);
  const [showLogin, setShowLogin] = useState(false);
  const [userName, setUserName] = useState('');

  const features = [
    { icon: MessageCircle, label: 'Text Chat', color: 'text-blue-500' },
    { icon: Mic, label: 'Voice Input', color: 'text-purple-500' },
    { icon: FileText, label: 'Manual Log', color: 'text-green-500' },
    { icon: Palette, label: 'Mood Board', color: 'text-pink-500' },
    { icon: Camera, label: 'Yoga Poses', color: 'text-orange-500' },
  ];

  const handleLogin = () => {
    if (userName.trim()) {
      onLogin({ name: userName, isGuest: false });
    }
  };

  const handleGuest = () => {
    onLogin({ name: 'Guest', isGuest: true });
  };

  return (
    <div className="min-h-screen flex flex-col items-center justify-center p-8 overflow-hidden relative">
      {/* Animated background elements */}
      <motion.div
        className="absolute top-20 left-10 w-32 h-32 bg-purple-300 rounded-full opacity-20 blur-3xl"
        animate={{
          y: [0, 30, 0],
          scale: [1, 1.2, 1],
        }}
        transition={{
          duration: 8,
          repeat: Infinity,
          ease: "easeInOut"
        }}
      />
      <motion.div
        className="absolute bottom-20 right-10 w-40 h-40 bg-blue-300 rounded-full opacity-20 blur-3xl"
        animate={{
          y: [0, -40, 0],
          scale: [1, 1.3, 1],
        }}
        transition={{
          duration: 10,
          repeat: Infinity,
          ease: "easeInOut"
        }}
      />

      <div className="max-w-5xl w-full z-10">
        {/* Hero Section */}
        <motion.div
          className="text-center mb-16"
          initial={{ opacity: 0, y: -50 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8 }}
        >
          <motion.div
            className="inline-flex items-center gap-2 mb-6"
            animate={{ rotate: [0, 5, -5, 0] }}
            transition={{ duration: 3, repeat: Infinity, ease: "easeInOut" }}
          >
            <Brain className="w-12 h-12 text-purple-600" />
            <Heart className="w-12 h-12 text-pink-600" />
            <Sparkles className="w-12 h-12 text-blue-600" />
          </motion.div>
          
          <h1 className="mb-4 bg-gradient-to-r from-purple-600 via-blue-600 to-pink-600 bg-clip-text text-transparent">
            Intelligent Mental Health Companion
          </h1>
          
          <p className="text-gray-600 max-w-2xl mx-auto mb-8">
            Your personalized AI-powered wellness journey combining ancient Ayurvedic wisdom with modern technology.
            Experience holistic well-being through Yoga, Diet, and Mindfulness.
          </p>

          <div className="flex gap-4 justify-center mb-4">
            <Button onClick={() => setShowLogin(true)} size="lg" className="bg-gradient-to-r from-purple-600 to-blue-600 hover:from-purple-700 hover:to-blue-700">
              Login
            </Button>
            <Button onClick={handleGuest} size="lg" variant="outline">
              Continue as Guest
            </Button>
          </div>

          <button
            onClick={() => setShowAbout(true)}
            className="text-sm text-purple-600 hover:underline"
          >
            Learn More About This Project
          </button>
        </motion.div>

        {/* Features Grid */}
        <motion.div
          className="grid grid-cols-2 md:grid-cols-5 gap-6"
          initial={{ opacity: 0, y: 50 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8, delay: 0.3 }}
        >
          {features.map((feature, index) => {
            const Icon = feature.icon;
            return (
              <motion.div
                key={feature.label}
                className="bg-white/80 backdrop-blur-sm rounded-2xl p-6 shadow-lg hover:shadow-xl transition-shadow"
                initial={{ opacity: 0, scale: 0.8 }}
                animate={{ opacity: 1, scale: 1 }}
                transition={{ duration: 0.5, delay: 0.5 + index * 0.1 }}
                whileHover={{ scale: 1.05, y: -5 }}
              >
                <Icon className={`w-8 h-8 ${feature.color} mx-auto mb-3`} />
                <p className="text-center text-sm text-gray-700">{feature.label}</p>
              </motion.div>
            );
          })}
        </motion.div>

        {/* Floating Info Cards */}
        <motion.div
          className="grid md:grid-cols-3 gap-6 mt-16"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ duration: 0.8, delay: 0.8 }}
        >
          {[
            { title: 'Ayurvedic Wisdom', desc: 'Personalized dosha-based recommendations' },
            { title: 'AI-Powered', desc: 'Intelligent emotion and stress detection' },
            { title: 'Holistic Approach', desc: 'Yoga, Diet, Routine & Sound therapy' },
          ].map((card, index) => (
            <motion.div
              key={card.title}
              className="bg-white/60 backdrop-blur-sm rounded-xl p-6 border border-purple-200"
              whileHover={{ scale: 1.02 }}
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: 1 + index * 0.2 }}
            >
              <h3 className="text-purple-700 mb-2">{card.title}</h3>
              <p className="text-sm text-gray-600">{card.desc}</p>
            </motion.div>
          ))}
        </motion.div>
      </div>

      {/* About Dialog */}
      <Dialog open={showAbout} onOpenChange={setShowAbout}>
        <DialogContent className="max-w-2xl">
          <DialogHeader>
            <DialogTitle>About This Project</DialogTitle>
            <DialogDescription className="space-y-4 pt-4">
              <p>
                The Intelligent Mental Health Companion is an innovative platform that bridges ancient Ayurvedic
                principles with cutting-edge AI technology to provide personalized mental wellness support.
              </p>
              <div className="space-y-2">
                <h4 className="text-sm text-gray-900">Core Features:</h4>
                <ul className="list-disc list-inside text-sm space-y-1">
                  <li>Multi-modal interaction: Text, Voice, Manual logging, Visual mood boards, and Camera-based yoga guidance</li>
                  <li>Emotion and stress detection using advanced ML models</li>
                  <li>Dosha mapping (Vata, Pitta, Kapha) for personalized recommendations</li>
                  <li>AI-powered suggestions for Yoga, Diet, Daily routines, and Sound therapy</li>
                  <li>Aura visualization and predictive wellness alerts</li>
                  <li>Comprehensive progress tracking and analytics</li>
                </ul>
              </div>
              <p>
                This platform combines the wisdom of Yoga and Ayurveda with modern machine learning to help you
                achieve balanced mental and physical well-being.
              </p>
            </DialogDescription>
          </DialogHeader>
        </DialogContent>
      </Dialog>

      {/* Login Dialog */}
      <Dialog open={showLogin} onOpenChange={setShowLogin}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Welcome Back</DialogTitle>
            <DialogDescription>
              Enter your name to access your personalized wellness dashboard
            </DialogDescription>
          </DialogHeader>
          <div className="space-y-4 pt-4">
            <Input
              placeholder="Enter your name"
              value={userName}
              onChange={(e) => setUserName(e.target.value)}
              onKeyPress={(e) => e.key === 'Enter' && handleLogin()}
            />
            <Button onClick={handleLogin} className="w-full" disabled={!userName.trim()}>
              Continue
            </Button>
          </div>
        </DialogContent>
      </Dialog>
    </div>
  );
}
