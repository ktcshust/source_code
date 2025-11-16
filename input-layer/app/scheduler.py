# APScheduler bootstrap
import asyncio
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from app.workers.rss_fetcher import run_all_feed_sources

scheduler = AsyncIOScheduler()

def start_scheduler():
    # e.g., run every 5 minutes
    scheduler.add_job(run_all_feed_sources, CronTrigger.from_crontab("*/5 * * * *"), id="rss_fetch")
    scheduler.start()
