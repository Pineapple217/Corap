from pprint import pprint
import streamlit as st
from peewee import *
from repository import Scrape, close_db, connect_db
import pandas as pd


def main():
    connect_db()

    rows = list(Scrape.select().dicts())
    # pprint(rows)
    x = pd.DataFrame(rows).set_index("id")

    st.dataframe(x, width=800, height=800)

    close_db()


if __name__ == "__main__":
    main()
