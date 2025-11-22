"""Background worker for scheduled tasks using RQ."""
import os
import sys

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from redis import Redis
from rq import Queue
from app.config import settings
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Connect to Redis
redis_conn = Redis.from_url(settings.REDIS_URL)

# Create queues
default_queue = Queue('default', connection=redis_conn)
high_priority_queue = Queue('high', connection=redis_conn)
low_priority_queue = Queue('low', connection=redis_conn)


if __name__ == '__main__':
    from rq import Worker
    
    logger.info("Starting RQ worker...")
    
    # Start worker listening to all queues
    worker = Worker(
        [high_priority_queue, default_queue, low_priority_queue],
        connection=redis_conn
    )
    
    worker.work()
