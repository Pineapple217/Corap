from datetime import datetime
import logging
import re
from bs4 import BeautifulSoup
import psycopg.rows
import zoneinfo
import requests
import psycopg

from repository import get_db

logger = logging.getLogger(__name__)
HEADERS = {
    "Cache-Control": "no-cache",
    "Pragma": "no-cache",
    "Accept-Encoding": "gzip",
}
URL = "https://education.thingsflow.eu/IAQ/DeviceByQR"


def hashednames(db: psycopg.Connection):
    cur = db.cursor(row_factory=psycopg.rows.tuple_row)
    devs = cur.execute("SELECT hashedname, deveui FROM devices").fetchall()
    cur.close()
    return devs


MAX_REQUEST_RETRIES = 3
MAX_SCRAPE_RETRIES = 3
TIMEOUT_TIME = 10
brussels_tz = zoneinfo.ZoneInfo("Europe/Brussels")


def scrape():
    logger.info("Start scraping")
    db = get_db()

    batch_id = db.execute("SELECT MAX(batch_id) as m from scrapes").fetchone()["m"]
    if batch_id is None:
        batch_id = 1
    else:
        batch_id += 1

    logger.info(f"Batch id: {batch_id}")

    for hashedname, deveui in hashednames(db):
        query = {"hashedname": hashedname}
        for i in range(MAX_SCRAPE_RETRIES):
            for j in range(MAX_REQUEST_RETRIES):
                try:
                    r = requests.get(
                        URL, params=query, timeout=TIMEOUT_TIME, headers=HEADERS
                    )
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
                page = BeautifulSoup(r.content, "html.parser")

                _title = page.find("h1").text.replace("Show Device ", "")
                time = page.find("h4").text.replace("Last update: ", "")
                time = datetime.strptime(time, "%d/%m/%Y %H:%M")
                time.replace(tzinfo=brussels_tz)

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
                humi = int(data[2].text.strip().replace("%", ""))
                break
            except AttributeError as e:
                logger.warning(
                    f"{deveui} {e}. Retrying ({i+1}/{MAX_SCRAPE_RETRIES})..."
                )
                continue
        else:
            logger.error(f"Failed to pull {deveui} due to AttributeErrors")
            continue

        s = (batch_id, deveui, co2, temp, humi, time)
        db.execute(
            """
            INSERT INTO scrapes (batch_id, deveui, co2, temp, humi, updated_at)
            VALUES (%s, %s, %s, %s, %s, %s)
            """,
            s,
        )
        logger.info(s)
    db.commit()
    db.close()
    logger.info("scraping done")
