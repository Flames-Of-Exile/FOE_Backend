import atexit
from apscheduler.schedulers.background import BackgroundScheduler

from views.calendar import notify_events

def schedule_builder():
    scheduler = BackgroundScheduler()
    scheduler.add_job(func=notify_events, trigger="cron", minute='*/1')
    scheduler.start()
    atexit.register(lambda: scheduler.shutdown())
