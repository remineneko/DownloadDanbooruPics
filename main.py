from BackgroundCode.DownloadModes import auto_download
from apscheduler.schedulers.background import BlockingScheduler

def main():
    sched = BlockingScheduler()
    sched.add_job(auto_download(), 'cron', day_of_week='mon-sun', hour=1, minute=00)
    sched.start()

main()