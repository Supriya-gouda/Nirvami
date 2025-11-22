"""Scheduler for periodic tasks."""
import schedule
import time
import logging
from app.workers.worker import default_queue
from app.workers.jobs import (
    compute_daily_wellness_scores,
    aggregate_daily_emotions,
    generate_daily_auras,
    compute_meal_emotion_correlations,
    sync_wearable_data
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def schedule_jobs():
    """Schedule all periodic jobs."""
    
    # Daily jobs - run at 2 AM
    schedule.every().day.at("02:00").do(
        lambda: default_queue.enqueue(aggregate_daily_emotions)
    )
    
    schedule.every().day.at("02:30").do(
        lambda: default_queue.enqueue(generate_daily_auras)
    )
    
    schedule.every().day.at("03:00").do(
        lambda: default_queue.enqueue(compute_daily_wellness_scores)
    )
    
    # Hourly jobs
    schedule.every().hour.do(
        lambda: default_queue.enqueue(compute_meal_emotion_correlations)
    )
    
    # Every 4 hours
    schedule.every(4).hours.do(
        lambda: default_queue.enqueue(sync_wearable_data)
    )
    
    logger.info("All jobs scheduled successfully")


if __name__ == '__main__':
    logger.info("Starting job scheduler...")
    schedule_jobs()
    
    while True:
        schedule.run_pending()
        time.sleep(60)  # Check every minute
