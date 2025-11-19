import { motion } from 'motion/react';
import { Home, MessageCircle, FileText, Activity, UtensilsCrossed, TrendingUp, LogOut } from 'lucide-react';
import { Button } from './ui/button';
import type { PageType, User } from '../App';
import logo from 'figma:asset/34629939463a62914e4d6cf8617751092b770df0.png';

interface NavigationProps {
  currentPage: PageType;
  onNavigate: (page: PageType) => void;
  onLogout?: () => void;
  user?: User | null;
}

export function Navigation({ currentPage, onNavigate, onLogout, user }: NavigationProps) {
  const navItems = [
    { id: 'dashboard' as PageType, icon: Home, label: 'Dashboard' },
    { id: 'chatbot' as PageType, icon: MessageCircle, label: 'Chat' },
    { id: 'manual' as PageType, icon: FileText, label: 'Log' },
    { id: 'yoga' as PageType, icon: Activity, label: 'Yoga' },
    { id: 'diet' as PageType, icon: UtensilsCrossed, label: 'Diet' },
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
              {user && <p className="text-xs text-gray-500">Welcome, {user.name}</p>}
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
              <Button
                onClick={onLogout}
                variant="ghost"
                size="sm"
                className="ml-4"
              >
                <LogOut className="w-4 h-4" />
              </Button>
            )}
          </div>
        </div>
      </div>
    </motion.nav>
  );
}