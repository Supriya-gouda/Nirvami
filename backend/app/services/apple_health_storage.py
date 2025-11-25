"""Storage service for Apple Health data."""
from typing import List, Dict, Optional
from datetime import date, datetime
import logging
from app.utils.database import get_supabase

logger = logging.getLogger(__name__)


class AppleHealthStorage:
    """Handle storage of Apple Health data in database."""
    
    @staticmethod
    def save_snapshots(snapshots: List[Dict]) -> Dict:
        """
        Save wearable snapshots to database.
        Uses upsert logic to handle duplicates.
        
        Args:
            snapshots: List of snapshot dictionaries
            
        Returns:
            Dictionary with save results and statistics
        """
        if not snapshots:
            return {
                'success': False,
                'message': 'No snapshots to save',
                'saved_count': 0,
                'failed_count': 0
            }
        
        supabase = get_supabase()
        saved_count = 0
        failed_count = 0
        errors = []
        
        # Validate user exists using service role (bypasses RLS)
        user_ids = set(s['user_id'] for s in snapshots)
        admin_client = get_supabase(use_service_role=True)
        
        for user_id in user_ids:
            try:
                # Use service role to check if user exists
                user_check = admin_client.table('profiles').select('id,email').eq('id', user_id).execute()
                
                if not user_check.data:
                    error_msg = f"User {user_id} does not exist in profiles table"
                    logger.error(error_msg)
                    return {
                        'success': False,
                        'message': "User profile not found. Please contact support.",
                        'saved_count': 0,
                        'failed_count': len(snapshots),
                        'errors': [error_msg]
                    }
                else:
                    logger.info(f"✅ User validated: {user_id} ({user_check.data[0].get('email')})")
                    
            except Exception as e:
                error_msg = f"Error validating user {user_id}: {str(e)}"
                logger.error(error_msg)
                return {
                    'success': False,
                    'message': "Could not validate user profile",
                    'saved_count': 0,
                    'failed_count': len(snapshots),
                    'errors': [error_msg]
                }
        
        # First, try to delete existing snapshots for the same user and dates to avoid duplicates
        dates_to_clear = set()
        
        for snapshot in snapshots:
            # Extract date from captured_at (format: 2025-11-24T12:00:00Z)
            captured_at = snapshot.get('captured_at', '')
            if 'T' in captured_at:
                date_part = captured_at.split('T')[0]
                dates_to_clear.add(date_part)
        
        # Delete existing snapshots for these dates
        for user_id in user_ids:
            for date_str in dates_to_clear:
                try:
                    delete_result = supabase.table('wearable_snapshots').delete().eq(
                        'user_id', user_id
                    ).gte(
                        'captured_at', f"{date_str}T00:00:00Z"
                    ).lte(
                        'captured_at', f"{date_str}T23:59:59Z"
                    ).eq(
                        'source', 'watch'  # Only delete watch data, not manual entries
                    ).execute()
                    logger.info(f"Cleared existing watch data for user {user_id} on {date_str}")
                except Exception as e:
                    logger.warning(f"Could not clear existing data for {date_str}: {e}")
        
        # Now insert new snapshots
        for snapshot in snapshots:
            try:
                # Insert into wearable_snapshots table
                result = supabase.table('wearable_snapshots').insert(snapshot).execute()
                
                if result.data:
                    saved_count += 1
                    logger.info(f"✅ Saved snapshot for {snapshot.get('captured_at')}")
                else:
                    failed_count += 1
                    error_msg = f"No data returned for snapshot {snapshot.get('captured_at')}"
                    logger.error(error_msg)
                    errors.append(error_msg)
                    
            except Exception as e:
                failed_count += 1
                error_msg = f"DB Error for {snapshot.get('captured_at')}: {type(e).__name__}: {str(e)}"
                logger.error(error_msg, exc_info=True)
                logger.error(f"Failed snapshot data: {snapshot}")
                errors.append(error_msg)
        
        logger.info(f"Saved {saved_count}/{len(snapshots)} snapshots to database")
        
        return {
            'success': saved_count > 0,
            'message': f'Saved {saved_count} snapshots, {failed_count} failed',
            'saved_count': saved_count,
            'failed_count': failed_count,
            'errors': errors[:5]  # Return first 5 errors
        }
    
    @staticmethod
    def aggregate_daily_stats(user_id: str, dates: List[str]) -> Dict:
        """
        Aggregate daily statistics for given dates.
        
        Args:
            user_id: User ID
            dates: List of date strings (YYYY-MM-DD format)
            
        Returns:
            Dictionary with aggregation results
        """
        supabase = get_supabase()
        aggregated_count = 0
        failed_count = 0
        
        for date_str in dates:
            try:
                # Convert string to date object
                target_date = date.fromisoformat(date_str)
                
                # Get all snapshots for this date
                result = supabase.table('wearable_snapshots').select('*').eq(
                    'user_id', user_id
                ).gte(
                    'captured_at', f"{date_str}T00:00:00Z"
                ).lte(
                    'captured_at', f"{date_str}T23:59:59Z"
                ).execute()
                
                if not result.data or len(result.data) == 0:
                    logger.debug(f"No snapshots found for {date_str}")
                    continue
                
                # Calculate aggregated metrics
                snapshots = result.data
                
                heart_rates = [s['heart_rate'] for s in snapshots if s.get('heart_rate')]
                steps = [s['steps'] for s in snapshots if s.get('steps')]
                sleep_hours = [s['sleep_hours'] for s in snapshots if s.get('sleep_hours')]
                calories = [s['calories_burned'] for s in snapshots if s.get('calories_burned')]
                hrv_values = [s['hrv_ms'] for s in snapshots if s.get('hrv_ms')]
                stress_values = [s['stress_level'] for s in snapshots if s.get('stress_level')]
                
                # Build daily stats record
                daily_stats = {
                    'user_id': user_id,
                    'date': date_str,
                    'data_source': 'watch'
                }
                
                if heart_rates:
                    daily_stats['avg_heart_rate'] = round(sum(heart_rates) / len(heart_rates), 1)
                
                if steps:
                    daily_stats['total_steps'] = sum(steps)
                
                if sleep_hours:
                    daily_stats['sleep_hours'] = round(sum(sleep_hours), 1)
                
                if calories:
                    daily_stats['total_calories_burned'] = round(sum(calories), 0)
                
                if hrv_values:
                    daily_stats['avg_hrv_ms'] = round(sum(hrv_values) / len(hrv_values), 1)
                
                if stress_values:
                    daily_stats['avg_stress_level'] = round(sum(stress_values) / len(stress_values), 1)
                
                # Check if daily stats already exist
                existing = supabase.table('wearable_daily_stats').select('id').eq(
                    'user_id', user_id
                ).eq(
                    'date', date_str
                ).execute()
                
                if existing.data and len(existing.data) > 0:
                    # Update existing record
                    update_result = supabase.table('wearable_daily_stats').update(
                        daily_stats
                    ).eq(
                        'id', existing.data[0]['id']
                    ).execute()
                    
                    if update_result.data:
                        aggregated_count += 1
                        logger.info(f"✅ Updated daily stats for {date_str}")
                else:
                    # Insert new record
                    insert_result = supabase.table('wearable_daily_stats').insert(
                        daily_stats
                    ).execute()
                    
                    if insert_result.data:
                        aggregated_count += 1
                        logger.info(f"✅ Created daily stats for {date_str}")
                        
            except Exception as e:
                failed_count += 1
                logger.error(f"❌ Failed to aggregate stats for {date_str}: {e}", exc_info=True)
        
        return {
            'success': aggregated_count > 0,
            'aggregated_count': aggregated_count,
            'failed_count': failed_count
        }
    
    @staticmethod
    def get_latest_summary(user_id: str) -> Optional[Dict]:
        """
        Get the latest wearable data summary for a user.
        
        Args:
            user_id: User ID
            
        Returns:
            Dictionary with latest health metrics or None
        """
        supabase = get_supabase()
        
        try:
            # Get most recent daily stats
            result = supabase.table('wearable_daily_stats').select('*').eq(
                'user_id', user_id
            ).order('date', desc=True).limit(1).execute()
            
            if not result.data or len(result.data) == 0:
                return None
            
            stats = result.data[0]
            
            return {
                'hasData': True,
                'heartRate': stats.get('avg_heart_rate'),
                'hrv': stats.get('avg_hrv_ms'),
                'sleepHours': stats.get('sleep_hours'),
                'steps': stats.get('total_steps'),
                'stressLevel': stats.get('avg_stress_level'),
                'lastSynced': stats.get('updated_at') or stats.get('created_at'),
                'source': stats.get('data_source', 'unknown'),
                'date': stats.get('date')
            }
            
        except Exception as e:
            logger.error(f"Error fetching latest summary: {e}")
            return None
