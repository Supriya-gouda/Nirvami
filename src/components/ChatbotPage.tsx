import { useState, useRef, useEffect } from 'react';
import { motion, AnimatePresence } from 'motion/react';
import { Send, Mic, MicOff, Sparkles } from 'lucide-react';
import { Navigation } from './Navigation';
import { Button } from './ui/button';
import { Input } from './ui/input';
import { Card } from './ui/card';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogDescription } from './ui/dialog';
import type { PageType, User } from '../App';

interface ChatbotPageProps {
  user: User | null;
  onNavigate: (page: PageType) => void;
}

interface Message {
  id: string;
  text: string;
  sender: 'user' | 'bot';
  timestamp: Date;
}

export function ChatbotPage({ user, onNavigate }: ChatbotPageProps) {
  const [messages, setMessages] = useState<Message[]>([
    {
      id: '1',
      text: `Hello ${user?.name}! I'm your AI wellness companion. How are you feeling today?`,
      sender: 'bot',
      timestamp: new Date(),
    },
  ]);
  const [inputValue, setInputValue] = useState('');
  const [isListening, setIsListening] = useState(false);
  const [showVoiceConfirm, setShowVoiceConfirm] = useState(false);
  const [voiceText, setVoiceText] = useState('');
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const suggestedResponses = [
    'I feel anxious',
    'Suggest a yoga routine',
    'What should I eat today?',
    'I need help relaxing',
  ];

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSendMessage = (text: string) => {
    if (!text.trim()) return;

    const userMessage: Message = {
      id: Date.now().toString(),
      text: text.trim(),
      sender: 'user',
      timestamp: new Date(),
    };

    setMessages((prev) => [...prev, userMessage]);
    setInputValue('');

    // Simulate bot response
    setTimeout(() => {
      const botResponse = generateBotResponse(text);
      const botMessage: Message = {
        id: (Date.now() + 1).toString(),
        text: botResponse,
        sender: 'bot',
        timestamp: new Date(),
      };
      setMessages((prev) => [...prev, botMessage]);
    }, 1000);
  };

  const generateBotResponse = (userText: string): string => {
    const lowerText = userText.toLowerCase();
    
    if (lowerText.includes('anxious') || lowerText.includes('stress')) {
      return "I understand you're feeling anxious. Let's work through this together. I recommend a 10-minute breathing exercise (Pranayama) to calm your Vata dosha. Would you like me to guide you through it?";
    }
    if (lowerText.includes('yoga')) {
      return "Based on your current dosha balance, I suggest a gentle Vinyasa flow focusing on grounding poses like Mountain Pose and Tree Pose. This will help balance your energy. Shall I create a personalized sequence for you?";
    }
    if (lowerText.includes('eat') || lowerText.includes('food')) {
      return "For your Pitta constitution, I recommend cooling foods like cucumber, coconut water, and sweet fruits. Avoid spicy and fried foods today. Would you like a detailed meal plan?";
    }
    if (lowerText.includes('relax')) {
      return "Let's focus on relaxation. I recommend practicing Yoga Nidra for 20 minutes, followed by some calming music. Your stress levels will decrease significantly. Should I prepare a relaxation session?";
    }
    
    return "I'm here to help with your wellness journey. I can suggest personalized yoga routines, dietary recommendations, stress management techniques, and mindfulness practices. What would you like to explore?";
  };

  const handleVoiceInput = () => {
    if (!isListening) {
      setIsListening(true);
      // Simulate voice recognition
      setTimeout(() => {
        const simulatedVoiceText = "I'm feeling stressed and need some guidance";
        setVoiceText(simulatedVoiceText);
        setIsListening(false);
        setShowVoiceConfirm(true);
      }, 2000);
    }
  };

  const confirmVoiceMessage = () => {
    handleSendMessage(voiceText);
    setShowVoiceConfirm(false);
    setVoiceText('');
  };

  return (
    <div className="min-h-screen">
      <Navigation currentPage="chatbot" onNavigate={onNavigate} user={user} />

      <div className="max-w-4xl mx-auto p-4 h-[calc(100vh-80px)] flex flex-col">
        {/* Header */}
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          className="mb-4"
        >
          <Card className="p-4 bg-gradient-to-r from-purple-500 to-blue-500 text-white">
            <div className="flex items-center gap-3">
              <motion.div
                animate={{ rotate: 360 }}
                transition={{ duration: 2, repeat: Infinity, ease: "linear" }}
              >
                <Sparkles className="w-6 h-6" />
              </motion.div>
              <div>
                <h2>AI Wellness Companion</h2>
                <p className="text-sm text-purple-100">Powered by Ayurvedic wisdom and modern AI</p>
              </div>
            </div>
          </Card>
        </motion.div>

        {/* Suggested Responses */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          className="mb-4"
        >
          <p className="text-sm text-gray-600 mb-2">Quick suggestions:</p>
          <div className="flex gap-2 flex-wrap">
            {suggestedResponses.map((response, index) => (
              <motion.button
                key={response}
                onClick={() => handleSendMessage(response)}
                className="px-4 py-2 bg-purple-100 text-purple-700 rounded-full text-sm hover:bg-purple-200 transition-colors"
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: index * 0.1 }}
              >
                {response}
              </motion.button>
            ))}
          </div>
        </motion.div>

        {/* Messages */}
        <div className="flex-1 overflow-y-auto mb-4 space-y-4">
          <AnimatePresence>
            {messages.map((message) => (
              <motion.div
                key={message.id}
                initial={{ opacity: 0, y: 20, scale: 0.95 }}
                animate={{ opacity: 1, y: 0, scale: 1 }}
                exit={{ opacity: 0, scale: 0.95 }}
                transition={{ duration: 0.3 }}
                className={`flex ${message.sender === 'user' ? 'justify-end' : 'justify-start'}`}
              >
                <div
                  className={`max-w-[80%] rounded-2xl px-4 py-3 ${
                    message.sender === 'user'
                      ? 'bg-gradient-to-r from-purple-500 to-blue-500 text-white'
                      : 'bg-white shadow-md text-gray-800'
                  }`}
                >
                  <p className="text-sm">{message.text}</p>
                  <p className={`text-xs mt-1 ${message.sender === 'user' ? 'text-purple-200' : 'text-gray-400'}`}>
                    {message.timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                  </p>
                </div>
              </motion.div>
            ))}
          </AnimatePresence>
          <div ref={messagesEndRef} />
        </div>

        {/* Input Area */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="bg-white rounded-xl shadow-lg p-4"
        >
          <div className="flex gap-2">
            <Input
              value={inputValue}
              onChange={(e) => setInputValue(e.target.value)}
              onKeyPress={(e) => e.key === 'Enter' && handleSendMessage(inputValue)}
              placeholder="Type your message..."
              className="flex-1"
            />
            <Button
              onClick={handleVoiceInput}
              variant={isListening ? 'default' : 'outline'}
              size="icon"
              className={isListening ? 'bg-red-500 hover:bg-red-600' : ''}
            >
              {isListening ? <MicOff className="w-4 h-4" /> : <Mic className="w-4 h-4" />}
            </Button>
            <Button
              onClick={() => handleSendMessage(inputValue)}
              disabled={!inputValue.trim()}
              size="icon"
              className="bg-gradient-to-r from-purple-500 to-blue-500 hover:from-purple-600 hover:to-blue-600"
            >
              <Send className="w-4 h-4" />
            </Button>
          </div>
          
          {isListening && (
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              className="mt-3 flex items-center justify-center gap-2 text-red-500"
            >
              <motion.div
                animate={{ scale: [1, 1.2, 1] }}
                transition={{ duration: 1, repeat: Infinity }}
                className="w-3 h-3 bg-red-500 rounded-full"
              />
              <span className="text-sm">Listening...</span>
            </motion.div>
          )}
        </motion.div>
      </div>

      {/* Voice Confirmation Dialog */}
      <Dialog open={showVoiceConfirm} onOpenChange={setShowVoiceConfirm}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Confirm Voice Message</DialogTitle>
            <DialogDescription className="space-y-4 pt-4">
              <div className="bg-purple-50 p-4 rounded-lg">
                <p className="text-purple-900">{voiceText}</p>
              </div>
              <div className="flex gap-2">
                <Button onClick={confirmVoiceMessage} className="flex-1">
                  Send Message
                </Button>
                <Button onClick={() => setShowVoiceConfirm(false)} variant="outline" className="flex-1">
                  Cancel
                </Button>
              </div>
            </DialogDescription>
          </DialogHeader>
        </DialogContent>
      </Dialog>
    </div>
  );
}
