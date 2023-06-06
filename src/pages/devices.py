import streamlit as st
from peewee import *
from repository import Scrape, close_db, db_init, Device
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta


def main():
    st.set_page_config(layout="wide")

    st.title("Device info")

    delta_datetime = datetime.now() - timedelta(days=2)
    rows = Scrape.select().where(Scrape.time_scraped > delta_datetime).dicts()
    scrapes = pd.DataFrame(rows).set_index("id")
    scrapes["temp"] = scrapes["temp"].astype(float)

    rows = Device.select().dicts()
    devices = pd.DataFrame(rows).sort_values(["name"])

    device_deveui = st.selectbox(
        "device",
        devices["deveui"],
        format_func=lambda d: devices[devices["deveui"] == d]["name"].iloc[0],
        label_visibility="collapsed",
    )
    device = Device.get(Device.deveui == device_deveui)

    st.write(f"[Scrape source]({device.url()})")
    dev_scrapes = scrapes[scrapes["deveui"] == device_deveui].sort_values(
        "time_scraped", ascending=False
    )

    col1, col2, col3 = st.columns(3)

    latest_scrape = dev_scrapes.iloc[0]
    prev_scrape = dev_scrapes.iloc[1]

    col1.metric(
        "Temp",
        latest_scrape["temp"],
        delta=round(latest_scrape["temp"] - prev_scrape["temp"], 1),
        delta_color="off",
    )
    col2.metric(
        "Co2",
        latest_scrape["co2"],
        delta=int(latest_scrape["co2"] - prev_scrape["co2"]),
        delta_color="inverse",
    )
    col3.metric(
        "Humidity",
        latest_scrape["humidity"],
        delta=int(latest_scrape["humidity"] - prev_scrape["humidity"]),
        delta_color="off",
    )

    tab1, tab2, tab3 = st.tabs(["Temp", "Co2", "Humidity"])

    with tab1:
        st.metric("volitility", round(dev_scrapes["temp"].std(), 4))
        fig_temp = px.line(
            dev_scrapes,
            x="time_scraped",
            y="temp",
            markers=True,
        )
        st.plotly_chart(fig_temp, theme="streamlit", use_container_width=True)

    with tab2:
        st.metric("volitility", round(dev_scrapes["co2"].std(), 4))
        fig_co2 = px.line(
            dev_scrapes,
            x="time_scraped",
            y="co2",
            markers=True,
        )
        st.plotly_chart(fig_co2, theme="streamlit", use_container_width=True)
        st.markdown(
            """
            ## About the CO2 Scale

            | CO2 Value  | Air Quality       |
            |------------|-------------------|
            | <= 450     | Excellent         |
            | 450 - 700  | Good              |
            | 700 - 800  | Lightly Polluted  |
            | 800 - 1500 | Heavily Polluted  |
            | > 1500     | Severely Polluted |

            """
        )

    with tab3:
        st.metric("volitility", round(dev_scrapes["humidity"].std(), 4))
        fig_hum = px.line(
            dev_scrapes,
            x="time_scraped",
            y="humidity",
            markers=True,
        )
        st.plotly_chart(fig_hum, theme="streamlit", use_container_width=True)


if __name__ == "__main__":
    main()
