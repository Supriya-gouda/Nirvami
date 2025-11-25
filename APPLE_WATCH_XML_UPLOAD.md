# Apple Watch XML Upload Feature - Implementation Guide

## Overview
This feature enables users to upload their Apple Health export XML file to sync real smartwatch data with the Nirvami platform, replacing hardcoded test data with actual health metrics.

## Features Implemented

### 1. Frontend Component (`WatchDataUpload.tsx`)
- **File Upload Interface**: Drag-and-drop or click to select XML file
- **Upload Progress**: Loading state with spinner during processing
- **Status Alerts**: Success/error messages with detailed stats
- **User Instructions**: Step-by-step guide to export Apple Health data
- **Stats Display**: Shows records processed, snapshots created, days covered, anomalies detected

### 2. Backend Endpoint (`POST /api/v1/wearable/upload-xml`)
- **XML Parsing**: Extracts health metrics from Apple Health export format
- **Data Aggregation**: Groups records by date and calculates daily averages
- **Database Storage**: Saves snapshots to `wearable_snapshots` table
- **Background Analysis**: Triggers health anomaly detection after upload

### 3. Supported Health Metrics
| Metric | Apple Health Type | Aggregation |
|--------|------------------|-------------|
| Heart Rate | `HKQuantityTypeIdentifierHeartRate` | Average per day |
| Steps | `HKQuantityTypeIdentifierStepCount` | Sum per day |
| Sleep | `HKCategoryTypeIdentifierSleepAnalysis` | Total hours per day |
| Calories | `HKQuantityTypeIdentifierActiveEnergyBurned` | Sum per day |

## How to Use

### For Users:
1. Open iPhone Health app
2. Tap your profile picture (top right)
3. Scroll down and tap "Export All Health Data"
4. Share the generated ZIP file to your computer
5. Extract the ZIP and locate `export.xml`
6. Go to Nirvami Device Page → Apple Watch section
7. Drag and drop the XML file or click to browse
8. Click "Upload Health Data"
9. Wait for processing confirmation with stats

### For Developers:

#### Testing the Upload Endpoint
```bash
# Run the test script
cd backend/scripts
python test_xml_upload.py
```

This will:
1. Generate a sample Apple Health XML with 3 days of data
2. Prompt for authentication token (get from browser localStorage)
3. Upload the XML to the backend
4. Display processing results

#### Manual Testing with cURL
```bash
curl -X POST "http://localhost:8000/api/v1/wearable/upload-xml" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -F "file=@export.xml"
```

#### Expected Response
```json
{
  "message": "Apple Health data uploaded successfully",
  "records_count": 245,
  "snapshots_created": 7,
  "days_processed": 7,
  "date_range": {
    "start": "2025-11-17",
    "end": "2025-11-24"
  }
}
```

## Implementation Details

### XML Parsing Logic
```python
# Parse Apple Health records
records_by_date = defaultdict(lambda: {
    'heart_rates': [],
    'steps': [],
    'sleep_minutes': [],
    'calories': []
})

for record in root.findall('.//Record'):
    record_type = record.get('type')
    value = record.get('value')
    date = record.get('startDate').split(' ')[0]
    
    if 'HeartRate' in record_type:
        records_by_date[date]['heart_rates'].append(float(value))
    # ... (similar for other metrics)
```

### Daily Aggregation
```python
# Calculate averages/totals per day
avg_heart_rate = sum(hr_list) / len(hr_list)
total_steps = sum(steps_list)
sleep_hours = sum(sleep_minutes_list) / 60
```

### Database Schema
```sql
-- wearable_snapshots table
CREATE TABLE wearable_snapshots (
    id UUID PRIMARY KEY,
    user_id UUID REFERENCES users(id),
    provider TEXT,
    captured_at TIMESTAMPTZ,
    heart_rate INTEGER,
    steps INTEGER,
    sleep_hours NUMERIC,
    calories_burned INTEGER,
    created_at TIMESTAMPTZ DEFAULT NOW()
);
```

## Integration Points

### 1. Frontend Integration
```tsx
// DevicePage.tsx
import { WatchDataUpload } from './WatchDataUpload';

<WatchDataUpload onSuccess={fetchLatestData} />
```

### 2. API Service
```typescript
// api.ts
async uploadWatchXML(formData: FormData): Promise<any> {
  const response = await this.api.post('/wearable/upload-xml', formData, {
    headers: { 'Content-Type': 'multipart/form-data' }
  });
  return response.data;
}
```

