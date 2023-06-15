import csv
from datetime import datetime
import logging
import re
from bs4 import BeautifulSoup
import requests
from peewee import fn

from repository import Scrape, close_db, db_init, Device


logger = logging.getLogger(__name__)
URL = "https://education.thingsflow.eu/IAQ/DeviceByQR"


def hashednames():
    return Device.select(Device.hashedname, Device.deveui).tuples()


MAX_REQUEST_RETRIES = 3
MAX_SCRAPE_RETRIES = 3
TIMEOUT_TIME = 10


def scrape():
    logger.info("Start scraping")
    batch_id = Scrape.select(fn.Max(Scrape.batch_id)).scalar()
    if batch_id is None:
        batch_id = 1
    else:
        batch_id += 1
    logger.info(f"Batch id: {batch_id}")

    for hashedname, deveui in hashednames():
        query = {"hashedname": hashedname}
        for i in range(MAX_SCRAPE_RETRIES):
            for j in range(MAX_REQUEST_RETRIES):
                try:
                    r = requests.post(URL, params=query, timeout=TIMEOUT_TIME)
                    break
                except requests.exceptions.ReadTimeout as e:
                    logger.warning(
                        f"Device {deveui} timed out. Retrying ({j+1}/{MAX_REQUEST_RETRIES})..."
                    )
                    continue
            else:
                logger.error(f"Failed to pull {deveui} due to Timeouts")
                continue

            try:
                page = BeautifulSoup(r.content, "html5lib")

                title = page.find("h1").text.replace("Show Device ", "")
                time = page.find("h4").text.replace("Last update: ", "")
                time = datetime.strptime(time, "%d/%m/%Y %H:%M")

                deveui = (
                    page.find_all("p", string=re.compile("DevEUI:"))[0]
                    .text.replace("DevEUI:", "")
                    .strip()
                )

                table = page.find("div", attrs={"class": "row"})
                data = table.findAll(
                    "div",
                    attrs={"class": "card-body"},
                )
                co2 = int(data[0].text.strip())
                temp = data[1].text.strip().replace("°C", "")
                humidity = int(data[2].text.strip().replace("%", ""))
                break
            except AttributeError as e:
                logger.warning(
                    f"{deveui} {e}. Retrying ({i+1}/{MAX_SCRAPE_RETRIES})..."
                )
                continue
        else:
            logger.error(f"Failed to pull {deveui} due to AttributeErrors")
            continue

        s = Scrape.create(
            deveui=deveui,
            batch_id=batch_id,
            co2=co2,
            temp=temp,
            humidity=humidity,
            time_updated=time,
        )
        logger.info(repr(s))
    logger.info("scraping done")
