"""
Apple Health XML Parser - Complete extraction and normalization.

Parses raw HealthKit XML records and converts them to normalized snapshots
that match the wearable_snapshots schema used by manual input.
"""
import logging
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from collections import defaultdict

logger = logging.getLogger(__name__)


class AppleHealthXMLParser:
    """Parse Apple Health XML export and extract health metrics."""
    
    # HealthKit type identifiers
    TYPE_HEART_RATE = "HKQuantityTypeIdentifierHeartRate"
    TYPE_STEPS = "HKQuantityTypeIdentifierStepCount"
    TYPE_SLEEP = "HKCategoryTypeIdentifierSleepAnalysis"
    TYPE_CALORIES = "HKQuantityTypeIdentifierActiveEnergyBurned"
    TYPE_HRV = "HKQuantityTypeIdentifierHeartRateVariabilitySDNN"
    
    # Sleep analysis values (HealthKit categories)
    SLEEP_ASLEEP = ["0", "1", "2"]  # InBed=0, Asleep=1, Awake=2, Core=3, Deep=4, REM=5
    
    @staticmethod
    def parse_xml(xml_content: str) -> Dict[str, Any]:
        """
        Parse Apple Health XML and extract all health metrics.
        
        Args:
            xml_content: Raw XML string from export.xml
            
        Returns:
            {
                "success": bool,
                "daily_snapshots": [{"date": "2025-11-25", "metrics": {...}}],
                "raw_records": {
                    "heart_rate": [...],
                    "steps": [...],
                    "sleep": [...],
                    "calories": [...],
                    "hrv": [...]
                },
                "stats": {...}
            }
        """
        try:
            logger.info("🔍 Starting XML parsing...")
            
            # Parse XML
            root = ET.fromstring(xml_content)
            
            # Extract raw records by type
            raw_records = {
                "heart_rate": AppleHealthXMLParser._extract_heart_rate(root),
                "steps": AppleHealthXMLParser._extract_steps(root),
                "sleep": AppleHealthXMLParser._extract_sleep(root),
                "calories": AppleHealthXMLParser._extract_calories(root),
                "hrv": AppleHealthXMLParser._extract_hrv(root)
            }
            
            # Aggregate by day
            daily_snapshots = AppleHealthXMLParser._aggregate_daily_snapshots(raw_records)
            
            # Calculate stats
            total_records = sum(len(records) for records in raw_records.values())
            days_with_data = len(daily_snapshots)
            
            stats = {
                "total_records": total_records,
                "days_with_data": days_with_data,
                "heart_rate_records": len(raw_records["heart_rate"]),
                "step_records": len(raw_records["steps"]),
                "sleep_records": len(raw_records["sleep"]),
                "calorie_records": len(raw_records["calories"]),
                "hrv_records": len(raw_records["hrv"])
            }
            
            logger.info(f"✅ Parsed {total_records} records across {days_with_data} days")
            
            return {
                "success": True,
                "daily_snapshots": daily_snapshots,
                "raw_records": raw_records,
                "stats": stats
            }
            
        except ET.ParseError as e:
            logger.error(f"❌ XML parse error: {e}")
            return {
                "success": False,
                "error": f"Invalid XML format: {str(e)}",
                "daily_snapshots": [],
                "raw_records": {},
                "stats": {}
            }
        except Exception as e:
            logger.error(f"❌ Parsing error: {e}", exc_info=True)
            return {
                "success": False,
                "error": str(e),
                "daily_snapshots": [],
                "raw_records": {},
                "stats": {}
            }
    
    @staticmethod
    def _extract_heart_rate(root: ET.Element) -> List[Dict]:
        """Extract heart rate records."""
        records = []
        
        for record in root.findall(f".//Record[@type='{AppleHealthXMLParser.TYPE_HEART_RATE}']"):
            try:
                value = float(record.get('value', 0))
                start_date = record.get('startDate', '')
                
                # Validate heart rate (30-220 bpm)
                if not (30 <= value <= 220):
                    continue
                
                # Parse timestamp
                timestamp = AppleHealthXMLParser._parse_date(start_date)
                if not timestamp:
                    continue
                
                records.append({
                    "value": value,
                    "timestamp": timestamp,
                    "date": timestamp.date().isoformat(),
                    "source": record.get('sourceName', 'Apple Watch')
                })
                
            except (ValueError, TypeError):
                continue
        
        logger.info(f"📊 Extracted {len(records)} heart rate records")
        return records
    
    @staticmethod
    def _extract_steps(root: ET.Element) -> List[Dict]:
        """Extract step count records."""
        records = []
        
        for record in root.findall(f".//Record[@type='{AppleHealthXMLParser.TYPE_STEPS}']"):
            try:
                value = float(record.get('value', 0))
                start_date = record.get('startDate', '')
                
                if value < 0:
                    continue
                
                timestamp = AppleHealthXMLParser._parse_date(start_date)
                if not timestamp:
                    continue
                
                records.append({
                    "value": value,
                    "timestamp": timestamp,
                    "date": timestamp.date().isoformat(),
                    "source": record.get('sourceName', 'iPhone')
                })
                
            except (ValueError, TypeError):
                continue
        
        logger.info(f"👟 Extracted {len(records)} step records")
        return records
    
    @staticmethod
    def _extract_sleep(root: ET.Element) -> List[Dict]:
        """
        Extract sleep analysis records.
        
        HealthKit provides sleep segments (not total hours).
        Must calculate duration from startDate/endDate.
        """
        records = []
        
        for record in root.findall(f".//Record[@type='{AppleHealthXMLParser.TYPE_SLEEP}']"):
            try:
                # Sleep category value (0=InBed, 1=Asleep, etc.)
                sleep_value = record.get('value', '0')
                
                # Only count actual sleep segments
                if sleep_value not in AppleHealthXMLParser.SLEEP_ASLEEP:
                    continue
                
                start_date = record.get('startDate', '')
                end_date = record.get('endDate', '')
                
                start_time = AppleHealthXMLParser._parse_date(start_date)
                end_time = AppleHealthXMLParser._parse_date(end_date)
                
                if not start_time or not end_time:
                    continue
                
                # Calculate sleep duration in hours
                duration = (end_time - start_time).total_seconds() / 3600
                
                if duration < 0 or duration > 24:  # Sanity check
                    continue
                
                # Use end_date to group sleep (sleep ending in morning belongs to that day)
                records.append({
                    "duration_hours": duration,
                    "start": start_time,
                    "end": end_time,
                    "date": end_time.date().isoformat(),
                    "category": sleep_value,
                    "source": record.get('sourceName', 'Apple Watch')
                })
                
            except (ValueError, TypeError):
                continue
        
        logger.info(f"😴 Extracted {len(records)} sleep segments")
        return records
    
    @staticmethod
    def _extract_calories(root: ET.Element) -> List[Dict]:
        """Extract active calories burned."""
        records = []
        
        for record in root.findall(f".//Record[@type='{AppleHealthXMLParser.TYPE_CALORIES}']"):
            try:
                value = float(record.get('value', 0))
                start_date = record.get('startDate', '')
                
                if value < 0:
                    continue
                
                timestamp = AppleHealthXMLParser._parse_date(start_date)
                if not timestamp:
                    continue
                
                records.append({
                    "value": value,
                    "timestamp": timestamp,
                    "date": timestamp.date().isoformat(),
                    "source": record.get('sourceName', 'Apple Watch')
                })
                
            except (ValueError, TypeError):
                continue
        
        logger.info(f"🔥 Extracted {len(records)} calorie records")
        return records
    
    @staticmethod
    def _extract_hrv(root: ET.Element) -> List[Dict]:
        """Extract Heart Rate Variability (HRV) records."""
        records = []
        
        for record in root.findall(f".//Record[@type='{AppleHealthXMLParser.TYPE_HRV}']"):
            try:
                value = float(record.get('value', 0))
                start_date = record.get('startDate', '')
                
                # HRV validation (typically 20-100ms)
                if not (10 <= value <= 200):
                    continue
                
                timestamp = AppleHealthXMLParser._parse_date(start_date)
                if not timestamp:
                    continue
                
                records.append({
                    "value": value,
                    "timestamp": timestamp,
                    "date": timestamp.date().isoformat(),
                    "source": record.get('sourceName', 'Apple Watch')
                })
                
            except (ValueError, TypeError):
                continue
        
        logger.info(f"💓 Extracted {len(records)} HRV records")
        return records
    
    @staticmethod
    def _aggregate_daily_snapshots(raw_records: Dict[str, List]) -> List[Dict]:
        """
        Aggregate raw time-series records into daily snapshots.
        
        This is the KEY difference from manual input:
        - Manual: user enters one value per metric
        - XML: hundreds of records that must be aggregated
        
        Returns list of daily snapshots matching wearable_snapshots schema.
        """
        daily_data = defaultdict(lambda: {
            "heart_rates": [],
            "steps": [],
            "sleep_hours": [],
            "calories": [],
            "hrv_values": []
        })
        
        # Group heart rate by date
        for hr in raw_records.get("heart_rate", []):
            daily_data[hr["date"]]["heart_rates"].append(hr["value"])
        
        # Group steps by date
        for step in raw_records.get("steps", []):
            daily_data[step["date"]]["steps"].append(step["value"])
        
        # Group sleep by date
        for sleep in raw_records.get("sleep", []):
            daily_data[sleep["date"]]["sleep_hours"].append(sleep["duration_hours"])
        
        # Group calories by date
        for cal in raw_records.get("calories", []):
            daily_data[cal["date"]]["calories"].append(cal["value"])
        
        # Group HRV by date
        for hrv in raw_records.get("hrv", []):
            daily_data[hrv["date"]]["hrv_values"].append(hrv["value"])
        
        # Compute daily aggregates
        snapshots = []
        
        for date_str, metrics in sorted(daily_data.items()):
            snapshot = {
                "date": date_str,
                "source": "watch"
            }
            
            # Average heart rate
            if metrics["heart_rates"]:
                snapshot["avg_heart_rate"] = int(sum(metrics["heart_rates"]) / len(metrics["heart_rates"]))
            
            # Total steps
            if metrics["steps"]:
                snapshot["steps"] = int(sum(metrics["steps"]))
            
            # Total sleep hours
            if metrics["sleep_hours"]:
                snapshot["sleep_hours"] = round(sum(metrics["sleep_hours"]), 1)
            
            # Total calories
            if metrics["calories"]:
                snapshot["calories_burned"] = round(sum(metrics["calories"]), 1)
            
            # Average HRV
            if metrics["hrv_values"]:
                snapshot["hrv_ms"] = int(sum(metrics["hrv_values"]) / len(metrics["hrv_values"]))
            
            # Infer stress level from physiological markers
            snapshot["stress_level"] = AppleHealthXMLParser._infer_stress_level(snapshot)
            
            snapshots.append(snapshot)
        
        logger.info(f"📅 Aggregated {len(snapshots)} daily snapshots")
        return snapshots
    
    @staticmethod
    def _infer_stress_level(snapshot: Dict) -> Optional[int]:
        """
        Infer stress level (1-10) from physiological markers.
        
        High stress indicators:
        - High heart rate (>90 bpm)
        - Low HRV (<30 ms)
        - Low sleep (<6 hours)
        """
        stress_score = 5  # Neutral baseline
        
        hr = snapshot.get("avg_heart_rate")
        hrv = snapshot.get("hrv_ms")
        sleep = snapshot.get("sleep_hours")
        
        # High heart rate increases stress
        if hr:
            if hr > 90:
                stress_score += 2
            elif hr > 80:
                stress_score += 1
        
        # Low HRV increases stress
        if hrv:
            if hrv < 30:
                stress_score += 2
            elif hrv < 50:
                stress_score += 1
        
        # Low sleep increases stress
        if sleep:
            if sleep < 5:
                stress_score += 2
            elif sleep < 6:
                stress_score += 1
        
        # Cap at 10
        return min(stress_score, 10)
    
    @staticmethod
    def _parse_date(date_str: str) -> Optional[datetime]:
        """
        Parse HealthKit date format.
        
        Format: "2025-11-25 10:30:00 +0000"
        """
        if not date_str:
            return None
        
        try:
            # Remove timezone for simplicity
            date_part = date_str.split('+')[0].split('-', 3)[-1].strip()
            return datetime.strptime(date_part, '%m-%d %H:%M:%S')
        except:
            try:
                # Alternative format
                return datetime.strptime(date_str[:19], '%Y-%m-%d %H:%M:%S')
            except:
                return None
