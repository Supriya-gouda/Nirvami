import { useState, useEffect } from 'react';
import { LandingPage } from './components/LandingPageNew';
import { Dashboard } from './components/Dashboard';
import { ChatbotPage } from './components/ChatbotPage';
import { LogPage } from './components/LogPage';
import { YogaLifestylePage } from './components/YogaLifestylePage';
import { DietMoodPage } from './components/DietMoodPage';
import { ProgressAnalyticsPage } from './components/ProgressAnalyticsPage';
import { AuraVisualizationPage } from './components/AuraVisualizationPage';
import { DevicePage } from './components/DevicePage';
import { SignInPage } from './components/SignInPage';
import { SignUpPage } from './components/SignUpPage';
import { MoodInputPopup } from './components/MoodInputPopup';
import { DoshaQuizPage } from './components/DoshaQuizPage';
import { NotificationCenter } from './components/NotificationCenter';
import { ProfilePage } from './components/ProfilePage';
import { Toaster } from './components/ui/sonner';
import { useAuth } from './contexts/AuthContext';

export type PageType = 'landing' | 'signin' | 'signup' | 'dashboard' | 'chatbot' | 'manual' | 'moodboard' | 'yoga' | 'diet' | 'progress' | 'aura' | 'device' | 'dosha' | 'profile';

function App() {
  const { user, isAuthenticated, isLoading, logout } = useAuth();
  const [currentPage, setCurrentPage] = useState<PageType>('landing');
  const [showMoodPopup, setShowMoodPopup] = useState(false);
  const [showNotificationCenter, setShowNotificationCenter] = useState(false);

  // Check if mood popup should be shown
  const checkAndShowMoodPopup = () => {
    const today = new Date().toISOString().split('T')[0];
    const lastMoodLog = localStorage.getItem('nirvami_mood_logged_today');
    
    if (lastMoodLog !== today && isAuthenticated) {
      // Show popup after a short delay
      setTimeout(() => {
        setShowMoodPopup(true);
      }, 2000);
    }
  };

  // Navigate to dashboard when user logs in
  useEffect(() => {
    if (!isLoading) {
      if (isAuthenticated) {
        if (currentPage === 'landing' || currentPage === 'signin' || currentPage === 'signup') {
          setCurrentPage('dashboard');
          checkAndShowMoodPopup();
        }
      } else {
        if (currentPage !== 'landing' && currentPage !== 'signin' && currentPage !== 'signup') {
          setCurrentPage('landing');
        }
      }
    }
  }, [isAuthenticated, isLoading]);

  const navigateToPage = (page: PageType) => {
    setCurrentPage(page);
  };

  const handleLoginSuccess = () => {
    setCurrentPage('dashboard');
    checkAndShowMoodPopup();
  };

  const handleLogout = () => {
    logout();
    setCurrentPage('landing');
  };

  const handleMoodSubmitted = () => {
    const today = new Date().toISOString().split('T')[0];
    localStorage.setItem('nirvami_mood_logged_today', today);
  };

  // Show loading state while checking auth
  if (isLoading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-purple-50 via-blue-50 to-pink-50 flex items-center justify-center">
        <div className="text-center">
          <div className="w-16 h-16 border-4 border-purple-500 border-t-transparent rounded-full animate-spin mx-auto mb-4"></div>
          <p className="text-gray-600">Loading...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-purple-50 via-blue-50 to-pink-50">
      {currentPage === 'landing' && <LandingPage onGetStarted={() => setCurrentPage('signin')} />}
      {currentPage === 'signin' && (
        <SignInPage 
          onSignIn={handleLoginSuccess} 
          onNavigateToSignUp={() => setCurrentPage('signup')} 
        />
      )}
      {currentPage === 'signup' && (
        <SignUpPage 
          onSignUp={handleLoginSuccess} 
          onNavigateToSignIn={() => setCurrentPage('signin')} 
        />
      )}
      {currentPage === 'dashboard' && <Dashboard user={user} onNavigate={navigateToPage} onLogout={handleLogout} onOpenNotifications={() => setShowNotificationCenter(true)} />}
      {currentPage === 'chatbot' && <ChatbotPage user={user} onNavigate={navigateToPage} onLogout={handleLogout} onOpenNotifications={() => setShowNotificationCenter(true)} />}
      {currentPage === 'manual' && <LogPage user={user} onNavigate={navigateToPage} onLogout={handleLogout} onOpenNotifications={() => setShowNotificationCenter(true)} />}
      {currentPage === 'moodboard' && <LogPage user={user} onNavigate={navigateToPage} onLogout={handleLogout} onOpenNotifications={() => setShowNotificationCenter(true)} />}
      {currentPage === 'yoga' && <YogaLifestylePage user={user} onNavigate={navigateToPage} onLogout={handleLogout} onOpenNotifications={() => setShowNotificationCenter(true)} />}
      {currentPage === 'diet' && <DietMoodPage user={user} onNavigate={navigateToPage} onLogout={handleLogout} onOpenNotifications={() => setShowNotificationCenter(true)} />}
      {currentPage === 'progress' && <ProgressAnalyticsPage user={user} onNavigate={navigateToPage} onLogout={handleLogout} onOpenNotifications={() => setShowNotificationCenter(true)} />}
      {currentPage === 'aura' && <AuraVisualizationPage user={user} onNavigate={navigateToPage} onLogout={handleLogout} onOpenNotifications={() => setShowNotificationCenter(true)} />}
      {currentPage === 'device' && <DevicePage user={user} onNavigate={navigateToPage} onLogout={handleLogout} onOpenNotifications={() => setShowNotificationCenter(true)} />}
      {currentPage === 'dosha' && <DoshaQuizPage user={user} onNavigate={navigateToPage} onLogout={handleLogout} onOpenNotifications={() => setShowNotificationCenter(true)} />}
      {currentPage === 'profile' && <ProfilePage user={user} onNavigate={navigateToPage} onLogout={handleLogout} onOpenNotifications={() => setShowNotificationCenter(true)} />}
      
      {/* Mood Input Popup */}
      <MoodInputPopup 
        isOpen={showMoodPopup} 
        onClose={() => setShowMoodPopup(false)}
        onMoodSubmitted={handleMoodSubmitted}
      />

      {/* Notification Center */}
      {showNotificationCenter && (
        <NotificationCenter 
          user={user} 
          onClose={() => setShowNotificationCenter(false)}
          onNavigate={navigateToPage}
        />
      )}
      
      <Toaster />
    </div>
  );
}

export default App;