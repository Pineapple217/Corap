from datetime import datetime, timedelta
from pprint import pprint
import streamlit as st
from peewee import *
from repository import Scrape, Device, get_db_size
import pandas as pd
import plotly.express as px


def main():
    st.set_page_config(layout="wide")

    st.title("Stats")
    col1, col2, col3, col4 = st.columns(4)

    rows = Device.select().dicts()
    devices = pd.DataFrame(rows).sort_values(["name"])

    last_scraped = Scrape.select(fn.Max(Scrape.time_scraped)).scalar()
    col1.metric("Last scraped", last_scraped.strftime("%Y-%m-%d %H:%M:%S"))

    scrape_count = Scrape.select().count()
    col2.metric("Scrape count", scrape_count)

    col3.metric("Database size", get_db_size())

    max_batch_nr = Scrape.select(fn.Max(Scrape.batch_id)).scalar()
    col4.metric("Batch count", max_batch_nr)

    st.title("About last 24h")
    col1, col2 = st.columns(2)

    delta_datetime = datetime.now() - timedelta(hours=24)
    scrape_count_delta = (
        Scrape.select().where(Scrape.time_scraped > delta_datetime).count()
    )
    scrape_accuracy = (scrape_count_delta) / (Device.select().count() * 4 * 24)
    col1.metric("Accuracy", f"{round(scrape_accuracy * 100, 2)} %")
    col2.metric("Delta scrapecount", scrape_count_delta)

    defect_devices_deveui = (
        Scrape.select(Scrape.deveui)
        .where(Scrape.temp == 0 and Scrape.co2 == 0 and Scrape.humidity == 0)
        .distinct()
    )
    defect_devices = Device.select().where(Device.deveui.in_(defect_devices_deveui))
    defect_devices_df = pd.DataFrame(defect_devices.dicts())

    st.title("Defecitve Devices")
    st.dataframe(defect_devices_df, width=900)

    st.title("Scrapes")
    rows = Scrape.select().where(Scrape.time_scraped > delta_datetime).dicts()
    scrapes = pd.DataFrame(rows).set_index(["id"])

    st.dataframe(scrapes, width=800, height=600)

    st.title("Devices")
    st.dataframe(devices, width=900, height=600)


if __name__ == "__main__":
    main()
