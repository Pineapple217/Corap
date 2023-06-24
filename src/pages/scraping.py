from datetime import datetime, timedelta
from pprint import pprint
import streamlit as st
from peewee import *
from repository import Scrape, Device, get_db_size
import pandas as pd


# @st.cache_data(ttl=60 * 15, show_spinner="Executing big query")
def get_missed_data_24h():
    delta_datetime = datetime.now() - timedelta(hours=24)
    rows = Scrape.get_missed_data(datetime.now(), delta_datetime)
    df = pd.DataFrame(rows, columns=["id", "prev", "next"])
    df["delta"] = df["next"] - df["prev"] + pd.to_datetime("1970/01/01")
    return df


def main():
    st.set_page_config(layout="wide")

    st.title("Stats")
    col1, col2, col3, col4 = st.columns(4)

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

    st.title("Devices")
    missed = get_missed_data_24h()
    st.dataframe(missed, width=900, height=600)


if __name__ == "__main__":
    main()
