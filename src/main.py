import datetime
import logging
import time
import argparse
from scrape import scrape
from device_find import device_find
from dotenv import load_dotenv
from devices_from_csv import main as import_devices

from repository import db_init, close_db
from device_polling import polling_test
from schedular import run_scheduler

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s: %(message)s",
    handlers=[
        logging.StreamHandler(),  # Output to stdout
    ],
)
logger = logging.getLogger(__name__)


def main():
    start = time.time()
    parser = argparse.ArgumentParser(description="CORAP CLI")

    subparsers = parser.add_subparsers(dest="command")
    subparsers.add_parser("scrape", help="Scrape data").set_defaults(func=scrape)

    subparsers.add_parser("device_find", help="Find devices").set_defaults(
        func=device_find
    )

    subparsers.add_parser(
        "polling_test", help="Tests device polling rate"
    ).set_defaults(func=polling_test)

    subparsers.add_parser(
        "import_devices", help="Imports devices form csv"
    ).set_defaults(func=import_devices)

    subparsers.add_parser("scheduler", help="Run the scheduler").set_defaults(
        func=run_scheduler
    )

    subparsers.add_parser("db_init", help="Create database and tables").set_defaults(
        func=db_init
    )

    args = parser.parse_args()

    if not hasattr(args, "func"):
        parser.print_help()
        return
    args.func()

    end = time.time()
    total_time = end - start
    formatted_time = str(datetime.timedelta(seconds=total_time))

    logger.info(f"Execution time: {formatted_time}")


if __name__ == "__main__":
    main()
