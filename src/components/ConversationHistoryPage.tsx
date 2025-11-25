import { useEffect, useState } from 'react';
import { motion } from 'motion/react';
import { MessageCircle, Calendar, ArrowLeft, User, Bot, Clock } from 'lucide-react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import { Navigation } from './Navigation';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from './ui/card';
import { Button } from './ui/button';
import { Badge } from './ui/badge';
import { Separator } from './ui/separator';
import { Alert, AlertDescription } from './ui/alert';
import api from '../services/api';
import type { PageType } from '../App';
import type { User as AuthUser, ChatSession, ChatMessage } from '../types/api.types';

interface ConversationHistoryPageProps {
  user: AuthUser | null;
  onNavigate: (page: PageType) => void;
  onLogout?: () => void;
  onOpenNotifications?: () => void;
}

export function ConversationHistoryPage({
  user,
  onNavigate,
  onLogout,
  onOpenNotifications,
}: ConversationHistoryPageProps) {
  const [sessions, setSessions] = useState<ChatSession[]>([]);
  const [selectedSession, setSelectedSession] = useState<ChatSession | null>(null);
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [loading, setLoading] = useState(true);
  const [loadingMessages, setLoadingMessages] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadSessions();
  }, []);

  const loadSessions = async () => {
    try {
      setLoading(true);
      setError(null);
      const sessionsData = await api.getChatSessions();
      setSessions(sessionsData);
    } catch (err: any) {
      console.error('Failed to load sessions:', err);
      setError('Failed to load conversation history. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const loadSessionMessages = async (session: ChatSession) => {
    try {
      setLoadingMessages(true);
      setSelectedSession(session);
      const messagesData = await api.getSessionMessages(session.id);
      setMessages(messagesData);
    } catch (err: any) {
      console.error('Failed to load messages:', err);
      setError('Failed to load conversation messages. Please try again.');
    } finally {
      setLoadingMessages(false);
    }
  };

  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    const now = new Date();
    const diffDays = Math.floor((now.getTime() - date.getTime()) / (1000 * 60 * 60 * 24));

    if (diffDays === 0) return 'Today';
    if (diffDays === 1) return 'Yesterday';
    if (diffDays < 7) return `${diffDays} days ago`;
    
    return date.toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
    });
  };

  const formatTime = (dateString: string) => {
    const date = new Date(dateString);
    return date.toLocaleTimeString('en-US', {
      hour: '2-digit',
      minute: '2-digit',
    });
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-purple-50 via-white to-pink-50">
      <Navigation
        currentPage="chatbot"
        onNavigate={onNavigate}
        onLogout={onLogout}
        onOpenNotifications={onOpenNotifications}
        user={user}
      />

      <div className="container max-w-7xl mx-auto px-4 py-8 mt-16">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="mb-8"
        >
          <div className="flex items-center gap-3 mb-2">
            <MessageCircle className="w-8 h-8 text-purple-600" />
            <h1 className="text-3xl font-bold text-gray-900">Conversation History</h1>
          </div>
          <p className="text-gray-600">Review your past conversations with Nirvami</p>
        </motion.div>

        {error && (
          <Alert variant="destructive" className="mb-6">
            <AlertDescription>{error}</AlertDescription>
          </Alert>
        )}

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Sessions List */}
          <motion.div
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            className="lg:col-span-1"
          >
            <Card className="sticky top-24">
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Calendar className="w-5 h-5" />
                  Your Sessions
                </CardTitle>
                <CardDescription>
                  {sessions.length} conversation{sessions.length !== 1 ? 's' : ''}
                </CardDescription>
              </CardHeader>
              <CardContent className="max-h-[600px] overflow-y-auto space-y-2">
                {loading ? (
                  <div className="text-center py-8 text-gray-500">Loading sessions...</div>
                ) : sessions.length === 0 ? (
                  <div className="text-center py-8">
                    <MessageCircle className="w-12 h-12 text-gray-300 mx-auto mb-2" />
                    <p className="text-gray-500">No conversations yet</p>
                    <Button
                      onClick={() => onNavigate('chatbot')}
                      variant="link"
                      className="mt-2 text-purple-600"
                    >
                      Start chatting
                    </Button>
                  </div>
                ) : (
                  sessions.map((session) => (
                    <motion.div
                      key={session.id}
                      whileHover={{ scale: 1.02 }}
                      whileTap={{ scale: 0.98 }}
                    >
                      <Button
                        variant={selectedSession?.id === session.id ? 'default' : 'outline'}
                        className="w-full text-left justify-start h-auto py-3 px-4"
                        onClick={() => loadSessionMessages(session)}
                      >
                        <div className="flex flex-col gap-1 w-full">
                          <div className="font-medium truncate text-sm">
                            {session.title || 'Untitled Conversation'}
                          </div>
                          <div className="flex items-center gap-2 text-xs text-gray-500">
                            <Clock className="w-3 h-3" />
                            {formatDate(session.last_message_at)}
                          </div>
                        </div>
                      </Button>
                    </motion.div>
                  ))
                )}
              </CardContent>
            </Card>
          </motion.div>

          {/* Messages View */}
          <motion.div
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            className="lg:col-span-2"
          >
            {!selectedSession ? (
              <Card className="h-full flex items-center justify-center min-h-[600px]">
                <CardContent className="text-center">
                  <MessageCircle className="w-16 h-16 text-gray-300 mx-auto mb-4" />
                  <h3 className="text-lg font-semibold text-gray-700 mb-2">
                    Select a Conversation
                  </h3>
                  <p className="text-gray-500">
                    Choose a session from the list to view the conversation
                  </p>
                </CardContent>
              </Card>
            ) : (
              <Card>
                <CardHeader className="border-b">
                  <div className="flex items-center justify-between">
                    <div>
                      <CardTitle className="text-xl">
                        {selectedSession.title || 'Conversation'}
                      </CardTitle>
                      <CardDescription className="flex items-center gap-2 mt-1">
                        <Calendar className="w-4 h-4" />
                        Started {formatDate(selectedSession.started_at)}
                      </CardDescription>
                    </div>
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() => {
                        setSelectedSession(null);
                        setMessages([]);
                      }}
                    >
                      <ArrowLeft className="w-4 h-4 mr-2" />
                      Back
                    </Button>
                  </div>
                </CardHeader>
                <CardContent className="max-h-[600px] overflow-y-auto p-6">
                  {loadingMessages ? (
                    <div className="text-center py-8 text-gray-500">Loading messages...</div>
                  ) : messages.length === 0 ? (
                    <div className="text-center py-8 text-gray-500">No messages in this conversation</div>
                  ) : (
                    <div className="space-y-4">
                      {messages.map((message, index) => (
                        <motion.div
                          key={message.id}
                          initial={{ opacity: 0, y: 10 }}
                          animate={{ opacity: 1, y: 0 }}
                          transition={{ delay: index * 0.05 }}
                          className={`flex gap-3 ${
                            message.role === 'user' ? 'justify-end' : 'justify-start'
                          }`}
                        >
                          {message.role !== 'user' && (
                            <div className="flex-shrink-0">
                              <div className="w-8 h-8 rounded-full bg-gradient-to-br from-purple-500 to-pink-500 flex items-center justify-center">
                                <Bot className="w-5 h-5 text-white" />
                              </div>
                            </div>
                          )}
                          
                          <div
                            className={`max-w-[70%] rounded-2xl px-4 py-3 ${
                              message.role === 'user'
                                ? 'bg-purple-600 text-white'
                                : 'bg-gray-100 text-gray-900'
                            }`}
                          >
                            {message.role === 'user' ? (
                              <p className="text-sm">{message.content}</p>
                            ) : (
                              <div className="prose prose-sm max-w-none">
                                <ReactMarkdown remarkPlugins={[remarkGfm]}>
                                  {message.content}
                                </ReactMarkdown>
                              </div>
                            )}
                            
                            <div className="flex items-center gap-2 mt-2 text-xs opacity-70">
                              <Clock className="w-3 h-3" />
                              {formatTime(message.created_at)}
                              {message.emotion_detected && (
                                <>
                                  <Separator orientation="vertical" className="h-3" />
                                  <Badge variant="secondary" className="text-xs py-0 px-2">
                                    {message.emotion_detected}
                                  </Badge>
                                </>
                              )}
                            </div>
                          </div>

                          {message.role === 'user' && (
                            <div className="flex-shrink-0">
                              <div className="w-8 h-8 rounded-full bg-gradient-to-br from-blue-500 to-cyan-500 flex items-center justify-center">
                                <User className="w-5 h-5 text-white" />
                              </div>
                            </div>
                          )}
                        </motion.div>
                      ))}
                    </div>
                  )}
                </CardContent>
              </Card>
            )}
          </motion.div>
        </div>

        {/* Back to Chat Button */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.3 }}
          className="mt-8 text-center"
        >
          <Button
            onClick={() => onNavigate('chatbot')}
            size="lg"
            className="bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-700 hover:to-pink-700"
          >
            <MessageCircle className="w-5 h-5 mr-2" />
            Continue Chatting
          </Button>
        </motion.div>
      </div>
    </div>
  );
}
