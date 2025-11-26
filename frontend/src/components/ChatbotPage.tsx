import { useState, useRef, useEffect } from 'react';
import { motion, AnimatePresence } from 'motion/react';
import { Send, Mic, MicOff, Sparkles, AlertTriangle, History } from 'lucide-react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import { Navigation } from './Navigation';
import { Button } from './ui/button';
import { Input } from './ui/input';
import { Card } from './ui/card';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogDescription } from './ui/dialog';
import { Alert, AlertDescription } from './ui/alert';
import api from '../services/api';
import type { PageType } from '../App';
import type { ChatMessage, SendMessageResponse, User } from '../types/api.types';

interface ChatbotPageProps {
  user: User | null;
  onNavigate: (page: PageType) => void;
  onLogout?: () => void;
  onOpenNotifications?: () => void;
}

interface Message {
  id: string;
  text: string;
  sender: 'user' | 'bot';
  timestamp: Date;
  emotion?: string;
  crisisDetected?: boolean;
}

export function ChatbotPage({ user, onNavigate, onLogout, onOpenNotifications }: ChatbotPageProps) {
  const [messages, setMessages] = useState<Message[]>([
    {
      id: '1',
      text: `Hello ${user?.full_name || 'User'}! I'm your AI wellness companion powered by Ayurvedic wisdom. How are you feeling today?`,
      sender: 'bot',
      timestamp: new Date(),
    },
  ]);
  const [inputValue, setInputValue] = useState('');
  const [isListening, setIsListening] = useState(false);
  const [showVoiceConfirm, setShowVoiceConfirm] = useState(false);
  const [voiceText, setVoiceText] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [sessionId, setSessionId] = useState<string | undefined>(undefined);
  const [crisisAlert, setCrisisAlert] = useState<string | null>(null);
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

  // Load chat history on mount
  useEffect(() => {
    const loadChatHistory = async () => {
      try {
        const history = await api.getChatHistory(sessionId);
        if (history.length > 0) {
          const formattedMessages: Message[] = history.map((msg) => ({
            id: msg.id,
            text: msg.content,
            sender: msg.role === 'user' ? 'user' : 'bot',
            timestamp: new Date(msg.created_at),
            emotion: msg.emotion_detected,
            crisisDetected: msg.crisis_detected,
          }));
          setMessages((prev) => [...prev, ...formattedMessages]);
        }
      } catch (error) {
        console.error('Failed to load chat history:', error);
      }
    };

    if (api.isAuthenticated()) {
      loadChatHistory();
    }
  }, []);

  const handleSendMessage = async (text: string) => {
    if (!text.trim() || isLoading) return;

    console.log('[CHAT FRONTEND] Sending message:', {
      sessionId,
      inputMessage: text.trim(),
      length: text.trim().length
    });

    const userMessage: Message = {
      id: Date.now().toString(),
      text: text.trim(),
      sender: 'user',
      timestamp: new Date(),
    };

    setMessages((prev) => [...prev, userMessage]);
    setInputValue('');
    setIsLoading(true);

    try {
      const response: SendMessageResponse = await api.sendMessage({
        content: text.trim(),
        session_id: sessionId,
      });

      console.log('[CHAT FRONTEND] Received response:', {
        sessionId: response.session_id,
        responseLength: response.response.length,
        emotion: response.emotion_detected,
        crisis: response.crisis_detected
      });

      // Update session ID if new
      if (!sessionId && response.session_id) {
        setSessionId(response.session_id);
      }

      // Check for crisis detection
      if (response.crisis_detected) {
        setCrisisAlert(
          'We detected you might be in distress. If this is an emergency, please contact emergency services or your mental health professional immediately.'
        );
      }

      const botMessage: Message = {
        id: response.message.id,
        text: response.response,
        sender: 'bot',
        timestamp: new Date(response.message.created_at),
        emotion: response.emotion_detected,
        crisisDetected: response.crisis_detected,
      };

      setMessages((prev) => [...prev, botMessage]);
    } catch (error) {
      console.error('Failed to send message:', error);
      const errorMessage: Message = {
        id: (Date.now() + 1).toString(),
        text: 'Sorry, I encountered an error. Please try again.',
        sender: 'bot',
        timestamp: new Date(),
      };
      setMessages((prev) => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleVoiceInput = () => {
    if (!isListening) {
      setIsListening(true);
      // Note: Real voice recognition would require Web Speech API or similar
      // For now, we'll keep the simulation but users can implement real voice
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
      <Navigation currentPage="chatbot" onNavigate={onNavigate} onLogout={onLogout} user={user} onOpenNotifications={onOpenNotifications} />

      <div className="max-w-4xl mx-auto p-4 h-[calc(100vh-80px)] flex flex-col">
        {/* Header */}
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          className="mb-4"
        >
          <Card className="p-4 bg-gradient-to-r from-purple-500 to-blue-500 text-white">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-3">
                <motion.div
                  animate={{ rotate: 360 }}
                  transition={{ duration: 2, repeat: Infinity, ease: "linear" }}
                >
                  <Sparkles className="w-6 h-6" />
                </motion.div>
                <div>
                  <h2>AI Wellness Companion</h2>
                  <p className="text-sm text-purple-100">Powered by RAG, Emotion AI, and Ayurvedic wisdom</p>
                </div>
              </div>
              <Button
                variant="ghost"
                size="sm"
                className="text-white hover:bg-white/20"
                onClick={() => onNavigate('conversation-history')}
              >
                <History className="w-4 h-4 mr-2" />
                History
              </Button>
            </div>
          </Card>
        </motion.div>

        {/* Crisis Alert */}
        {crisisAlert && (
          <motion.div
            initial={{ opacity: 0, y: -10 }}
            animate={{ opacity: 1, y: 0 }}
            className="mb-4"
          >
            <Alert className="border-red-500 bg-red-50">
              <AlertTriangle className="h-4 w-4 text-red-600" />
              <AlertDescription className="text-red-800">
                {crisisAlert}
                <Button
                  variant="ghost"
                  size="sm"
                  className="ml-2"
                  onClick={() => setCrisisAlert(null)}
                >
                  Dismiss
                </Button>
              </AlertDescription>
            </Alert>
          </motion.div>
        )}

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
                  className={`max-w-[80%] rounded-2xl px-4 py-3 ${message.sender === 'user'
                    ? 'bg-gradient-to-r from-purple-500 to-blue-500 text-white'
                    : `bg-white shadow-md text-gray-800 ${message.crisisDetected ? 'border-2 border-red-500' : ''}`
                    }`}
                >
                  <div className="text-sm prose prose-sm max-w-none prose-p:my-1 prose-ul:my-1 prose-li:my-0 dark:prose-invert">
                    <ReactMarkdown
                      remarkPlugins={[remarkGfm]}
                      components={{
                        p: ({ node, ...props }) => <p className="mb-2 last:mb-0" {...props} />,
                        ul: ({ node, ...props }) => <ul className="list-disc ml-4 mb-2" {...props} />,
                        ol: ({ node, ...props }) => <ol className="list-decimal ml-4 mb-2" {...props} />,
                        li: ({ node, ...props }) => <li className="mb-1" {...props} />,
                        strong: ({ node, ...props }) => <span className="font-bold text-purple-700 dark:text-purple-300" {...props} />,
                      }}
                    >
                      {message.text}
                    </ReactMarkdown>
                  </div>
                  <div className="flex items-center justify-between mt-1">
                    <p className={`text-xs ${message.sender === 'user' ? 'text-purple-200' : 'text-gray-400'}`}>
                      {message.timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                    </p>
                    {message.emotion && (
                      <span className="text-xs bg-purple-100 text-purple-700 px-2 py-1 rounded-full ml-2">
                        {message.emotion}
                      </span>
                    )}
                  </div>
                </div>
              </motion.div>
            ))}
          </AnimatePresence>
          {isLoading && (
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              className="flex justify-start"
            >
              <div className="bg-white shadow-md rounded-2xl px-4 py-3">
                <div className="flex gap-2">
                  <motion.div
                    animate={{ scale: [1, 1.2, 1] }}
                    transition={{ duration: 0.6, repeat: Infinity, delay: 0 }}
                    className="w-2 h-2 bg-purple-500 rounded-full"
                  />
                  <motion.div
                    animate={{ scale: [1, 1.2, 1] }}
                    transition={{ duration: 0.6, repeat: Infinity, delay: 0.2 }}
                    className="w-2 h-2 bg-purple-500 rounded-full"
                  />
                  <motion.div
                    animate={{ scale: [1, 1.2, 1] }}
                    transition={{ duration: 0.6, repeat: Infinity, delay: 0.4 }}
                    className="w-2 h-2 bg-purple-500 rounded-full"
                  />
                </div>
              </div>
            </motion.div>
          )}
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
              disabled={!inputValue.trim() || isLoading}
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
