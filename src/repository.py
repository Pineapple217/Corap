import datetime
import logging
import os
from peewee import *
from dotenv import load_dotenv

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
    time_scraped = DateTimeField(default=datetime.datetime.now)

    class Meta:
        db_table = "scrape"

    def __str__(self):
        return self.id + " | " + self.deveui

    def __repr__(self) -> str:
        return (
            f"Scrape(id={self.id}, batch_id={self.batch_id}, deveui={self.deveui}, co2={self.co2}, temp={self.temp}, "
            f"humidity={self.humidity}, time_updated={self.time_updated}, time_scraped={self.time_scraped})"
        )


def connect_db():
    logger.info("Connection to DB...")
    # db.set_time_zone(TIMEZONE)
    db.create_tables([Scrape], safe=True)


def seed_db():
    pass


def close_db():
    logger.info("clossing db")
    db.close()


connect_db()
