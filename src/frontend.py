from datetime import datetime, timedelta
from pprint import pprint
import streamlit as st
from peewee import *
from repository import Scrape, close_db, db_init, Device
import pandas as pd
import plotly.express as px


def main():
    st.set_page_config(layout="wide")

    rows = Scrape.select().dicts()
    scrapes = pd.DataFrame(rows).set_index("id")

    rows = Device.select().dicts()
    devices = pd.DataFrame(rows).sort_values(["name"])

    last_scraped = Scrape.select(fn.Max(Scrape.time_scraped)).scalar()
    st.metric("Last scraped", last_scraped.strftime("%Y-%m-%d %H:%M:%S"))

    scrape_count = Scrape.select().count()
    st.metric("Scrape count", scrape_count)

    delta_datetime = datetime.now() - timedelta(hours=24)
    scrape_count_delta = (
        Scrape.select().where(Scrape.time_scraped > delta_datetime).count()
    )
    scrape_accuracy = (scrape_count_delta) / (Device.select().count() * 4 * 24)
    st.metric("Accuracy", f"{round(scrape_accuracy * 100, 2)} %")
    st.metric("Delta scrapecount", scrape_count_delta)

    st.dataframe(scrapes, width=800, height=800)
    st.dataframe(devices, width=800, height=800)


if __name__ == "__main__":
    main()
