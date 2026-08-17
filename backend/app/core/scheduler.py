from apscheduler.schedulers.asyncio import AsyncIOScheduler 
from app.db.session import AsyncSessionLocal 
from app.services.application import ApplicationService 
from datetime import datetime
scheduler = AsyncIOScheduler()

async def auto_ghost_detection_job():
    async with AsyncSessionLocal() as session:
        await ApplicationService.detect_and_mark_ghosted(session,days_threshold=14)

def start_scheduler():
    scheduler.add_job(
        auto_ghost_detection_job,
        trigger="interval",
        hours=24,
        id="ghost_detection_job",
        replace_existing=True,
        next_run_time=datetime.now(),
    )
    scheduler.start()

def shutdown_scheduler():
    scheduler.shutdown()