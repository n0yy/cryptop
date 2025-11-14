from app.tasks.celery_app import celery_app
from app.utils.logger import logger


@celery_app.task(name="app.tasks.report_tasks.generate_report")
def generate_report(report_id: str, user_id: int, report_type: str, symbols: list):
    try:
        logger.info(f"Generating report {report_id} for user {user_id}")
        
        return {
            "status": "success",
            "reportId": report_id,
            "downloadUrl": f"https://cdn.example.com/reports/{report_id}.pdf"
        }
    
    except Exception as e:
        logger.error(f"Error generating report: {e}")
        return {"status": "error", "message": str(e)}


@celery_app.task(name="app.tasks.report_tasks.send_scheduled_report")
def send_scheduled_report(user_id: int, report_type: str):
    try:
        logger.info(f"Sending scheduled {report_type} report to user {user_id}")
        
        return {"status": "success"}
    
    except Exception as e:
        logger.error(f"Error sending scheduled report: {e}")
        return {"status": "error", "message": str(e)}
