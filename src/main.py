import datetime
import inspect
import logging
import time
import argparse
from dotenv import load_dotenv

from device_find import device_find
from scrape import scrape
from device_polling import polling_test
from scheduler import start_scheduler
from analyse_device import generate_analysis
from stats import generate_stats

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(module)s | %(levelname)s: %(message)s",
    handlers=[
        logging.StreamHandler(),  # Output to stdout
    ],
)
logger = logging.getLogger(__name__)

from repository import db_init


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

    sp = subparsers.add_parser("scheduler", help="Run the scheduler")
    sp.add_argument(
        "-f", action="store_true", help="Force scheduler to schedule immediately"
    )
    sp.set_defaults(func=start_scheduler)

    subparsers.add_parser("db_init", help="Create database and tables").set_defaults(
        func=db_init
    )

    subparsers.add_parser("gen_analysis", help="Run all analysis").set_defaults(
        func=generate_analysis
    )

    subparsers.add_parser("gen_stats", help="Run all stats").set_defaults(
        func=generate_stats
    )

    args = parser.parse_args()

    if not hasattr(args, "func"):
        parser.print_help()
        return

    if len(inspect.signature(args.func).parameters) == 0:
        args.func()
    else:
        args.func(args)

    end = time.time()
    total_time = end - start
    formatted_time = str(datetime.timedelta(seconds=total_time))

    logger.info(f"Execution time: {formatted_time}")


if __name__ == "__main__":
    main()
