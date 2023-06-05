import logging
import os
from dotenv import load_dotenv
import psycopg2

load_dotenv()

DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_DATABASE = os.getenv("DB_DATABASE")


logger = logging.getLogger(__name__)


def main():
    conn = psycopg2.connect(
        user=DB_USER, password=DB_PASSWORD, host=DB_HOST, port=DB_PORT
    )
    conn.autocommit = True
    cursor = conn.cursor()
    sql = f"""
    CREATE DATABASE {DB_DATABASE}
    """
    # WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = '{DB_DATABASE}')
    cursor.execute(sql)
    logger.info(f"Database '{DB_DATABASE}' created successfully")
    conn.close()


if __name__ == "__main__":
    main()
