import { useState } from 'react';
import { motion } from 'motion/react';
import { Upload, File, Check, AlertCircle, Loader2, Watch, Activity, Heart } from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from './ui/card';
import { Button } from './ui/button';
import { Alert, AlertDescription } from './ui/alert';
import { toast } from 'sonner';
import api from '../services/api';

interface WatchDataUploadProps {
  onSuccess?: (response?: any) => void;
}

export function WatchDataUpload({ onSuccess }: WatchDataUploadProps) {
  const [file, setFile] = useState<File | null>(null);
  const [uploading, setUploading] = useState(false);
  const [status, setStatus] = useState<'idle' | 'success' | 'error'>('idle');
  const [message, setMessage] = useState('');
  const [stats, setStats] = useState<any>(null);
  const [uploadTimestamp, setUploadTimestamp] = useState<string | null>(null);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const selectedFile = e.target.files?.[0];
    if (selectedFile) {
      if (!selectedFile.name.endsWith('.xml')) {
        setStatus('error');
        setMessage('Please select an XML file exported from Apple Health');
        setFile(null);
        return;
      }
      setFile(selectedFile);
      setStatus('idle');
      setMessage('');
    }
  };

  const handleUpload = async () => {
    if (!file) {
      toast.error('Please select an XML file first');
      return;
    }

    try {
      setUploading(true);
      setStatus('idle');
      setMessage('Uploading and processing your Apple Watch data...');
      // Clear previous results when starting new upload
      setStats(null);
      setUploadTimestamp(null);

      const formData = new FormData();
      formData.append('file', file);

      const response = await api.uploadWatchXML(formData);

      setStatus('success');
      setStats(response);
      setUploadTimestamp(new Date().toLocaleString());
      
      console.log('XML upload response:', response);
      
      if (response.success) {
        const metrics = response.latest_metrics || {};
        const metricsMsg = [
          metrics.avg_heart_rate ? `HR: ${metrics.avg_heart_rate} bpm` : null,
          metrics.steps ? `Steps: ${metrics.steps.toLocaleString()}` : null,
          metrics.sleep_hours ? `Sleep: ${metrics.sleep_hours}h` : null,
        ].filter(Boolean).join(' | ');
        
        setMessage(response.message || 'Apple Watch data processed successfully!');
        
        // Show analysis result if available
        if (response.analysis) {
          console.log('Analysis result from XML upload:', response.analysis);
          const analysisMsg = response.analysis.has_risks 
            ? `${response.analysis.risks.length} health concern(s) detected from watch data` 
            : 'No health risks detected';
          
          toast.success(`✅ Success! Processed ${response.days_processed} days of data`, {
            description: analysisMsg,
            duration: 5000
          });
        } else {
          toast.success(`✅ Success! Processed ${response.days_processed} days of data`, {
            description: metricsMsg || 'Data synced successfully'
          });
        }
      } else {
        toast.warning(response.message || 'No usable health data found in the file');
      }

      if (onSuccess) {
        setTimeout(() => onSuccess(response), 1500);
      }

      // Keep analysis visible - don't auto-clear
      // User can manually clear by uploading a new file

    } catch (error: any) {
      console.error('Upload error:', error);
      const errorDetail = error.response?.data?.detail || error.message || 'Failed to process XML file. Please check the file format.';
      setStatus('error');
      setMessage(errorDetail);
      toast.error(errorDetail);
    } finally {
      setUploading(false);
    }
  };

  return (
    <Card className="w-full">
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Watch className="w-5 h-5 text-purple-600" />
          Upload Apple Watch Data
        </CardTitle>
        <CardDescription>
          Export your health data from Apple Health as XML and upload it here
        </CardDescription>
      </CardHeader>
      <CardContent className="space-y-4">
        {/* Instructions */}
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 text-sm">
          <h4 className="font-semibold text-blue-900 mb-2">How to export from Apple Health:</h4>
          <ol className="list-decimal list-inside space-y-1 text-blue-800">
            <li>Open the Health app on your iPhone</li>
            <li>Tap your profile picture (top right)</li>
            <li>Scroll down and tap "Export All Health Data"</li>
            <li>Share the ZIP file to your computer</li>
            <li>Extract the ZIP and find "export.xml"</li>
            <li>Upload the XML file here</li>
          </ol>
        </div>

        {/* File Input */}
        <div className="space-y-3">
          <label
            htmlFor="xml-upload"
            className="flex flex-col items-center justify-center w-full h-32 border-2 border-dashed border-gray-300 rounded-lg cursor-pointer bg-gray-50 hover:bg-gray-100 transition-colors"
          >
            <div className="flex flex-col items-center justify-center pt-5 pb-6">
              {file ? (
                <>
                  <File className="w-10 h-10 text-green-600 mb-2" />
                  <p className="text-sm text-gray-700 font-medium">{file.name}</p>
                  <p className="text-xs text-gray-500">{(file.size / 1024 / 1024).toFixed(2)} MB</p>
                </>
              ) : (
                <>
                  <Upload className="w-10 h-10 text-gray-400 mb-2" />
                  <p className="text-sm text-gray-600">Click to select XML file</p>
                  <p className="text-xs text-gray-500 mt-1">or drag and drop</p>
                </>
              )}
            </div>
            <input
              id="xml-upload"
              type="file"
              accept=".xml"
              onChange={handleFileChange}
              className="hidden"
            />
          </label>

          {file && (
            <Button
              onClick={handleUpload}
              disabled={uploading}
              className="w-full"
            >
              {uploading ? (
                <>
                  <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                  Analyzing...
                </>
              ) : (
                <>
                  <Upload className="w-4 h-4 mr-2" />
                  Upload & Analyze Data
                </>
              )}
            </Button>
          )}
        </div>

        {/* Status Messages */}
        {status === 'success' && (
          <Alert className="bg-green-50 border-green-200">
            <Check className="h-4 w-4 text-green-600" />
            <AlertDescription className="text-green-700">
              {message}
              {stats && (
                <div className="mt-3 space-y-2">
                  {/* Extraction Stats */}
                  <div className="text-xs space-y-1 pb-2 border-b border-green-200">
                    <p className="font-semibold">Data Extracted:</p>
                    <p>• {stats.records_parsed?.toLocaleString() || 0} total records parsed</p>
                    <p>• {stats.days_processed || 0} days of health data saved</p>
                    {stats.date_range && (
                      <p className="text-green-600">
                        📅 {stats.date_range.start} to {stats.date_range.end}
                      </p>
                    )}
                  </div>
                  
                  {/* Latest Metrics */}
                  {stats.latest_metrics && Object.keys(stats.latest_metrics).some(k => stats.latest_metrics[k]) && (
                    <div className="text-xs space-y-1 pb-2 border-b border-green-200">
                      <p className="font-semibold">Latest Synced Metrics:</p>
                      {stats.latest_metrics.avg_heart_rate && (
                        <p className="flex items-center gap-1">
                          <Heart className="w-3 h-3" /> Heart Rate: {stats.latest_metrics.avg_heart_rate} bpm
                        </p>
                      )}
                      {stats.latest_metrics.steps && (
                        <p className="flex items-center gap-1">
                          <Activity className="w-3 h-3" /> Steps: {stats.latest_metrics.steps.toLocaleString()}
                        </p>
                      )}
                      {stats.latest_metrics.sleep_hours && (
                        <p>😴 Sleep: {stats.latest_metrics.sleep_hours} hours</p>
                      )}
                      {stats.latest_metrics.calories_burned && (
                        <p>🔥 Calories: {stats.latest_metrics.calories_burned} kcal</p>
                      )}
                      {stats.latest_metrics.hrv_ms && (
                        <p>💓 HRV: {stats.latest_metrics.hrv_ms} ms</p>
                      )}
                      {stats.latest_metrics.stress_level && (
                        <p>😌 Stress Level: {stats.latest_metrics.stress_level}/10</p>
                      )}
                    </div>
                  )}
                  
                  {/* Sync Timestamp */}
                  {uploadTimestamp && (
                    <div className="text-xs text-green-700 pt-2">
                      <p>🕒 Last synced: {uploadTimestamp}</p>
                      <p className="text-green-600 mt-1 font-medium">✨ Check "Your Health Analysis" section below for detailed insights</p>
                    </div>
                  )}
                </div>
              )}
            </AlertDescription>
          </Alert>
        )}

        {status === 'error' && (
          <Alert className="bg-red-50 border-red-200">
            <AlertCircle className="h-4 w-4 text-red-600" />
            <AlertDescription className="text-red-700">
              {message}
            </AlertDescription>
          </Alert>
        )}

        {uploading && (
          <Alert className="bg-blue-50 border-blue-200">
            <Loader2 className="h-4 w-4 text-blue-600 animate-spin" />
            <AlertDescription className="text-blue-700">
              {message}
            </AlertDescription>
          </Alert>
        )}
      </CardContent>
    </Card>
  );
}
