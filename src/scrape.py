import csv
import logging
from bs4 import BeautifulSoup
import requests
import os

logger = logging.getLogger(__name__)
URL = "https://education.thingsflow.eu/IAQ/DeviceByQR"


def hashednames():
    with open("./src/ids.csv", "r") as file:
        reader = csv.DictReader(file)
        for row in reader:
            hashedname = row["hashedname"]
            yield hashedname


def scrape():
    for hashedname in hashednames():
        query = {"hashedname": hashedname}
        r = requests.post(URL, params=query)
        soup = BeautifulSoup(r.content, "html5lib")

        quotes = []  # a list to store quotes

        title = soup.find("h1").text.replace("Show Device ", "")
        time = soup.find("h4").text.replace("Last update: ", "")
        print(title, time, end="")
        table = soup.find("div", attrs={"class": "row"})

        for label, value in zip(
            ["CO2 in ppm", "Temperature", "Humidity"],
            table.findAll(
                "div",
                attrs={"class": "card-body"},
            ),
        ):
            print(f" {value.text.strip()}", end="")
        print()
