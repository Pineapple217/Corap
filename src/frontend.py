from datetime import datetime, timedelta
from pprint import pprint
import streamlit as st
from peewee import *
from repository import Scrape, Device, get_db_size
import pandas as pd
import plotly.express as px


def main():
    st.set_page_config(layout="wide")

    rows = Device.select().dicts()
    devices = pd.DataFrame(rows).sort_values(["name"])
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
    delta_datetime = datetime.now() - timedelta(hours=24)
    rows = Scrape.select().where(Scrape.time_scraped > delta_datetime).dicts()
    scrapes = pd.DataFrame(rows).set_index(["id"])

    st.dataframe(scrapes, width=800, height=600)

    st.title("Devices")
    st.dataframe(devices, width=900, height=600)


if __name__ == "__main__":
    main()
