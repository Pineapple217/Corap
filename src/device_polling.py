import csv
import datetime
import logging
import re
from bs4 import BeautifulSoup
import requests
import time

logger = logging.getLogger(__name__)
URL = "https://education.thingsflow.eu/IAQ/DeviceByQR"
HASHEDNAME = "b8004bde67a16c938f5ad35e92df5c26d53460229008b63b94598f74b35968e8"


def polling_test():
    starttime = time.time()
    q = []
    while True:
        logger.info(f"Scraping...")
        try:
            query = {"hashedname": HASHEDNAME}
            r = requests.post(URL, params=query)
            page = BeautifulSoup(r.content, "html5lib")

            time_page = page.find("h4").text.replace("Last update: ", "")
            time_page = datetime.datetime.strptime(time_page, "%d/%m/%Y %H:%M")

            q.append(time_page)
            q = sorted(set(q))  # remove duplicates
            if len(q) > 10:
                q.pop(0)
            logger.debug(q)
            if len(q) <= 1:
                average_difference = datetime.timedelta(0)
            else:
                differences = [j - i for i, j in zip(q[:-1], q[1:])]
                average_difference = sum(differences, datetime.timedelta(0)) / len(
                    differences
                )
            logger.info(f"Last update: {str(time_page)}")
            logger.info(f"Avarage of last 10: {average_difference}")
        except Exception as e:
            logger.error(e)
        logger.info("Sleeping...")
        time.sleep(60.0 - ((time.time() - starttime) % 60.0))
