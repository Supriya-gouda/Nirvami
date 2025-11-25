"""Apple Health XML Parser - Extract and convert health data."""
import xml.etree.ElementTree as ET
from datetime import datetime
from collections import defaultdict
from typing import Dict, List, Optional
import logging

logger = logging.getLogger(__name__)


class AppleHealthParser:
    """Parse Apple Health export.xml and extract health metrics."""
    
    # Apple Health record type identifiers
    HEART_RATE_TYPES = [
        'HKQuantityTypeIdentifierHeartRate',
        'HeartRate',
        'heart_rate'
    ]
    
    STEP_COUNT_TYPES = [
        'HKQuantityTypeIdentifierStepCount',
        'StepCount',
        'step_count'
    ]
    
    SLEEP_TYPES = [
        'HKCategoryTypeIdentifierSleepAnalysis',
        'SleepAnalysis',
        'sleep'
    ]
    
    ACTIVE_ENERGY_TYPES = [
        'HKQuantityTypeIdentifierActiveEnergyBurned',
        'ActiveEnergyBurned',
        'active_energy'
    ]
    
    @staticmethod
    def parse_xml_file(xml_content: str) -> Dict:
        """
        Parse Apple Health XML and extract health records.
        
        Args:
            xml_content: String content of the export.xml file
            
        Returns:
            Dictionary with parsed data and statistics
        """
        try:
            # Parse XML
            root = ET.fromstring(xml_content)
            logger.info(f"Parsing XML with root tag: {root.tag}")
            
            # Validate root element
            if root.tag != 'HealthData':
                raise ValueError(f"Invalid Apple Health export. Expected 'HealthData', got '{root.tag}'")
            
            # Find all Record elements
            all_records = root.findall('.//Record')
            logger.info(f"Found {len(all_records)} total Record elements")
            
            # Extract all unique record types for debugging
            all_types = set()
            for record in all_records[:100]:  # Sample first 100
                record_type = record.get('type', '')
                if record_type:
                    all_types.add(record_type)
            
            logger.info(f"Sample record types: {list(all_types)[:10]}")
            
            # Parse records by date
            daily_data = AppleHealthParser._extract_daily_metrics(all_records)
            
            # Calculate statistics
            stats = {
                'total_records': len(all_records),
                'days_with_data': len(daily_data),
                'unique_types': len(all_types),
                'sample_types': list(all_types)[:20]
            }
            
            logger.info(f"Extracted data for {len(daily_data)} days")
            
            return {
                'success': True,
                'daily_data': daily_data,
                'stats': stats
            }
            
        except ET.ParseError as e:
            logger.error(f"XML parsing error: {e}")
            return {
                'success': False,
                'error': f"Invalid XML format: {str(e)}",
                'daily_data': {},
                'stats': {}
            }
        except Exception as e:
            logger.error(f"Error parsing Apple Health XML: {e}", exc_info=True)
            return {
                'success': False,
                'error': str(e),
                'daily_data': {},
                'stats': {}
            }
    
    @staticmethod
    def _extract_daily_metrics(records: List) -> Dict[str, Dict]:
        """
        Extract and aggregate health metrics by day.
        
        Args:
            records: List of Record XML elements
            
        Returns:
            Dictionary mapping date strings to aggregated metrics
        """
        daily_metrics = defaultdict(lambda: {
            'heart_rates': [],
            'steps': [],
            'sleep_minutes': [],
            'calories': []
        })
        
        processed = 0
        skipped = 0
        
        for record in records:
            try:
                record_type = record.get('type', '')
                start_date = record.get('startDate', '')
                end_date = record.get('endDate', '')
                value = record.get('value', '')
                unit = record.get('unit', '')
                
                # Skip if no date
                if not start_date:
                    skipped += 1
                    continue
                
                # Extract date (format: 2025-11-24 07:30:00 -0800)
                date_str = start_date.split(' ')[0]
                
                # Heart Rate
                if AppleHealthParser._matches_type(record_type, AppleHealthParser.HEART_RATE_TYPES):
                    if value:
                        try:
                            hr = float(value)
                            daily_metrics[date_str]['heart_rates'].append(hr)
                            processed += 1
                        except ValueError:
                            pass
                
                # Step Count
                elif AppleHealthParser._matches_type(record_type, AppleHealthParser.STEP_COUNT_TYPES):
                    if value:
                        try:
                            steps = int(float(value))
                            daily_metrics[date_str]['steps'].append(steps)
                            processed += 1
                        except ValueError:
                            pass
                
                # Sleep Analysis
                elif AppleHealthParser._matches_type(record_type, AppleHealthParser.SLEEP_TYPES):
                    if start_date and end_date:
                        try:
                            duration_mins = AppleHealthParser._calculate_duration(start_date, end_date)
                            if duration_mins > 0:
                                daily_metrics[date_str]['sleep_minutes'].append(duration_mins)
                                processed += 1
                        except Exception:
                            pass
                
                # Active Energy
                elif AppleHealthParser._matches_type(record_type, AppleHealthParser.ACTIVE_ENERGY_TYPES):
                    if value:
                        try:
                            calories = float(value)
                            daily_metrics[date_str]['calories'].append(calories)
                            processed += 1
                        except ValueError:
                            pass
            
            except Exception as e:
                logger.debug(f"Error processing record: {e}")
                skipped += 1
                continue
        
        logger.info(f"Processed {processed} health records, skipped {skipped}")
        
        # Convert to regular dict and aggregate
        result = {}
        for date_str, metrics in daily_metrics.items():
            aggregated = AppleHealthParser._aggregate_metrics(metrics)
            if aggregated:  # Only include days with actual data
                result[date_str] = aggregated
        
        return result
    
    @staticmethod
    def _matches_type(record_type: str, type_list: List[str]) -> bool:
        """Check if record type matches any type in the list."""
        record_type_lower = record_type.lower()
        for type_name in type_list:
            if type_name.lower() in record_type_lower:
                return True
        return False
    
    @staticmethod
    def _calculate_duration(start_date: str, end_date: str) -> float:
        """Calculate duration in minutes between start and end dates."""
        try:
            # Remove timezone (format: 2025-11-24 07:30:00 -0800)
            start_clean = ' '.join(start_date.split(' ')[:2])
            end_clean = ' '.join(end_date.split(' ')[:2])
            
            start_dt = datetime.strptime(start_clean, '%Y-%m-%d %H:%M:%S')
            end_dt = datetime.strptime(end_clean, '%Y-%m-%d %H:%M:%S')
            
            duration = (end_dt - start_dt).total_seconds() / 60
            return duration
        except Exception as e:
            logger.debug(f"Error calculating duration: {e}")
            return 0
    
    @staticmethod
    def _aggregate_metrics(metrics: Dict[str, List]) -> Optional[Dict]:
        """
        Aggregate raw metrics into daily summary.
        
        Returns:
            Dictionary with aggregated metrics or None if no data
        """
        result = {}
        
        # Heart rate - average
        if metrics['heart_rates']:
            result['avg_heart_rate'] = round(sum(metrics['heart_rates']) / len(metrics['heart_rates']), 1)
            result['min_heart_rate'] = round(min(metrics['heart_rates']), 1)
            result['max_heart_rate'] = round(max(metrics['heart_rates']), 1)
        
        # Steps - total
        if metrics['steps']:
            result['total_steps'] = sum(metrics['steps'])
        
        # Sleep - total hours
        if metrics['sleep_minutes']:
            result['sleep_hours'] = round(sum(metrics['sleep_minutes']) / 60, 1)
        
        # Calories - total
        if metrics['calories']:
            result['total_calories'] = round(sum(metrics['calories']), 0)
        
        return result if result else None
    
    @staticmethod
    def convert_to_snapshots(daily_data: Dict[str, Dict], user_id: str) -> List[Dict]:
        """
        Convert parsed daily data to wearable snapshot format.
        
        Args:
            daily_data: Dictionary of daily aggregated metrics
            user_id: User ID for the snapshots
            
        Returns:
            List of snapshot dictionaries ready for database insertion
        """
        snapshots = []
        
        for date_str, metrics in daily_data.items():
            timestamp = f"{date_str}T12:00:00Z"  # Use noon as default time
            snapshot = {
                'user_id': user_id,
                'provider': 'apple_watch',
                'captured_at': timestamp,
                'recorded_at': timestamp,  # Required field for backward compatibility
                'source': 'watch'
            }
            
            # Add metrics if present
            if 'avg_heart_rate' in metrics:
                snapshot['heart_rate'] = int(metrics['avg_heart_rate'])
            
            if 'total_steps' in metrics:
                snapshot['steps'] = metrics['total_steps']
            
            if 'sleep_hours' in metrics:
                snapshot['sleep_hours'] = metrics['sleep_hours']
            
            if 'total_calories' in metrics:
                snapshot['calories_burned'] = int(metrics['total_calories'])
            
            # Only add snapshots that have at least one metric
            if len(snapshot) > 4:  # More than just user_id, provider, captured_at, source
                snapshots.append(snapshot)
        
        logger.info(f"Converted {len(snapshots)} daily records to snapshots")
        return snapshots
