import logging
import threading
import schedule
import time

from scrape import scrape

logger = logging.getLogger(__name__)


def job():
    print("I'm working...")


def run_threaded(job_func):
    job_thread = threading.Thread(target=job_func)
    job_thread.start()


def run_scheduler():
    logger.info("Running scheduler")

    j = schedule.every(15).minutes.do(run_threaded, scrape)
    logger.info(j)

    run_threaded(scrape)
    while True:
        schedule.run_pending()
        time.sleep(1)
