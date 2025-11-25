import logging
from datetime import date, datetime
from typing import Dict, Any
from app.utils.database import get_supabase

logger = logging.getLogger(__name__)

class WatchService:
    """Service for handling Apple Watch data integration."""

    @staticmethod
    def store_watch_data(user_id: str, data: Dict[str, Any]) -> Dict:
        """Validate and store Apple Watch data as a wearable snapshot.

        Expected data keys: timestamp (ISO string), heart_rate, hrv, sleep_hours, steps, activity_type.
        """
        required_keys = {"timestamp", "heart_rate", "hrv", "sleep_hours", "steps", "activity_type"}
        missing = required_keys - data.keys()
        if missing:
            raise ValueError(f"Missing required watch data fields: {missing}")

        supabase = get_supabase()
        snapshot_entry = {
            "user_id": user_id,
            "recorded_at": data["timestamp"],
            "device_type": "apple_watch",
            "heart_rate": data["heart_rate"],
            "hrv": data["hrv"],
            "sleep_hours": data["sleep_hours"],
            "steps": data["steps"],
            "raw_data": data,
        }
        try:
            result = supabase.table("wearable_snapshots").upsert(snapshot_entry).execute()
            logger.info(f"Stored wearable snapshot for user {user_id}")
            return result.data[0] if result.data else snapshot_entry
        except Exception as e:
            logger.error(f"Error storing wearable snapshot: {e}")
            raise

    @staticmethod
    def get_today_watch_data(user_id: str) -> Dict:
        """Fetch the most recent wearable snapshot for today for the user. Returns empty dict if none found."""
        supabase = get_supabase()
        today_str = date.today().isoformat()
        try:
            result = (
                supabase.table("wearable_snapshots")
                .select("*")
                .eq("user_id", user_id)
                .gte("recorded_at", today_str)
                .lte("recorded_at", f"{today_str}T23:59:59Z")
                .order("recorded_at", desc=True)
                .limit(1)
                .execute()
            )
            if result.data and len(result.data) > 0:
                return result.data[0]
            return {}
        except Exception as e:
            logger.error(f"Error fetching today wearable snapshot: {e}")
            return {}
