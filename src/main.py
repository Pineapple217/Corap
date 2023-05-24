import datetime
import logging
import time
from bs4 import BeautifulSoup
import asyncio
import argparse
from scrape import scrape
from device_find import device_find
from tortoise import Tortoise

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s: %(message)s",
    handlers=[
        logging.StreamHandler(),  # Output to stdout
    ],
)
logger = logging.getLogger(__name__)


async def init():
    # Here we connect to a SQLite DB file.
    # also specify the app name of "models"
    # which contain models from "app.models"
    await Tortoise.init(
        config={
            "connections": {
                # Dict format for connection
                "default": {
                    "engine": "tortoise.backends.asyncpg",
                    "credentials": {
                        "host": "localhost",
                        "port": "5432",
                        "user": "corap",
                        "password": "root",
                        "database": "corap",
                    },
                },
            },
            "apps": {
                "corap": {
                    "models": ["models"],
                    # If no default_connection specified, defaults to 'default'
                    "default_connection": "default",
                }
            },
            # "routers": ["path.router1", "path.router2"],
            "use_tz": False,
            "timezone": "UTC",
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
