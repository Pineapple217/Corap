from pprint import pprint
import streamlit as st
from peewee import *
from repository import Scrape, close_db, db_init, Device
import pandas as pd
import plotly.express as px


def main():
    db_init()

    rows = Scrape.select().dicts()
    scrapes = pd.DataFrame(rows).set_index("id")

    rows = Device.select().dicts()
    devices = pd.DataFrame(rows).sort_values(["name"])

    last_scraped = Scrape.select(fn.Max(Scrape.time_scraped)).scalar()
    st.metric("Last scraped", last_scraped.strftime("%Y-%m-%d %H:%M:%S"))

    device = st.selectbox(
        "device",
        devices["deveui"],
        format_func=lambda d: devices[devices["deveui"] == d]["name"].iloc[0],
    )
    tab1, tab2, tab3 = st.tabs(["Temp", "Co2", "Humidity"])

    with tab1:
        fig_temp = px.line(
            scrapes[scrapes["deveui"] == device],
            x="time_updated",
            y="temp",
            markers=True,
        )
        st.plotly_chart(fig_temp, theme="streamlit", use_container_width=True)

    with tab2:
        fig_co2 = px.line(
            scrapes[scrapes["deveui"] == device],
            x="time_updated",
            y="co2",
            markers=True,
        )
        st.plotly_chart(fig_co2, theme="streamlit", use_container_width=True)

    with tab3:
        fig_hum = px.line(
            scrapes[scrapes["deveui"] == device],
            x="time_updated",
            y="humidity",
            markers=True,
        )
        st.plotly_chart(fig_hum, theme="streamlit", use_container_width=True)

    st.dataframe(scrapes, width=800, height=800)


if __name__ == "__main__":
    main()
