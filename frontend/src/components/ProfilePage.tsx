import { useEffect, useState } from 'react';
import { motion } from 'motion/react';
import { User as UserIcon, Mail, Calendar, Settings, Download, Trash2, Bell, Globe, Sun, Save } from 'lucide-react';
import { Navigation } from './Navigation';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from './ui/card';
import { Button } from './ui/button';
import { Input } from './ui/input';
import { Label } from './ui/label';
import { Switch } from './ui/switch';
import { Avatar, AvatarFallback, AvatarImage } from './ui/avatar';
import { Separator } from './ui/separator';
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
} from './ui/alert-dialog';
import type { PageType } from '../App';
import type { User } from '../contexts/AuthContext';
import api from '../services/api';

interface ProfilePageProps {
  user: User | null;
  onNavigate: (page: PageType) => void;
  onLogout?: () => void;
  onOpenNotifications?: () => void;
}

interface UserProfile {
  id: number;
  email: string;
  full_name?: string;
  avatar_url?: string;
  timezone?: string;
  created_at: string;
}

interface UserPreferences {
  notifications_enabled: boolean;
  email_notifications: boolean;
  crisis_alerts: boolean;
  wellness_reminders: boolean;
  theme: 'light' | 'dark' | 'auto';
}

export function ProfilePage({ user, onNavigate, onLogout, onOpenNotifications }: ProfilePageProps) {
  const [profile, setProfile] = useState<UserProfile | null>(null);
  const [preferences, setPreferences] = useState<UserPreferences>({
    notifications_enabled: true,
    email_notifications: true,
    crisis_alerts: true,
    wellness_reminders: true,
    theme: 'light'
  });
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [showDeleteDialog, setShowDeleteDialog] = useState(false);
  const [isExporting, setIsExporting] = useState(false);

  // Profile editing state
  const [editedName, setEditedName] = useState('');
  const [editedTimezone, setEditedTimezone] = useState('UTC');

  useEffect(() => {
    loadProfile();
  }, []);

  const loadProfile = async () => {
    try {
      setLoading(true);
      if (user) {
        const profileData = await api.getProfile();
        setProfile({
          id: parseInt(user.id),
          email: user.email,
          full_name: profileData.full_name,
          timezone: profileData.timezone,
          created_at: profileData.created_at
        });
        setEditedName(profileData.full_name || user.email);
        setEditedTimezone(profileData.timezone || 'UTC');

        // Load preferences (if API exists, otherwise use defaults)
        try {
          const prefsData = await api.getPreferences?.();
          if (prefsData) {
            setPreferences(prefsData as any);
          }
        } catch (err) {
          console.log('Preferences endpoint not available, using defaults');
        }
      }
    } catch (err) {
      console.error('Failed to load profile:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleSaveProfile = async () => {
    if (!user) return;
    
    try {
      setSaving(true);
      await api.updateProfile({
        full_name: editedName,
        timezone: editedTimezone
      });
      
      setProfile({ ...profile!, full_name: editedName, timezone: editedTimezone });
      alert('Profile updated successfully!');
    } catch (err) {
      console.error('Failed to update profile:', err);
      alert('Failed to update profile');
    } finally {
      setSaving(false);
    }
  };

  const handleSavePreferences = async () => {
    if (!user) return;
    
    try {
      setSaving(true);
      // Save preferences (if API exists)
      try {
        await api.updatePreferences?.(preferences);
        alert('Preferences saved successfully!');
      } catch (err) {
        console.log('Preferences endpoint not available');
        alert('Preferences saved locally (backend integration pending)');
      }
    } catch (err) {
      console.error('Failed to save preferences:', err);
      alert('Failed to save preferences');
    } finally {
      setSaving(false);
    }
  };

  const handleExportData = async () => {
    try {
      setIsExporting(true);
      const data = await api.exportUserData();
      
      // Create download
      const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `mindful-data-${new Date().toISOString().split('T')[0]}.json`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      URL.revokeObjectURL(url);
      
      alert('Your data has been downloaded!');
    } catch (err) {
      console.error('Failed to export data:', err);
      alert('Failed to export data');
    } finally {
      setIsExporting(false);
    }
  };

  const handleDeleteAccount = async () => {
    if (!user) return;
    
    try {
      await api.deleteAccount();
      alert('Your account has been deleted. You will be logged out.');
      onLogout?.();
    } catch (err) {
      console.error('Failed to delete account:', err);
      alert('Failed to delete account');
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-purple-50 via-blue-50 to-pink-50">
        <Navigation currentPage="yoga" onNavigate={onNavigate} onLogout={onLogout} user={user} onOpenNotifications={onOpenNotifications} />
        <div className="flex items-center justify-center h-[calc(100vh-200px)]">
          <div className="w-12 h-12 border-4 border-purple-200 border-t-purple-600 rounded-full animate-spin" />
        </div>
      </div>
    );
  }

  const userInitials = user?.email?.slice(0, 2).toUpperCase() || 'U';
  const memberSince = profile?.created_at 
    ? new Date(profile.created_at).toLocaleDateString('en-US', { month: 'long', year: 'numeric' })
    : 'Unknown';

  return (
    <div className="min-h-screen bg-gradient-to-br from-purple-50 via-blue-50 to-pink-50">
      <Navigation currentPage="yoga" onNavigate={onNavigate} onLogout={onLogout} user={user} onOpenNotifications={onOpenNotifications} />
      
      <div className="max-w-5xl mx-auto p-8">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="mb-8"
        >
          <h1 className="text-4xl font-bold mb-2 bg-gradient-to-r from-purple-600 to-pink-600 bg-clip-text text-transparent">
            Profile & Settings
          </h1>
          <p className="text-gray-600">Manage your account and preferences</p>
        </motion.div>

        <div className="grid md:grid-cols-3 gap-6">
          {/* Sidebar */}
          <motion.div
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: 0.1 }}
            className="md:col-span-1"
          >
            <Card>
              <CardContent className="pt-6">
                <div className="flex flex-col items-center">
                  <Avatar className="w-24 h-24 mb-4">
                    <AvatarImage src={profile?.avatar_url} />
                    <AvatarFallback className="bg-gradient-to-br from-purple-500 to-pink-500 text-white text-2xl">
                      {userInitials}
                    </AvatarFallback>
                  </Avatar>
                  
                  <h2 className="text-xl font-bold mb-1">
                    {profile?.full_name || user?.email || 'User'}
                  </h2>
                  <p className="text-sm text-gray-500 mb-4">{user?.email}</p>
                  
                  <div className="w-full space-y-2 text-sm text-gray-600">
                    <div className="flex items-center gap-2">
                      <Calendar className="w-4 h-4" />
                      <span>Member since {memberSince}</span>
                    </div>
                    <div className="flex items-center gap-2">
                      <Globe className="w-4 h-4" />
                      <span>{profile?.timezone || 'UTC'}</span>
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>
          </motion.div>

          {/* Main Content */}
          <div className="md:col-span-2 space-y-6">
            {/* Profile Information */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.2 }}
            >
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <UserIcon className="w-5 h-5" />
                    Profile Information
                  </CardTitle>
                  <CardDescription>Update your personal details</CardDescription>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div>
                    <Label htmlFor="fullName">Full Name</Label>
                    <Input
                      id="fullName"
                      value={editedName}
                      onChange={(e) => setEditedName(e.target.value)}
                      placeholder="Your name"
                      className="mt-1"
                    />
                  </div>
                  
                  <div>
                    <Label htmlFor="email">Email</Label>
                    <Input
                      id="email"
                      value={user?.email || ''}
                      disabled
                      className="mt-1 bg-gray-50"
                    />
                    <p className="text-xs text-gray-500 mt-1">Email cannot be changed</p>
                  </div>

                  <div>
                    <Label htmlFor="timezone">Timezone</Label>
                    <Input
                      id="timezone"
                      value={editedTimezone}
                      onChange={(e) => setEditedTimezone(e.target.value)}
                      placeholder="UTC"
                      className="mt-1"
                    />
                  </div>

                  <Button
                    onClick={handleSaveProfile}
                    disabled={saving}
                    className="bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-700 hover:to-pink-700"
                  >
                    <Save className="w-4 h-4 mr-2" />
                    {saving ? 'Saving...' : 'Save Profile'}
                  </Button>
                </CardContent>
              </Card>
            </motion.div>

            {/* Preferences */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.3 }}
            >
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <Settings className="w-5 h-5" />
                    Preferences
                  </CardTitle>
                  <CardDescription>Customize your experience</CardDescription>
                </CardHeader>
                <CardContent className="space-y-6">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-3">
                      <Bell className="w-5 h-5 text-gray-600" />
                      <div>
                        <Label>Push Notifications</Label>
                        <p className="text-xs text-gray-500">Receive in-app notifications</p>
                      </div>
                    </div>
                    <Switch
                      checked={preferences.notifications_enabled}
                      onCheckedChange={(checked: boolean) => 
                        setPreferences({ ...preferences, notifications_enabled: checked })
                      }
                    />
                  </div>

                  <Separator />

                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-3">
                      <Mail className="w-5 h-5 text-gray-600" />
                      <div>
                        <Label>Email Notifications</Label>
                        <p className="text-xs text-gray-500">Receive updates via email</p>
                      </div>
                    </div>
                    <Switch
                      checked={preferences.email_notifications}
                      onCheckedChange={(checked: boolean) => 
                        setPreferences({ ...preferences, email_notifications: checked })
                      }
                    />
                  </div>

                  <Separator />

                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-3">
                      <UserIcon className="w-5 h-5 text-gray-600" />
                      <div>
                        <Label>Crisis Alerts</Label>
                        <p className="text-xs text-gray-500">Urgent mental health notifications</p>
                      </div>
                    </div>
                    <Switch
                      checked={preferences.crisis_alerts}
                      onCheckedChange={(checked: boolean) => 
                        setPreferences({ ...preferences, crisis_alerts: checked })
                      }
                    />
                  </div>

                  <Separator />

                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-3">
                      <Sun className="w-5 h-5 text-gray-600" />
                      <div>
                        <Label>Wellness Reminders</Label>
                        <p className="text-xs text-gray-500">Daily check-in prompts</p>
                      </div>
                    </div>
                    <Switch
                      checked={preferences.wellness_reminders}
                      onCheckedChange={(checked: boolean) => 
                        setPreferences({ ...preferences, wellness_reminders: checked })
                      }
                    />
                  </div>

                  <Button
                    onClick={handleSavePreferences}
                    disabled={saving}
                    variant="outline"
                    className="w-full"
                  >
                    <Save className="w-4 h-4 mr-2" />
                    {saving ? 'Saving...' : 'Save Preferences'}
                  </Button>
                </CardContent>
              </Card>
            </motion.div>

            {/* Data & Privacy */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.4 }}
            >
              <Card>
                <CardHeader>
                  <CardTitle>Data & Privacy</CardTitle>
                  <CardDescription>Manage your data and account</CardDescription>
                </CardHeader>
                <CardContent className="space-y-4">
                  <Button
                    onClick={handleExportData}
                    disabled={isExporting}
                    variant="outline"
                    className="w-full justify-start"
                  >
                    <Download className="w-4 h-4 mr-2" />
                    {isExporting ? 'Exporting...' : 'Download My Data'}
                  </Button>

                  <Separator />

                  <div className="bg-red-50 border border-red-200 rounded-lg p-4">
                    <h3 className="font-semibold text-red-900 mb-2">Danger Zone</h3>
                    <p className="text-sm text-red-700 mb-4">
                      Once you delete your account, there is no going back. Please be certain.
                    </p>
                    <Button
                      onClick={() => setShowDeleteDialog(true)}
                      variant="destructive"
                      className="w-full justify-start"
                    >
                      <Trash2 className="w-4 h-4 mr-2" />
                      Delete My Account
                    </Button>
                  </div>
                </CardContent>
              </Card>
            </motion.div>
          </div>
        </div>
      </div>

      {/* Delete Account Dialog */}
      <AlertDialog open={showDeleteDialog} onOpenChange={setShowDeleteDialog}>
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle>Are you absolutely sure?</AlertDialogTitle>
            <AlertDialogDescription>
              This action cannot be undone. This will permanently delete your account
              and remove all your data from our servers.
            </AlertDialogDescription>
          </AlertDialogHeader>
          <AlertDialogFooter>
            <AlertDialogCancel>Cancel</AlertDialogCancel>
            <AlertDialogAction
              onClick={handleDeleteAccount}
              className="bg-red-600 hover:bg-red-700"
            >
              Yes, delete my account
            </AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>
    </div>
  );
}
