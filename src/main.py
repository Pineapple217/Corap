import datetime
import logging
import os
import time
from bs4 import BeautifulSoup
import asyncio
import argparse
from scrape import scrape
from device_find import device_find
from tortoise import Tortoise
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s: %(message)s",
    handlers=[
        logging.StreamHandler(),  # Output to stdout
    ],
)
logger = logging.getLogger(__name__)

DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_DATABASE = os.getenv("DB_DATABASE")
TIMEZONE = os.getenv("TIMEZONE")


async def init():
    await Tortoise.init(
        config={
            "connections": {
                "default": {
                    "engine": "tortoise.backends.asyncpg",
                    "credentials": {
                        "host": DB_HOST,
                        "port": DB_PORT,
                        "user": DB_USER,
                        "password": DB_PASSWORD,
                        "database": DB_DATABASE,
                    },
                },
            },
            "apps": {
                "corap": {
                    "models": ["models"],
                    "default_connection": "default",
                }
            },
            "use_tz": True,
            "timezone": TIMEZONE,
        }
    )
    # Generate the schema
    await Tortoise.generate_schemas()


async def main():
    start = time.time()
    parser = argparse.ArgumentParser(description="CORAP CLI")

    subparsers = parser.add_subparsers(dest="command")
    scrape_parser = subparsers.add_parser("scrape", help="Scrape data")
    scrape_parser.set_defaults(func=scrape)

    device_find_parser = subparsers.add_parser("device_find", help="Find devices")
    device_find_parser.set_defaults(func=device_find)

    args = parser.parse_args()

    if not hasattr(args, "func"):
        parser.print_help()
        return
    await init()
    await args.func()

    end = time.time()
    total_time = end - start
    formatted_time = str(datetime.timedelta(seconds=total_time))

    logger.info(f"Execution time: {formatted_time}")


if __name__ == "__main__":
    asyncio.run(main())
