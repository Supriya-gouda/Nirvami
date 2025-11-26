import { motion } from 'motion/react';
import { useState, useEffect } from 'react';
import { Home, MessageCircle, FileText, Activity, UtensilsCrossed, TrendingUp, LogOut, Sparkles, Watch, Bell, User as UserIconLucide, Settings, CalendarCheck } from 'lucide-react';
import { Button } from './ui/button';
import { Badge } from './ui/badge';
import type { PageType, User } from '../App';
import logo from 'figma:asset/34629939463a62914e4d6cf8617751092b770df0.png';
import api from '../services/api';

interface NavigationProps {
  currentPage: PageType;
  onNavigate: (page: PageType) => void;
  onLogout?: () => void;
  user?: User | null;
  onOpenNotifications?: () => void;
}

export function Navigation({ currentPage, onNavigate, onLogout, user, onOpenNotifications }: NavigationProps) {
  const [unreadCount, setUnreadCount] = useState(0);

  useEffect(() => {
    if (user) {
      loadUnreadCount();
      const interval = setInterval(loadUnreadCount, 30000); // Poll every 30s
      return () => clearInterval(interval);
    }
  }, [user]);

  const loadUnreadCount = async () => {
    try {
      const count = await api.getUnreadCount();
      setUnreadCount(count || 0);
    } catch (err) {
      console.error('Failed to load unread count:', err);
    }
  };

  const navItems = [
    { id: 'dashboard' as PageType, icon: Home, label: 'Dashboard' },
    { id: 'chatbot' as PageType, icon: MessageCircle, label: 'Chat' },
    { id: 'manual' as PageType, icon: FileText, label: 'Log' },
    { id: 'aura' as PageType, icon: Sparkles, label: 'Aura' },
    { id: 'yoga' as PageType, icon: Activity, label: 'Yoga' },
    { id: 'routines' as PageType, icon: CalendarCheck, label: 'Routines' },
    { id: 'diet' as PageType, icon: UtensilsCrossed, label: 'Diet' },
    { id: 'device' as PageType, icon: Watch, label: 'Device' },
    { id: 'progress' as PageType, icon: TrendingUp, label: 'Progress' },
  ];

  return (
    <motion.nav
      className="bg-white/80 backdrop-blur-md shadow-lg border-b border-purple-100"
      initial={{ y: -100 }}
      animate={{ y: 0 }}
      transition={{ duration: 0.5 }}
    >
      <div className="max-w-7xl mx-auto px-4 py-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <motion.div
              className="flex items-center justify-center"
              whileHover={{ scale: 1.1, rotate: 180 }}
              transition={{ duration: 0.3 }}
            >
              <img src={logo} alt="Nirvami" className="w-10 h-10" />
            </motion.div>
            <div>
              <h2 className="text-purple-700">Nirvami</h2>
              {user?.name && <p className="text-xs text-gray-500">Welcome, {user.name}</p>}
            </div>
          </div>

          <div className="flex items-center gap-2">
            {navItems.map((item) => {
              const Icon = item.icon;
              const isActive = currentPage === item.id;
              return (
                <motion.button
                  key={item.id}
                  onClick={() => onNavigate(item.id)}
                  className={`flex items-center gap-2 px-4 py-2 rounded-lg transition-colors ${
                    isActive
                      ? 'bg-purple-100 text-purple-700'
                      : 'text-gray-600 hover:bg-purple-50'
                  }`}
                  whileHover={{ scale: 1.05 }}
                  whileTap={{ scale: 0.95 }}
                >
                  <Icon className="w-4 h-4" />
                  <span className="hidden md:inline text-sm">{item.label}</span>
                </motion.button>
              );
            })}

            {onLogout && (
              <div className="flex items-center gap-3 ml-4 pl-4 border-l border-gray-200">
                {/* Notification Bell */}
                <motion.button
                  onClick={onOpenNotifications}
                  className="relative p-2 rounded-lg text-gray-600 hover:bg-purple-50 hover:text-purple-700 transition-colors"
                  whileHover={{ scale: 1.05 }}
                  whileTap={{ scale: 0.95 }}
                >
                  <Bell className="w-5 h-5" />
                  {unreadCount > 0 && (
                    <Badge
                      variant="destructive"
                      className="absolute -top-1 -right-1 h-5 w-5 flex items-center justify-center p-0 text-xs"
                    >
                      {unreadCount > 9 ? '9+' : unreadCount}
                    </Badge>
                  )}
                </motion.button>

                {/* Settings Button */}
                <motion.button
                  onClick={() => onNavigate('settings')}
                  className={`p-2 rounded-lg transition-colors ${
                    currentPage === 'settings'
                      ? 'bg-purple-100 text-purple-700'
                      : 'text-gray-600 hover:bg-purple-50 hover:text-purple-700'
                  }`}
                  whileHover={{ scale: 1.05 }}
                  whileTap={{ scale: 0.95 }}
                >
                  <Settings className="w-5 h-5" />
                </motion.button>

                {user?.name && (
                  <div className="hidden lg:flex items-center gap-2">
                    <div className="w-8 h-8 bg-gradient-to-br from-purple-400 to-pink-400 rounded-full flex items-center justify-center text-white font-semibold text-sm">
                      {user.name.charAt(0).toUpperCase()}
                    </div>
                    <span className="text-sm text-gray-700">{user.name}</span>
                  </div>
                )}
                <Button
                  onClick={onLogout}
                  variant="ghost"
                  size="sm"
                  className="text-red-600 hover:text-red-700 hover:bg-red-50 flex items-center gap-2"
                >
                  <LogOut className="w-4 h-4" />
                  <span className="text-sm font-medium">Sign Out</span>
                </Button>
              </div>
            )}
          </div>
        </div>
      </div>
    </motion.nav>
  );
}