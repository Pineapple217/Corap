import logging
import os
import threading
from dotenv import load_dotenv
from sqlalchemy import URL
from apscheduler.schedulers.blocking import BlockingScheduler
import analyse_device


from scrape import scrape

logger = logging.getLogger(__name__)


load_dotenv()
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_DATABASE = os.getenv("DB_DATABASE")

db_url = URL.create(
    "postgresql+psycopg2",
    username=DB_USER,
    password=DB_PASSWORD,
    host=DB_HOST,
    database=DB_DATABASE,
    port=DB_PORT,
)
scheduler = BlockingScheduler()


def job():
    print("I'm working...")


def run_threaded(job_func):
    job_thread = threading.Thread(target=job_func)
    job_thread.start()


def run_scheduler():
    logger.info("Running scheduler")
    scheduler.add_jobstore("sqlalchemy", url=db_url)
    scheduler.add_job(
        scrape, "cron", minute="*/15", name="scrape", id="100", replace_existing=True
    )
    scheduler.add_job(
        analyse_device.analyse,
        "cron",
        minute="5-59/15",
        name="analyse_device",
        id="1000",
        replace_existing=True,
    )
    scheduler.start()
