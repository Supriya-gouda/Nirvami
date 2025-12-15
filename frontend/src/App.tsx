import { useState, useEffect, useRef } from 'react';
import { LandingPage } from './components/LandingPageNew';
import { Dashboard } from './components/Dashboard';
import { ChatbotPage } from './components/ChatbotPage';
import { ConversationHistoryPage } from './components/ConversationHistoryPage';
import { LogPage } from './components/LogPage';
import { YogaRecommendationPage } from './components/YogaRecommendationPage';
import { AyurvedaRecommendationPage } from './components/AyurvedaRecommendationPage';
import { DietMoodPage } from './components/DietMoodPage';
import { ProgressAnalyticsPage } from './components/ProgressAnalyticsPage';
import { EmotionHistoryPage } from './components/EmotionHistoryPage';
import { AuraVisualizationPage } from './components/AuraVisualizationPage';
import { DevicePage } from './components/DevicePage';
import { SignInPage } from './components/SignInPage';
import { SignUpPage } from './components/SignUpPage';
import { MoodInputPopup } from './components/MoodInputPopup';
import { DoshaQuizPage } from './components/DoshaQuizPage';
import { NotificationCenter } from './components/NotificationCenter';
import { ProfilePage } from './components/ProfilePage';
import { AccountSettingsPage } from './components/AccountSettingsPage';
import { DailyRoutinesPage } from './components/DailyRoutinesPage';
import { DinacharyaPage } from './components/DinacharyaPage';
import { PracticeDetailPage } from './components/PracticeDetailPage';
import { Toaster } from './components/ui/sonner';
import { useAuth } from './contexts/AuthContext';
import api from './services/api';

export type PageType = 'landing' | 'signin' | 'signup' | 'dashboard' | 'chatbot' | 'conversation-history' | 'manual' | 'moodboard' | 'yoga-recommendations' | 'ayurveda-recommendations' | 'diet' | 'progress' | 'emotion-history' | 'aura' | 'device' | 'dosha' | 'profile' | 'settings' | 'routines' | 'dinacharya' | 'practice';

