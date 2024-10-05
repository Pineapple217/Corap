from datetime import datetime, timedelta
import logging
import sched
import time
from concurrent.futures import ThreadPoolExecutor

import analyse_device
from scrape import scrape
import stats

logger = logging.getLogger(__name__)

scheduler = sched.scheduler(time.time, time.sleep)

INTERVAL = 15
MAX_WORKERS = 4


def run():
    try:
        scrape()
        time.sleep(1)
        analyse_device.generate_analysis()
        time.sleep(1)
        stats.generate_stats()
    except Exception as e:
        logger.error(e)


def job(run_moment, pool: ThreadPoolExecutor, func):
    n_run_moment = run_moment + timedelta(minutes=INTERVAL)
    logger.info(f"Schedulling next job for: {n_run_moment}")
    scheduler.enterabs(
        time.mktime(n_run_moment.timetuple()),
        1,
        job,
        argument=(n_run_moment, pool, func),
    )

    logger.info("Running job")
    pool.submit(func)


def start_scheduler(args):
    logger.info("Running scheduler")
    now = datetime.now()
    x = now.minute // INTERVAL
    minu = (x * INTERVAL) + INTERVAL
    run_moment = datetime(now.year, now.month, now.day, now.hour, 0, 0, 0) + timedelta(
        minutes=minu
    )
    logger.info(f"Next run on: {run_moment}")

    pool = ThreadPoolExecutor(max_workers=MAX_WORKERS)
    if args.f:
        pool.submit(run)

    scheduler.enterabs(
        time.mktime(run_moment.timetuple()), 1, job, argument=(run_moment, pool, run)
    )
    scheduler.run()
