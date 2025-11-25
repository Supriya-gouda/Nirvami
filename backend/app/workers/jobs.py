"""Scheduled jobs for background processing."""
from app.utils.database import get_supabase
from app.services.aura_service import AuraService
from datetime import date, datetime, timedelta
import logging

logger = logging.getLogger(__name__)


def calculate_wellness_score_for_user(user_id: str, target_date: date, supabase):
    """Calculate wellness score for a user on a specific date."""
    from app.api.routes.wellness import calculate_wellness_score
    
    try:
        wellness_data = calculate_wellness_score(user_id, target_date, supabase)
        
        # Insert/update in database with proper upsert
        supabase.table("wellness_scores").upsert(
            wellness_data,
            on_conflict="user_id,date"
        ).execute()
        
        logger.info(f"Computed wellness score for user {user_id}: {wellness_data['overall_score']}")
        return True
    except Exception as e:
        logger.error(f"Error computing wellness for user {user_id}: {e}")
        return False


def compute_daily_wellness_scores():
    """Compute wellness scores for all users for yesterday."""
    logger.info("Starting daily wellness score computation...")
    
    try:
        supabase = get_supabase(use_service_role=True)
        
        # Get all active users
        users = supabase.table("profiles").select("id").execute()
        
        target_date = date.today() - timedelta(days=1)
        
        success_count = 0
        for user in users.data:
            user_id = user["id"]
            if calculate_wellness_score_for_user(user_id, target_date, supabase):
                success_count += 1
        
        logger.info(f"Daily wellness score computation completed: {success_count}/{len(users.data)} users")
        
    except Exception as e:
        logger.error(f"Error in wellness score job: {e}")


def aggregate_daily_emotions():
    """Aggregate emotion logs into daily summaries."""
    logger.info("Starting daily emotion aggregation...")
    
    try:
        supabase = get_supabase(use_service_role=True)
        
        # Get all users
        users = supabase.table("profiles").select("id").execute()
        
        target_date = date.today() - timedelta(days=1)
        
        for user in users.data:
            user_id = user["id"]
            try:
                # Get emotion logs for the day
                start_time = datetime.combine(target_date, datetime.min.time())
                end_time = datetime.combine(target_date, datetime.max.time())
                
                emotions = supabase.table("emotion_logs").select("*").eq(
                    "user_id", user_id
                ).gte("created_at", start_time.isoformat()).lte(
                    "created_at", end_time.isoformat()
                ).execute()
                
                if not emotions.data:
                    continue
                
                # Aggregate emotions
                emotion_counts = {}
                total_entries = len(emotions.data)
                
                for emotion in emotions.data:
                    etype = emotion["emotion_type"]
                    emotion_counts[etype] = emotion_counts.get(etype, 0) + 1
                
                # Calculate distribution
                emotion_dist = {
                    k: v / total_entries for k, v in emotion_counts.items()
                }
                
                dominant = max(emotion_counts, key=emotion_counts.get)
                
                # Create aggregate
                aggregate_data = {
                    "user_id": user_id,
                    "date": target_date.isoformat(),
                    "dominant_emotion": dominant,
                    "emotion_distribution": emotion_dist,
                    "total_entries": total_entries
                }
                
                supabase.table("emotion_aggregates").upsert(aggregate_data).execute()
                
                logger.info(f"Aggregated emotions for user {user_id}")
                
            except Exception as e:
                logger.error(f"Error aggregating emotions for user {user_id}: {e}")
        
        logger.info("Daily emotion aggregation completed")
        
    except Exception as e:
        logger.error(f"Error in emotion aggregation job: {e}")


def generate_daily_auras():
    """Generate aura visualizations for all users."""
    logger.info("Starting daily aura generation...")
    
    try:
        supabase = get_supabase(use_service_role=True)
        aura_service = AuraService(supabase)
        
        # Get all users
        users = supabase.table("profiles").select("id").execute()
        
        target_date = date.today() - timedelta(days=1)
        
        success_count = 0
        for user in users.data:
            user_id = user["id"]
            try:
                # Run async function in sync context
                import asyncio
                try:
                    loop = asyncio.get_event_loop()
                except RuntimeError:
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                
                loop.run_until_complete(aura_service.generate_daily_aura(user_id, target_date))
                logger.info(f"Generated aura for user {user_id}")
                success_count += 1
            except Exception as e:
                logger.error(f"Error generating aura for user {user_id}: {e}")
        
        logger.info(f"Daily aura generation completed: {success_count}/{len(users.data)} users")
        
    except Exception as e:
        logger.error(f"Error in aura generation job: {e}")


def compute_meal_emotion_correlations():
    """Compute correlations between meals and emotions for all users."""
    logger.info("Starting meal-emotion correlation computation...")
    
    try:
        from app.services.meal_service import MealCorrelationService
        
        supabase = get_supabase(use_service_role=True)
        
        # Get all active users
        users = supabase.table("profiles").select("id").execute()
        
        success_count = 0
        total_correlations = 0
        
        for user in users.data:
            user_id = user["id"]
            
            try:
                # Run correlation analysis for user
                result = MealCorrelationService.run_correlation_analysis(user_id)
                
                if result["success"]:
                    success_count += 1
                    total_correlations += result["correlations_stored"]
                    
            except Exception as e:
                logger.error(f"Error computing correlations for user {user_id}: {e}")
        
        logger.info(f"Meal-emotion correlation computation completed: {success_count}/{len(users.data)} users, {total_correlations} correlations stored")
        
    except Exception as e:
        logger.error(f"Error in meal correlation job: {e}")


def sync_wearable_data():
    """Process and normalize wearable data."""
    logger.info("Starting wearable data sync...")
    
    try:
        # Implementation here
        logger.info("Wearable data sync completed")
        
    except Exception as e:
        logger.error(f"Error in wearable sync job: {e}")