function App() {
  const { user, isAuthenticated, isLoading, logout } = useAuth();
  const [currentPage, setCurrentPage] = useState<PageType>('landing');
  const [showMoodPopup, setShowMoodPopup] = useState(false);
  const [showNotificationCenter, setShowNotificationCenter] = useState(false);
  const [auraRefreshTrigger, setAuraRefreshTrigger] = useState(0);
  const [previousPage, setPreviousPage] = useState<PageType>('dashboard');
  const [selectedPractice, setSelectedPractice] = useState<{
    id?: string;
    title: string;
    content: string;
    category?: string;
    source?: string;
  } | null>(null);
  
  // Track last popup time and user activity to prevent spam
  const lastPopupTimeRef = useRef<number>(0);
  const lastActivityTimeRef = useRef<number>(Date.now());
  const activityTimerRef = useRef<NodeJS.Timeout | null>(null);
  const popupCheckTimerRef = useRef<NodeJS.Timeout | null>(null);

  // Check if mood popup should be shown
  const checkAndShowMoodPopup = async (force: boolean = false) => {
    if (!isAuthenticated) {
      console.log('[Mood Popup] Not authenticated, skipping popup check');
      return;
    }
    
    // Prevent showing popup if it's already open
    if (showMoodPopup) {
      console.log('[Mood Popup] Popup already open, skipping');
      return;
    }
    
    // Prevent showing popup if it was shown less than 10 minutes ago (unless forced)
    const now = Date.now();
    const tenMinutes = 10 * 60 * 1000;
    if (!force && (now - lastPopupTimeRef.current) < tenMinutes) {
      console.log('[Mood Popup] Less than 10 minutes since last popup, skipping');
      return;
    }

    console.log('[Mood Popup] Checking if mood logged today (force:', force, ')');
    try {
      const result = await api.checkMoodLoggedToday();
      console.log('[Mood Popup] API result:', result);
      
      if (!result.logged_today || force) {
        console.log('[Mood Popup] Showing popup in', force ? '0ms' : '2000ms');
        lastPopupTimeRef.current = now;
        // Show popup after a short delay
        setTimeout(() => {
          console.log('[Mood Popup] Setting showMoodPopup to true');
          setShowMoodPopup(true);
        }, force ? 0 : 2000);
      } else {
        console.log('[Mood Popup] Already logged today, not showing popup');
      }
    } catch (error) {
      console.error('[Mood Popup] Error checking mood log status:', error);
      // Show popup anyway on error
      console.log('[Mood Popup] Showing popup due to API error');
      lastPopupTimeRef.current = now;
      setTimeout(() => {
        setShowMoodPopup(true);
      }, force ? 0 : 2000);
    }
  };

  // Track user activity for 10-minute timer
  useEffect(() => {
    if (!isAuthenticated) {
      // Clear timers when logged out
      if (activityTimerRef.current) {
        clearInterval(activityTimerRef.current);
        activityTimerRef.current = null;
      }
      if (popupCheckTimerRef.current) {
        clearInterval(popupCheckTimerRef.current);
        popupCheckTimerRef.current = null;
      }
      return;
    }

    // Track when user session started (login or page load)
    const sessionStartTime = Date.now();
    let lastActivityTime = Date.now();

    // Track user activity (mouse moves, clicks, keyboard, scroll)
    const updateActivity = () => {
      lastActivityTime = Date.now();
    };

    window.addEventListener('mousemove', updateActivity, { passive: true });
    window.addEventListener('click', updateActivity, { passive: true });
    window.addEventListener('keydown', updateActivity, { passive: true });
    window.addEventListener('scroll', updateActivity, { passive: true });
    window.addEventListener('touchstart', updateActivity, { passive: true });

    // Check every 30 seconds if 10 minutes of active usage have passed
    activityTimerRef.current = setInterval(() => {
      const now = Date.now();
      const tenMinutes = 10 * 60 * 1000;
      
      // Check if user has been active for at least 10 minutes since session start
      // and at least 10 minutes since last popup
      const timeSinceSessionStart = now - sessionStartTime;
      const timeSinceLastPopup = now - lastPopupTimeRef.current;
      const timeSinceLastActivity = now - lastActivityTime;
      
      // Only show popup if:
      // 1. User has been active for 10+ minutes since session start
      // 2. At least 10 minutes have passed since last popup
      // 3. User was active in the last 2 minutes (not idle)
      if (
        timeSinceSessionStart >= tenMinutes &&
        timeSinceLastPopup >= tenMinutes &&
        timeSinceLastActivity < 2 * 60 * 1000 // Active in last 2 minutes
      ) {
        checkAndShowMoodPopup(false);
        lastActivityTime = now; // Reset to prevent immediate re-trigger
      }
    }, 30000); // Check every 30 seconds

    return () => {
      window.removeEventListener('mousemove', updateActivity);
      window.removeEventListener('click', updateActivity);
      window.removeEventListener('keydown', updateActivity);
      window.removeEventListener('scroll', updateActivity);
      window.removeEventListener('touchstart', updateActivity);
      if (activityTimerRef.current) {
        clearInterval(activityTimerRef.current);
      }
    };
  }, [isAuthenticated, showMoodPopup]);

  // Navigate to dashboard when user logs in
  useEffect(() => {
    if (!isLoading) {
      if (isAuthenticated) {
        if (currentPage === 'landing' || currentPage === 'signin' || currentPage === 'signup') {
          console.log('[App] User just logged in, navigating to dashboard and showing popup');
          setCurrentPage('dashboard');
          // Show popup immediately after login (forced) - wait a bit for dashboard to mount
          setTimeout(() => {
            checkAndShowMoodPopup(true);
          }, 500);
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
    console.log('[App] Login success handler called');
    setCurrentPage('dashboard');
    // Don't call checkAndShowMoodPopup here - let the useEffect above handle it
    // when isAuthenticated becomes true
  };

  const handleLogout = () => {
    logout();
    setCurrentPage('landing');
  };

  const handleMoodSubmitted = () => {
    setShowMoodPopup(false);
    lastPopupTimeRef.current = Date.now(); // Update last popup time
    lastActivityTimeRef.current = Date.now(); // Reset activity timer
    // Trigger aura refresh in child components
    setAuraRefreshTrigger(prev => prev + 1);
    console.log('[App] Mood submitted - aura refresh triggered');
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
      {currentPage === 'dashboard' && <Dashboard user={user} onNavigate={navigateToPage} onLogout={handleLogout} onOpenNotifications={() => setShowNotificationCenter(true)} onRequestMoodPopup={() => checkAndShowMoodPopup(true)} refreshTrigger={auraRefreshTrigger} />}
      {currentPage === 'chatbot' && <ChatbotPage user={user} onNavigate={navigateToPage} onLogout={handleLogout} onOpenNotifications={() => setShowNotificationCenter(true)} />}
      {currentPage === 'conversation-history' && <ConversationHistoryPage user={user} onNavigate={navigateToPage} onLogout={handleLogout} onOpenNotifications={() => setShowNotificationCenter(true)} />}
      {currentPage === 'manual' && <LogPage user={user} onNavigate={navigateToPage} onLogout={handleLogout} onOpenNotifications={() => setShowNotificationCenter(true)} />}
      {currentPage === 'moodboard' && <LogPage user={user} onNavigate={navigateToPage} onLogout={handleLogout} onOpenNotifications={() => setShowNotificationCenter(true)} />}
      {currentPage === 'yoga-recommendations' && <YogaRecommendationPage user={user} onNavigate={navigateToPage} onLogout={handleLogout} onOpenNotifications={() => setShowNotificationCenter(true)} onOpenPractice={(rec) => { setPreviousPage('yoga-recommendations'); setSelectedPractice(rec); setCurrentPage('practice'); }} />}
      {currentPage === 'ayurveda-recommendations' && <AyurvedaRecommendationPage user={user} onNavigate={navigateToPage} onLogout={handleLogout} onOpenNotifications={() => setShowNotificationCenter(true)} onOpenPractice={(rec) => { setPreviousPage('ayurveda-recommendations'); setSelectedPractice(rec); setCurrentPage('practice'); }} />}
      {currentPage === 'diet' && <DietMoodPage user={user} onNavigate={navigateToPage} onLogout={handleLogout} onOpenNotifications={() => setShowNotificationCenter(true)} />}
      {currentPage === 'progress' && <ProgressAnalyticsPage user={user} onNavigate={navigateToPage} onLogout={handleLogout} onOpenNotifications={() => setShowNotificationCenter(true)} />}
      {currentPage === 'emotion-history' && <EmotionHistoryPage user={user} onNavigate={navigateToPage} onLogout={handleLogout} onOpenNotifications={() => setShowNotificationCenter(true)} />}
      {currentPage === 'aura' && <AuraVisualizationPage user={user} onNavigate={navigateToPage} onLogout={handleLogout} onOpenNotifications={() => setShowNotificationCenter(true)} refreshTrigger={auraRefreshTrigger} />}
      {currentPage === 'device' && <DevicePage user={user} onNavigate={navigateToPage} onLogout={handleLogout} onOpenNotifications={() => setShowNotificationCenter(true)} />}
      {currentPage === 'dosha' && <DoshaQuizPage user={user} onNavigate={navigateToPage} onLogout={handleLogout} onOpenNotifications={() => setShowNotificationCenter(true)} />}
      {currentPage === 'routines' && <DailyRoutinesPage user={user} onNavigate={navigateToPage} onLogout={handleLogout} onOpenNotifications={() => setShowNotificationCenter(true)} />}
      {currentPage === 'dinacharya' && <DinacharyaPage user={user} onNavigate={navigateToPage} onLogout={handleLogout} onOpenNotifications={() => setShowNotificationCenter(true)} />}
      {currentPage === 'profile' && <ProfilePage user={user} onNavigate={navigateToPage} onLogout={handleLogout} onOpenNotifications={() => setShowNotificationCenter(true)} />}
      {currentPage === 'settings' && <AccountSettingsPage user={user} onNavigate={navigateToPage} onLogout={handleLogout} onOpenNotifications={() => setShowNotificationCenter(true)} />}
      {currentPage === 'practice' && selectedPractice && (
        <PracticeDetailPage
          user={user}
          recommendation={selectedPractice}
          onNavigate={navigateToPage}
          onLogout={handleLogout}
          onOpenNotifications={() => setShowNotificationCenter(true)}
          onClose={() => { setCurrentPage(previousPage); setSelectedPractice(null); }}
        />
      )}

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