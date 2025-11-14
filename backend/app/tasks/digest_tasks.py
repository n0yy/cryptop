from app.tasks.celery_app import celery_app
from app.utils.logger import logger


@celery_app.task(name="app.tasks.digest_tasks.generate_daily_digests")
def generate_daily_digests():
    try:
        logger.info("Generating daily digests for all users")
        
        return {"status": "success", "digests_sent": 0}
    
    except Exception as e:
        logger.error(f"Error generating daily digests: {e}")
        return {"status": "error", "message": str(e)}


@celery_app.task(name="app.tasks.digest_tasks.cleanup_old_data")
def cleanup_old_data():
    try:
        logger.info("Cleaning up old data")
        
        return {"status": "success", "records_deleted": 0}
    
    except Exception as e:
        logger.error(f"Error cleaning up old data: {e}")
        return {"status": "error", "message": str(e)}
