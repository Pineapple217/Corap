import csv
from datetime import datetime
import logging
import re
from bs4 import BeautifulSoup
import pytz
import requests
import os
from models import Scrape
from tortoise.expressions import Q
from tortoise.functions import Max


logger = logging.getLogger(__name__)
URL = "https://education.thingsflow.eu/IAQ/DeviceByQR"


def hashednames():
    with open("./src/ids.csv", "r") as file:
        reader = csv.DictReader(file)
        for row in reader:
            hashedname = row["hashedname"]
            yield hashedname


async def scrape():
    batch_id = (
        await Scrape.annotate(batch_id=Max("batch_id")).first().values("batch_id")
    )
    batch_id = batch_id["batch_id"]
    if batch_id is None:
        batch_id = 1
    else:
        batch_id += 1
    logger.info(f"Batch id: {batch_id}")
    for hashedname in hashednames():
        try:
            query = {"hashedname": hashedname}
            r = requests.post(URL, params=query)
            page = BeautifulSoup(r.content, "html5lib")

            title = page.find("h1").text.replace("Show Device ", "")
            time = page.find("h4").text.replace("Last update: ", "")
            # time = datetime.strptime(time, "%d/%m/%Y %H:%M")
            time = datetime.strptime(time, "%d/%m/%Y %H:%M")
            # time = pytz.timezone("Europe/Brussels").localize(time)

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
        except Exception as e:
            logger.error(e)
            continue
        logger.info(f"{title} {batch_id} {time} {deveui} {co2} {temp} {humidity}")

        await Scrape.create(
            deveui=deveui,
            batch_id=batch_id,
            co2=co2,
            temp=temp,
            humidity=humidity,
            time_updated=time,
        )
