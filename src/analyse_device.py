from datetime import datetime, timedelta
import logging
import numpy as np

import pandas as pd

from repository import Scrape, Device, AnalysisDevice

logger = logging.getLogger(__name__)


def defect_detect():
    logger.info("Defect detect...")

    delta_datetime = datetime.now() - timedelta(hours=24)
    rows = Scrape.select().where(Scrape.time_scraped > delta_datetime).dicts()
    scrapes = pd.DataFrame(rows).set_index(["deveui", "id"])

    defects = []
    for dev_id, dev_df in scrapes.groupby(level=0):
        logger.info(f"Checking {dev_id}")
        if not np.all(dev_df["temp"] == dev_df["temp"].iloc[0]):
            continue
        if not np.all(dev_df["co2"] == dev_df["co2"].iloc[0]):
            continue
        if not np.all(dev_df["humidity"] == dev_df["humidity"].iloc[0]):
            continue
        defects.append(dev_id)
    logger.info(f"Defective devices (count: {len(defects)}): {defects}")
    return defects


def analyse():
    olds = [r.id for r in AnalysisDevice.select()]
    defective_devices_ids = defect_detect()
    for device in Device.select(Device.deveui):
        if device.deveui in defective_devices_ids:
            AnalysisDevice.create(device=device, is_defect=True)
        else:
            AnalysisDevice.create(device=device, is_defect=False)
    AnalysisDevice.delete().where(AnalysisDevice.id.in_(olds)).execute()


if __name__ == "__main__":
    analyse()
