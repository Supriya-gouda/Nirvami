import { useEffect, useState } from 'react';
import { motion, AnimatePresence } from 'motion/react';
import { X, CheckCheck, AlertTriangle, Info, Bell } from 'lucide-react';
import { Card } from './ui/card';
import { Button } from './ui/button';
import { Badge } from './ui/badge';
import { ScrollArea } from './ui/scroll-area';
import api from '../services/api';
import type { PageType } from '../App';
import type { User } from '../contexts/AuthContext';
import type { Alert } from '../types/api.types';

interface NotificationCenterProps {
  user: User | null;
  onClose: () => void;
  onNavigate: (page: PageType) => void;
}

export function NotificationCenter({ user, onClose }: NotificationCenterProps) {
  const [alerts, setAlerts] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadAlerts();
  }, []);

  const loadAlerts = async () => {
    try {
      setLoading(true);
      // Fetch both alerts and notifications
      const [alertsData, notificationsData] = await Promise.all([
        api.getAlerts().catch(() => []),
        api.getNotifications(false).catch(() => [])
      ]);
      
      // Combine and sort by created_at/timestamp
      const combined = [...(alertsData || []), ...(notificationsData || [])];
      combined.sort((a, b) => {
        const dateA = new Date(a.created_at || a.timestamp || 0);
        const dateB = new Date(b.created_at || b.timestamp || 0);
        return dateB.getTime() - dateA.getTime();
      });
      
      setAlerts(combined);
    } catch (err) {
      console.error('Failed to load notifications:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleMarkRead = async (alertId: string) => {
    try {
      const item = alerts.find(a => a.id === alertId);
      if (item && item.body) {
        // It's a notification
        await api.markNotificationRead(alertId);
      } else {
        // It's an alert
        await api.markAlertRead(alertId);
      }
      setAlerts(alerts.map(a => a.id === alertId ? { ...a, read: true } : a));
    } catch (err) {
      console.error('Failed to mark item as read:', err);
    }
  };

  const handleMarkAllRead = async () => {
    try {
      const unreadItems = alerts.filter(a => !a.read);
      await Promise.all(unreadItems.map(item => {
        if (item.body) {
          return api.markNotificationRead(item.id);
        } else {
          return api.markAlertRead(item.id);
        }
      }));
      setAlerts(alerts.map(a => ({ ...a, read: true })));
    } catch (err) {
      console.error('Failed to mark all items as read:', err);
    }
  };

  const getSeverityColor = (item: any) => {
    // Handle both alert severity and notification type
    const severity = item.severity || item.type || 'low';
    const colors = {
      low: 'bg-blue-100 text-blue-800 border-blue-200',
      info: 'bg-blue-100 text-blue-800 border-blue-200',
      medium: 'bg-yellow-100 text-yellow-800 border-yellow-200',
      warning: 'bg-yellow-100 text-yellow-800 border-yellow-200',
      high: 'bg-red-100 text-red-800 border-red-200',
      error: 'bg-red-100 text-red-800 border-red-200'
    };
    return colors[severity as keyof typeof colors] || colors.low;
  };

  const getSeverityIcon = (item: any) => {
    const severity = item.severity || item.type || 'low';
    const icons = {
      low: <Info className="w-5 h-5" />,
      info: <Info className="w-5 h-5" />,
      medium: <AlertTriangle className="w-5 h-5" />,
      warning: <AlertTriangle className="w-5 h-5" />,
      high: <AlertTriangle className="w-5 h-5" />,
      error: <AlertTriangle className="w-5 h-5" />
    };
    return icons[severity as keyof typeof icons] || icons.low;
  };

  const getAlertTypeLabel = (item: any) => {
    // Handle both alert_type and notification title
    if (item.title && !item.alert_type) {
      return 'Health Alert'; // For notifications
    }
    
    const type = item.alert_type || 'notification';
    const labels = {
      crisis_detected: 'Crisis Alert',
      high_stress: 'High Stress',
      low_mood: 'Low Mood',
      irregular_pattern: 'Irregular Pattern',
      wellness_milestone: 'Milestone Achieved',
      notification: 'Notification'
    };
    return labels[type as keyof typeof labels] || type;
  };

  const formatTimestamp = (timestamp: string) => {
    const date = new Date(timestamp);
    const now = new Date();
    const diffMs = now.getTime() - date.getTime();
    const diffMins = Math.floor(diffMs / 60000);
    const diffHours = Math.floor(diffMs / 3600000);
    const diffDays = Math.floor(diffMs / 86400000);

    if (diffMins < 60) return `${diffMins}m ago`;
    if (diffHours < 24) return `${diffHours}h ago`;
    if (diffDays < 7) return `${diffDays}d ago`;
    return date.toLocaleDateString();
  };

  const unreadCount = alerts.filter(a => !a.read).length;

  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
      className="fixed inset-0 bg-black/50 z-50 flex items-center justify-center p-4"
      onClick={onClose}
    >
      <motion.div
        initial={{ scale: 0.9, y: 20 }}
        animate={{ scale: 1, y: 0 }}
        exit={{ scale: 0.9, y: 20 }}
        onClick={(e) => e.stopPropagation()}
        className="bg-white rounded-2xl shadow-2xl w-full max-w-2xl max-h-[80vh] flex flex-col"
      >
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-full bg-gradient-to-br from-purple-500 to-pink-500 flex items-center justify-center">
              <Bell className="w-5 h-5 text-white" />
            </div>
            <div>
              <h2 className="text-2xl font-bold">Notifications</h2>
              <p className="text-sm text-gray-500">
                {unreadCount > 0 ? `${unreadCount} unread` : 'All caught up!'}
              </p>
            </div>
          </div>
          <div className="flex items-center gap-2">
            {unreadCount > 0 && (
              <Button
                variant="ghost"
                size="sm"
                onClick={handleMarkAllRead}
                className="text-purple-600 hover:text-purple-700"
              >
                <CheckCheck className="w-4 h-4 mr-2" />
                Mark all read
              </Button>
            )}
            <Button variant="ghost" size="icon" onClick={onClose}>
              <X className="w-5 h-5" />
            </Button>
          </div>
        </div>

        {/* Content */}
        <ScrollArea className="flex-1 p-6">
          {loading ? (
            <div className="flex items-center justify-center py-12">
              <div className="w-8 h-8 border-4 border-purple-200 border-t-purple-600 rounded-full animate-spin" />
            </div>
          ) : alerts.length === 0 ? (
            <div className="text-center py-12">
              <Bell className="w-16 h-16 text-gray-300 mx-auto mb-4" />
              <p className="text-gray-500 text-lg">No notifications yet</p>
              <p className="text-gray-400 text-sm mt-2">
                We'll notify you about important updates
              </p>
            </div>
          ) : (
            <div className="space-y-3">
              <AnimatePresence>
                {alerts.map((alert, index) => (
                  <motion.div
                    key={alert.id}
                    initial={{ opacity: 0, x: -20 }}
                    animate={{ opacity: 1, x: 0 }}
                    exit={{ opacity: 0, x: 20 }}
                    transition={{ delay: index * 0.05 }}
                  >
                    <Card
                      className={`p-4 transition-all cursor-pointer hover:shadow-md border-l-4 ${
                        !alert.read ? 'bg-purple-50 border-l-purple-500' : 'border-l-gray-200'
                      }`}
                      onClick={() => !alert.read && handleMarkRead(alert.id)}
                    >
                      <div className="flex items-start gap-3">
                        <div className={`p-2 rounded-lg ${getSeverityColor(alert)}`}>
                          {getSeverityIcon(alert)}
                        </div>
                        
                        <div className="flex-1 min-w-0">
                          <div className="flex items-center gap-2 mb-1">
                            <Badge
                              variant="outline"
                              className={`text-xs ${getSeverityColor(alert)}`}
                            >
                              {getAlertTypeLabel(alert)}
                            </Badge>
                            {!alert.read && (
                              <div className="w-2 h-2 rounded-full bg-purple-600" />
                            )}
                            <span className="text-xs text-gray-400 ml-auto">
                              {formatTimestamp(alert.created_at || alert.timestamp)}
                            </span>
                          </div>
                          
                          <h3 className="font-semibold text-gray-900 mb-1">
                            {alert.title}
                          </h3>
                          <p className="text-sm text-gray-600 line-clamp-2 whitespace-pre-line">
                            {alert.body || alert.message}
                          </p>
                        </div>
                      </div>
                    </Card>
                  </motion.div>
                ))}
              </AnimatePresence>
            </div>
          )}
        </ScrollArea>
      </motion.div>
    </motion.div>
  );
}
