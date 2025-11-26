import { useEffect, useState } from 'react';
import { motion } from 'motion/react';
import { Sparkles, Calendar, Info } from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from './ui/card';
import {
  Tooltip,
  TooltipContent,
  TooltipProvider,
  TooltipTrigger,
} from './ui/tooltip';
import api from '../services/api';
import type { AuraEntry } from '../types/api.types';

interface AuraHistoryProps {
  days?: number;
  showTitle?: boolean;
  compact?: boolean;
}

const AURA_COLORS: Record<string, { hex: string; name: string }> = {
  red: { hex: '#E53935', name: 'Energy & Courage' },
  orange: { hex: '#FB8C00', name: 'Joy & Playfulness' },
  yellow: { hex: '#FDD835', name: 'Optimism & Clarity' },
  green: { hex: '#66BB6A', name: 'Balance & Healing' },
  blue: { hex: '#42A5F5', name: 'Calm & Communication' },
  teal: { hex: '#26A69A', name: 'Emotional Healing' },
  indigo: { hex: '#1A237E', name: 'Depth & Protection' },
  violet: { hex: '#8E24AA', name: 'Insight & Transformation' },
  pink: { hex: '#EC407A', name: 'Self-Love & Gentleness' },
  white: { hex: '#F5F5F5', name: 'Clarity & Reset' },
  grey: { hex: '#9E9E9E', name: 'Neutral & Balance' },
};