### 3. Backend Route
```python
# wearable.py
@router.post("/upload-xml")
async def upload_wearable_xml(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    current_user_id: str = Depends(get_current_user_id)
):
    # Parse XML, aggregate data, save snapshots, trigger analysis
```

## Health Anomaly Detection

After XML upload, the system automatically:
1. Analyzes each snapshot for health anomalies
2. Creates in-app notifications for detected issues
3. Sends SMS alerts (if enabled) for critical values

### Thresholds
- **High Heart Rate**: ≥100 bpm (medium), ≥120 bpm (critical)
- **Low Sleep**: <5 hours (high), <4 hours (critical)
- **High Stress**: ≥8/10 (medium)

## Error Handling

### Frontend
```typescript
// Invalid file type
if (!file.name.endsWith('.xml')) {
  setStatus('error');
  setMessage('Please select an XML file');
  return;
}
```

### Backend
```python
# Validation errors
if not file.filename.endswith('.xml'):
    raise HTTPException(status_code=400, detail="File must be an XML file")

# Parsing errors
try:
    root = ET.fromstring(content)
except ET.ParseError as e:
    raise HTTPException(status_code=400, detail=f"Invalid XML: {e}")
```

## Future Enhancements

### Planned Features
1. **Incremental Uploads**: Only process new records since last upload
2. **Real-time Sync**: Direct Apple Watch → Nirvami sync without XML export
3. **Additional Metrics**: 
   - Blood pressure (HKQuantityTypeIdentifierBloodPressure)
   - Respiratory rate (HKQuantityTypeIdentifierRespiratoryRate)
   - Blood oxygen (HKQuantityTypeIdentifierOxygenSaturation)
4. **Emotion Detection**: Auto-generate emotion logs based on health patterns
5. **Recommendations**: AI-powered yoga poses and meal suggestions based on metrics

### Technical Improvements
1. Stream large XML files instead of loading into memory
2. Use multiprocessing for faster XML parsing
3. Add progress websocket for real-time upload status
4. Implement XML schema validation before processing

## Troubleshooting

### Issue: Upload fails with "Invalid XML format"
**Solution**: Ensure the file is the actual `export.xml` from Apple Health, not a different XML file.

### Issue: No snapshots created
**Solution**: Check that the XML contains supported record types (HeartRate, StepCount, SleepAnalysis, ActiveEnergyBurned).

### Issue: Missing data for certain days
**Solution**: Apple Health may not have recorded data on those days. Check the source iPhone/Apple Watch for gaps.

### Issue: Anomaly detection not triggering
**Solution**: Verify `WearableHealthAnalyzer` is properly configured and background tasks are running.

## Files Modified

### Frontend
- `src/components/WatchDataUpload.tsx` - New component
- `src/components/DevicePage.tsx` - Integrated upload component
- `src/services/api.ts` - Added `uploadWatchXML()` method

### Backend
- `backend/app/api/routes/wearable.py` - Added `/upload-xml` endpoint
- Added XML parsing logic with `xml.etree.ElementTree`
- Integrated background health analysis

### Testing
- `backend/scripts/test_xml_upload.py` - Automated test script

## API Reference

### POST /api/v1/wearable/upload-xml

**Authentication**: Required (Bearer token)

**Request**:
- Content-Type: `multipart/form-data`
- Body: `file` (XML file from Apple Health export)

**Response**:
```json
{
  "message": "Apple Health data uploaded successfully",
  "records_count": 1500,
  "snapshots_created": 30,
  "days_processed": 30,
  "date_range": {
    "start": "2025-10-25",
    "end": "2025-11-24"
  }
}
```

**Error Codes**:
- `400`: Invalid file format or malformed XML
- `401`: Authentication required
- `500`: Server error during processing

## Performance Considerations

### Memory Usage
- Large XML files (>10MB) are loaded entirely into memory
- Recommendation: Process XML in chunks for files >50MB

### Processing Time
- ~1-2 seconds per 1000 records
- Background tasks run asynchronously (non-blocking)

### Database Impact
- Batch inserts for snapshots (one per day)
- Daily stats aggregation runs in background
- Minimal impact on user experience

## Security

### File Validation
- Only `.xml` files accepted
- XML content validated before processing
- User can only upload to their own account (auth check)

### Data Privacy
- Health data stored securely in Supabase
- Row-level security enforced
- No data shared across users

## Conclusion

This implementation provides a complete Apple Watch integration via XML upload, enabling users to sync their real health data with the Nirvami platform. The system handles parsing, validation, storage, aggregation, and anomaly detection automatically.
