import asyncio
import os
import streamlit as st
import psycopg2
from dotenv import load_dotenv

from main import db_init


async def main():
    await db_init()
    # pass
    load_dotenv()

    DB_HOST = os.getenv("DB_HOST")
    DB_PORT = os.getenv("DB_PORT")
    DB_USER = os.getenv("DB_USER")
    DB_PASSWORD = os.getenv("DB_PASSWORD")
    DB_DATABASE = os.getenv("DB_DATABASE")

    # Initialize connection.
    # Uses st.cache_resource to only run once.
    @st.cache_resource
    def init_connection():
        return psycopg2.connect(
            host=DB_HOST,
            port=DB_PORT,
            dbname=DB_DATABASE,
            user=DB_USER,
            password=DB_PASSWORD,
        )

    conn = init_connection()

    # Perform query.
    # Uses st.cache_data to only rerun when the query changes or after 10 min.
    @st.cache_data(ttl=600)
    def run_query(query):
        with conn.cursor() as cur:
            cur.execute(query)
            return cur.fetchall()

    rows = run_query("SELECT * from scrape;")
    st.dataframe(rows, width=800, height=800)


if __name__ == "__main__":
    asyncio.run(main())
