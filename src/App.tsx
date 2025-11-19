import { useState } from 'react';
import { LandingPage } from './components/LandingPageNew';
import { Dashboard } from './components/Dashboard';
import { ChatbotPage } from './components/ChatbotPage';
import { LogPage } from './components/LogPage';
import { YogaLifestylePage } from './components/YogaLifestylePage';
import { DietMoodPage } from './components/DietMoodPage';
import { ProgressAnalyticsPage } from './components/ProgressAnalyticsPage';
import { Toaster } from './components/ui/sonner';

export type PageType = 'landing' | 'dashboard' | 'chatbot' | 'manual' | 'moodboard' | 'yoga' | 'diet' | 'progress';

export interface User {
  name: string;
  isGuest: boolean;
}

function App() {
  const [currentPage, setCurrentPage] = useState<PageType>('landing');
  const [user, setUser] = useState<User | null>(null);

  const navigateToPage = (page: PageType) => {
    setCurrentPage(page);
  };

  const handleLogin = (userData: User) => {
    setUser(userData);
    setCurrentPage('dashboard');
  };

  const handleLogout = () => {
    setUser(null);
    setCurrentPage('landing');
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-purple-50 via-blue-50 to-pink-50">
      {currentPage === 'landing' && <LandingPage onLogin={handleLogin} />}
      {currentPage === 'dashboard' && <Dashboard user={user} onNavigate={navigateToPage} onLogout={handleLogout} />}
      {currentPage === 'chatbot' && <ChatbotPage user={user} onNavigate={navigateToPage} />}
      {currentPage === 'manual' && <LogPage user={user} onNavigate={navigateToPage} />}
      {currentPage === 'moodboard' && <LogPage user={user} onNavigate={navigateToPage} />}
      {currentPage === 'yoga' && <YogaLifestylePage user={user} onNavigate={navigateToPage} />}
      {currentPage === 'diet' && <DietMoodPage user={user} onNavigate={navigateToPage} />}
      {currentPage === 'progress' && <ProgressAnalyticsPage user={user} onNavigate={navigateToPage} />}
      <Toaster />
    </div>
  );
}

export default App;