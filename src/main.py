import datetime
import logging
import time
import argparse
from scrape import scrape
from device_find import device_find
from dotenv import load_dotenv

from repository import connect_db, close_db
from device_polling import polling_test

load_dotenv()

logging.basicConfig(
    level=logging.DEBUG,
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
    scrape_parser = subparsers.add_parser("scrape", help="Scrape data")
    scrape_parser.set_defaults(func=scrape)

    device_find_parser = subparsers.add_parser("device_find", help="Find devices")
    device_find_parser.set_defaults(func=device_find)

    device_find_parser = subparsers.add_parser(
        "polling_test", help="Tests device polling rate"
    )
    device_find_parser.set_defaults(func=polling_test)

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
