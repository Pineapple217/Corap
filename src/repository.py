from datetime import datetime, timedelta
import logging
import os
from peewee import *
from dotenv import load_dotenv
import psycopg2

load_dotenv()

DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_DATABASE = os.getenv("DB_DATABASE")
# TIMEZONE = os.getenv("TIMEZONE")


logger = logging.getLogger(__name__)


db = PostgresqlDatabase(
    host=DB_HOST, port=DB_PORT, user=DB_USER, password=DB_PASSWORD, database=DB_DATABASE
)


class BaseModel(Model):
    class Meta:
        database = db


class Scrape(BaseModel):
    id = AutoField(primary_key=True)
    batch_id = IntegerField()
    deveui = CharField()
    co2 = SmallIntegerField()
    temp = DecimalField(max_digits=4, decimal_places=1)
    humidity = SmallIntegerField()
    time_updated = DateTimeField()
    time_scraped = DateTimeField(default=datetime.now)

    def get_missed_data(start_time, end_time, distinct=True):
        columns = (
            "DISTINCT ON (current.deveui, previous.time_updated)" if distinct else ""
        )
        cursor = db.execute_sql(
            f"""
        SELECT
            {columns}
            previous.deveui AS deveui,
            previous.time_updated AS previous_time_updated,
            current.time_updated AS current_time_updated
        FROM
            scrape AS current
        LEFT JOIN
            scrape AS previous ON previous.deveui = current.deveui
            AND previous.time_updated = (
                SELECT MAX(time_updated)
                FROM scrape
                WHERE deveui = current.deveui
                AND time_updated < current.time_updated
            )
        WHERE
            current.time_updated - previous.time_updated > interval '15 minutes'
            AND current.time_updated >= %s
            AND current.time_updated <= %s
        ORDER BY
		    current.deveui, previous.time_updated;
        """,
            (
                end_time.strftime("%Y-%m-%d %H:%M:%S"),
                start_time.strftime("%Y-%m-%d %H:%M:%S"),
            ),
        )
        return cursor.fetchall()

    class Meta:
        db_table = "scrape"

    def __str__(self):
        return self.id + " | " + self.deveui

    def __repr__(self) -> str:
        return (
            f"Scrape(id={self.id}, batch_id={self.batch_id}, deveui={self.deveui}, co2={self.co2}, temp={self.temp}, "
            f"humidity={self.humidity}, time_updated={self.time_updated}, time_scraped={self.time_scraped})"
        )


class Device(BaseModel):
    deveui = CharField(max_length=16, primary_key=True)
    name = CharField()
    hashedname = CharField(max_length=64)

    def url(self):
        return f"https://education.thingsflow.eu/IAQ/DeviceByQR?hashedname={self.hashedname}"


def db_init():
    # db.set_time_zone(TIMEZONE)

    db.create_tables([Scrape, Device], safe=True)
    logger.info(f"Tables created successfully")


def seed_db():
    pass


def close_db():
    logger.info("clossing db")
    db.close()


def get_db_size() -> str:
    return str(
        db.execute_sql(
            f"SELECT pg_size_pretty(pg_database_size('{DB_DATABASE}'));"
        ).fetchone()[0]
    )
