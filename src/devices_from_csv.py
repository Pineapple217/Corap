import csv
import logging
from repository import Device, db_init


logger = logging.getLogger(__name__)


def main():
    db_init()
    logger.info("importing csv...")
    devices = []
    with open("./devs.csv", "r") as file:
        reader = csv.DictReader(file)
        for d in reader:
            devices.append(
                Device(deveui=d["deveui"], name=d["name"], hashedname=d["hashedname"])
            )
    logger.info(f"Import {len(devices)} device(s)")
    Device.bulk_create(devices)
