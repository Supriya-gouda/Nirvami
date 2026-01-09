import { useState, useEffect } from 'react';
import { BookOpen, Play, Youtube, AlertCircle } from 'lucide-react';
import { Button } from '../ui/button';
import { Card, CardContent } from '../ui/card';
import { Badge } from '../ui/badge';

interface PracticeLearnSectionProps {
  practiceName: string;
  category: string;
  content: string;
  onStartPractice: () => void;
}

const YOUTUBE_API_KEY = import.meta.env.VITE_YOUTUBE_API_KEY;

export function PracticeLearnSection({
  practiceName,
  category,
  content,
  onStartPractice
}: PracticeLearnSectionProps) {
  const [videoId, setVideoId] = useState<string | null>(null);
  const [isLoadingVideo, setIsLoadingVideo] = useState(true);
  const [videoError, setVideoError] = useState(false);

  // Generate YouTube search query based on recommendation
  const generateYouTubeSearchQuery = (): string => {
    let query = practiceName;
    if (category === 'yoga') query += ' yoga pose tutorial';
    else if (category === 'breathing') query += ' pranayama breathing tutorial';
    else if (category === 'meditation') query += ' meditation guide';
    else if (category === 'ayurveda') query += ' ayurveda guide';
    else query += ' how to';
    
    return query;
  };

  // Fetch YouTube video on component mount
  useEffect(() => {
    const fetchYouTubeVideo = async () => {
      try {
        setIsLoadingVideo(true);
        setVideoError(false);

        const searchQuery = generateYouTubeSearchQuery();
        const response = await fetch(
          `https://www.googleapis.com/youtube/v3/search?part=snippet&q=${encodeURIComponent(searchQuery)}&type=video&maxResults=1&key=${YOUTUBE_API_KEY}`
        );

        if (!response.ok) {
          throw new Error('YouTube API request failed');
        }

        const data = await response.json();
        
        if (data.items && data.items.length > 0) {
          const topVideo = data.items[0];
          setVideoId(topVideo.id.videoId);
          console.log(`✅ Found YouTube video: ${topVideo.snippet.title}`);
        } else {
          console.warn('No YouTube videos found for query:', searchQuery);
          setVideoError(true);
        }
      } catch (error) {
        console.error('Failed to fetch YouTube video:', error);
        setVideoError(true);
      } finally {
        setIsLoadingVideo(false);
      }
    };

    fetchYouTubeVideo();
  }, [practiceName, category]);

  return (
    <div className="space-y-6 pb-32">
      {/* Learn Header */}
      <div className="flex items-center gap-3 mb-4">
        <div className="w-12 h-12 rounded-full bg-purple-100 flex items-center justify-center">
          <BookOpen className="w-6 h-6 text-purple-600" />
        </div>
        <div>
          <h3 className="text-xl font-semibold text-gray-900">Learn First</h3>
          <p className="text-sm text-gray-600">
            Understand the technique before practicing
          </p>
        </div>
      </div>

      {/* Content Description */}
      <Card>
        <CardContent className="pt-6">
          <div className="prose prose-sm max-w-none">
            <h4 className="text-lg font-semibold text-gray-900 mb-3">{practiceName}</h4>
            <Badge className="mb-3" variant="outline">
              {category.charAt(0).toUpperCase() + category.slice(1)}
            </Badge>
            <p className="text-gray-700 whitespace-pre-line">{content}</p>
          </div>
        </CardContent>
      </Card>

      {/* Video Learning Section */}
      <Card className="scroll-mt-4">
        <CardContent className="pt-6">
          <div className="space-y-4">
            <div className="flex items-center justify-center gap-3">
              <div className="inline-flex items-center justify-center w-12 h-12 rounded-full bg-red-50">
                <Youtube className="w-6 h-6 text-red-600" />
              </div>
              <h4 className="text-lg font-semibold text-gray-900">
                Tutorial Video
              </h4>
            </div>

            {/* Loading State */}
            {isLoadingVideo && (
              <div className="flex items-center justify-center py-8">
                <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-red-600"></div>
                <p className="ml-3 text-gray-600">Finding the best tutorial...</p>
              </div>
            )}

            {/* Video Embed - Optimized for visibility */}
            {!isLoadingVideo && videoId && (
              <div className="relative w-full aspect-video min-h-[360px] bg-black rounded-lg">
                <iframe
                  className="absolute top-0 left-0 w-full h-full rounded-lg shadow-lg"
                  src={`https://www.youtube.com/embed/${videoId}`}
                  title="Practice Tutorial Video"
                  allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
                  allowFullScreen
                ></iframe>
              </div>
            )}

            {/* Fallback - Video Not Found */}
            {!isLoadingVideo && videoError && (
              <div className="bg-amber-50 border border-amber-200 rounded-lg p-6 space-y-3">
                <div className="flex items-center gap-2 text-amber-800">
                  <AlertCircle className="w-5 h-5" />
                  <h5 className="font-semibold">Video Not Available</h5>
                </div>
                <div className="text-sm text-amber-700 space-y-2">
                  <p className="font-medium">Follow these text instructions instead:</p>
                  <div className="bg-white rounded p-4 space-y-2">
                    <p className="whitespace-pre-line">{content}</p>
                  </div>
                  <p className="text-xs mt-3">
                    💡 <strong>Tip:</strong> If you're unfamiliar with this practice, consider consulting a certified instructor before attempting it on your own.
                  </p>
                </div>
              </div>
            )}
          </div>
        </CardContent>
      </Card>

      {/* Benefits Section (if applicable) */}
      {(category === 'yoga' || category === 'breathing' || category === 'meditation') && (
        <Card>
          <CardContent className="pt-6">
            <h4 className="text-md font-semibold text-gray-900 mb-3">Benefits</h4>
            <ul className="space-y-2 text-sm text-gray-700">
              {category === 'yoga' && (
                <>
                  <li className="flex items-start gap-2">
                    <span className="text-green-500 mt-1">•</span>
                    <span>Improves flexibility and strength</span>
                  </li>
                  <li className="flex items-start gap-2">
                    <span className="text-green-500 mt-1">•</span>
                    <span>Enhances body awareness and posture</span>
                  </li>
                  <li className="flex items-start gap-2">
                    <span className="text-green-500 mt-1">•</span>
                    <span>Reduces stress and promotes relaxation</span>
                  </li>
                </>
              )}
              {category === 'breathing' && (
                <>
                  <li className="flex items-start gap-2">
                    <span className="text-green-500 mt-1">•</span>
                    <span>Calms the nervous system</span>
                  </li>
                  <li className="flex items-start gap-2">
                    <span className="text-green-500 mt-1">•</span>
                    <span>Increases oxygen flow and energy</span>
                  </li>
                  <li className="flex items-start gap-2">
                    <span className="text-green-500 mt-1">•</span>
                    <span>Improves focus and mental clarity</span>
                  </li>
                </>
              )}
              {category === 'meditation' && (
                <>
                  <li className="flex items-start gap-2">
                    <span className="text-green-500 mt-1">•</span>
                    <span>Reduces anxiety and stress</span>
                  </li>
                  <li className="flex items-start gap-2">
                    <span className="text-green-500 mt-1">•</span>
                    <span>Enhances emotional well-being</span>
                  </li>
                  <li className="flex items-start gap-2">
                    <span className="text-green-500 mt-1">•</span>
                    <span>Improves concentration and mindfulness</span>
                  </li>
                </>
              )}
            </ul>
          </CardContent>
        </Card>
      )}

      {/* Start Practice Button */}
      <div className="mt-8 bg-gradient-to-t from-white via-white to-transparent pt-6 pb-4">
        <Button
          onClick={onStartPractice}
          size="lg"
          style={{
            background: '#9b33e1',
            color: 'white',
            border: 'none',
            fontWeight: '600',
            boxShadow: '0 2px 8px rgba(155, 51, 225, 0.3)',
            transition: 'all 0.2s ease'
          }}
          className="w-full hover:brightness-110 hover:shadow-lg"
          onMouseEnter={(e) => {
            e.currentTarget.style.background = '#8a2bc7';
            e.currentTarget.style.boxShadow = '0 4px 12px rgba(155, 51, 225, 0.4)';
          }}
          onMouseLeave={(e) => {
            e.currentTarget.style.background = '#9b33e1';
            e.currentTarget.style.boxShadow = '0 2px 8px rgba(155, 51, 225, 0.3)';
          }}
        >
          <Play className="w-5 h-5 mr-2" />
          Ready to Practice
        </Button>
        <p className="text-xs text-center text-gray-500 mt-2">
          Make sure you've watched the tutorial first
        </p>
      </div>
    </div>
  );
}