export function AuraHistory({ days = 30, showTitle = true, compact = false }: AuraHistoryProps) {
  const [auraHistory, setAuraHistory] = useState<AuraEntry[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadHistory();
  }, [days]);

  const loadHistory = async () => {
    try {
      setLoading(true);
      const data = await api.getAuraTimeline(days);
      setAuraHistory(data);
    } catch (err) {
      console.error('Failed to load aura history:', err);
      setAuraHistory([]);
    } finally {
      setLoading(false);
    }
  };

  const formatDate = (dateStr: string) => {
    const date = new Date(dateStr);
    const now = new Date();
    const diffDays = Math.floor((now.getTime() - date.getTime()) / (1000 * 60 * 60 * 24));

    if (diffDays === 0) return 'Today';
    if (diffDays === 1) return 'Yesterday';
    if (diffDays < 7) return `${diffDays} days ago`;
    
    return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
  };

  const getColorInfo = (colorName: string) => {
    return AURA_COLORS[colorName.toLowerCase()] || AURA_COLORS.grey;
  };

  if (loading) {
    return (
      <Card>
        {showTitle && (
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Sparkles className="w-5 h-5" />
              Aura History
            </CardTitle>
          </CardHeader>
        )}
        <CardContent>
          <div className="text-center py-6 text-gray-500">Loading aura history...</div>
        </CardContent>
      </Card>
    );
  }

  if (auraHistory.length === 0) {
    return (
      <Card>
        {showTitle && (
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Sparkles className="w-5 h-5" />
              Aura History
            </CardTitle>
          </CardHeader>
        )}
        <CardContent>
          <div className="text-center py-6">
            <Calendar className="w-12 h-12 text-gray-300 mx-auto mb-2" />
            <p className="text-gray-500">No aura data yet</p>
            <p className="text-sm text-gray-400 mt-1">Log emotions to start building your aura history</p>
          </div>
        </CardContent>
      </Card>
    );
  }

  if (compact) {
    // Compact view - just circles in a row
    return (
      <div className="flex flex-wrap gap-2">
        <TooltipProvider>
          {auraHistory.slice(0, 14).map((aura, index) => {
            const colorInfo = getColorInfo(aura.color_code);
            return (
              <Tooltip key={aura.id}>
                <TooltipTrigger>
                  <motion.div
                    initial={{ opacity: 0, scale: 0 }}
                    animate={{ opacity: 1, scale: 1 }}
                    transition={{ delay: index * 0.05 }}
                    className="w-10 h-10 rounded-full border-2 border-white shadow-lg cursor-pointer hover:scale-110 transition-transform"
                    style={{
                      backgroundColor: colorInfo.hex,
                      boxShadow: `0 0 ${aura.glow_level || 50}px ${colorInfo.hex}50`,
                    }}
                  />
                </TooltipTrigger>
                <TooltipContent>
                  <div className="text-sm">
                    <div className="font-semibold">{formatDate(aura.date)}</div>
                    <div className="text-gray-400">{colorInfo.name}</div>
                    <div className="text-xs text-gray-500 capitalize">{aura.aura_type}</div>
                  </div>
                </TooltipContent>
              </Tooltip>
            );
          })}
        </TooltipProvider>
      </div>
    );
  }

  // Full view with more details
  return (
    <Card>
      {showTitle && (
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Sparkles className="w-5 h-5" />
            Aura History
          </CardTitle>
          <CardDescription>Your energetic journey over the past {days} days</CardDescription>
        </CardHeader>
      )}
      <CardContent>
        <div className="space-y-4">
          {/* Timeline Grid */}
          <div className="grid grid-cols-7 gap-2">
            {auraHistory.map((aura, index) => {
              const colorInfo = getColorInfo(aura.color_code);
              return (
                <TooltipProvider key={aura.id}>
                  <Tooltip>
                    <TooltipTrigger>
                      <motion.div
                        initial={{ opacity: 0, scale: 0 }}
                        animate={{ opacity: 1, scale: 1 }}
                        transition={{ delay: index * 0.02 }}
                        className="relative group"
                      >
                        <div
                          className="w-full aspect-square rounded-lg border-2 border-white shadow-md cursor-pointer hover:scale-110 transition-transform"
                          style={{
                            backgroundColor: colorInfo.hex,
                            opacity: 0.3 + (aura.intensity || 50) / 100 * 0.7,
                          }}
                        >
                          {/* Glow effect */}
                          <div
                            className="absolute inset-0 rounded-lg blur-sm -z-10"
                            style={{
                              backgroundColor: colorInfo.hex,
                              opacity: (aura.glow_level || 50) / 200,
                            }}
                          />
                        </div>
                      </motion.div>
                    </TooltipTrigger>
                    <TooltipContent>
                      <div className="text-sm space-y-1">
                        <div className="font-semibold">{formatDate(aura.date)}</div>
                        <div style={{ color: colorInfo.hex }}>{colorInfo.name}</div>
                        <div className="text-xs text-gray-500 capitalize">
                          Type: {aura.aura_type || 'balanced'}
                        </div>
                        <div className="text-xs text-gray-500">
                          Intensity: {Math.round(aura.intensity || 50)}%
                        </div>
                        {aura.emotion_basis && Object.keys(aura.emotion_basis).length > 0 && (
                          <div className="text-xs text-gray-400 mt-1">
                            Based on: {Object.keys(aura.emotion_basis).slice(0, 2).join(', ')}
                          </div>
                        )}
                      </div>
                    </TooltipContent>
                  </Tooltip>
                </TooltipProvider>
              );
            })}
          </div>

          {/* Legend */}
          <div className="mt-6 pt-4 border-t">
            <div className="flex items-center gap-2 text-sm text-gray-600 mb-3">
              <Info className="w-4 h-4" />
              <span className="font-medium">Aura Color Meanings</span>
            </div>
            <div className="grid grid-cols-2 md:grid-cols-3 gap-2 text-xs">
              {Object.entries(AURA_COLORS).slice(0, 6).map(([key, { hex, name }]) => (
                <div key={key} className="flex items-center gap-2">
                  <div
                    className="w-4 h-4 rounded-full border border-gray-300"
                    style={{ backgroundColor: hex }}
                  />
                  <span className="text-gray-600">{name}</span>
                </div>
              ))}
            </div>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}
