from datetime import datetime, timedelta
import logging
import numpy as np

import pandas as pd

from repository import Scrape

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
