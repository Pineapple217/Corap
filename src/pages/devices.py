import streamlit as st
from peewee import *
from repository import Scrape, Device
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta


@st.cache_data(ttl=60 * 5, show_spinner="Fetching data")
def get_device_srapes(deveui, days):
    delta_datetime = datetime.now() - timedelta(days=days)
    rows = (
        Scrape.select()
        .where(Scrape.time_scraped > delta_datetime)
        .where(Scrape.deveui == deveui)
        .dicts()
    )
    scrapes = pd.DataFrame(rows).set_index("id")
    scrapes["temp"] = scrapes["temp"].astype(float)
    return scrapes


@st.cache_data(ttl=60 * 5, show_spinner="Fething devices")
def get_devices():
    rows = Device.select().dicts()
    devices = pd.DataFrame(rows).sort_values(["name"])
    return devices


def main():
    st.set_page_config(layout="wide")

    st.title("Device info")

    devices = get_devices()

    tab1, tab2 = st.tabs(["By name", "By deveui"])
    device = None
    with tab1:
        device_deveui = st.selectbox(
            "device",
            devices["deveui"],
            format_func=lambda d: devices[devices["deveui"] == d]["name"].iloc[0],
            label_visibility="collapsed",
        )
        device = Device.get(Device.deveui == device_deveui)

    with tab2:
        device_deveui = st.text_input(
            "deveui", value=device_deveui, label_visibility="collapsed"
        )
        try:
            device = Device.get(Device.deveui == device_deveui)
        except:
            st.stop()

    days = st.selectbox("Range (days)", [1, 3, 10, 100])

    st.write(f"[Scrape source]({device.url()})")
    dev_scrapes = get_device_srapes(device_deveui, days)

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
