import csv
import logging
import os
from dotenv import load_dotenv
import psycopg

load_dotenv()

DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_DATABASE = os.getenv("DB_DATABASE")
TIMEZONE = os.getenv("TIMEZONE")

logger = logging.getLogger(__name__)


def db_init():
    logger.info("Checking for database")
    with psycopg.connect(
        user=DB_USER,
        password=DB_PASSWORD,
        host=DB_HOST,
        port=DB_PORT,
        dbname="postgres",
    ) as conn:
        conn.autocommit = True
        db_name = conn.execute(
            "SELECT datname FROM pg_catalog.pg_database WHERE lower(datname) = %s;",
            (DB_DATABASE,),
        ).fetchone()
        if db_name is not None and db_name[0] == DB_DATABASE:
            logger.info(f"Database found: '{db_name[0]}'")
        else:
            logger.info(f"Database not found, creating databse: '{DB_DATABASE}'")
            conn.execute(f"CREATE DATABASE {DB_DATABASE};")

    conn = psycopg.connect(
        user=DB_USER,
        password=DB_PASSWORD,
        host=DB_HOST,
        port=DB_PORT,
        dbname=DB_DATABASE,
    )

    logger.info("Creating tables")
    conn.execute(
        """
            CREATE TABLE IF NOT EXISTS devices
            (
                deveui character varying(16) NOT NULL,
                name text NOT NULL,
                hashedname character varying(64) NOT NULL,
                PRIMARY KEY (deveui)
            );
        """
    )
    conn.execute(
        """
            CREATE TABLE IF NOT EXISTS scrapes
            (
                id bigserial NOT NULL,
                batch_id integer NOT NULL,
                deveui character varying(16) NOT NULL,
                co2 smallint NOT NULL,
                temp numeric(4, 1) NOT NULL,
                humi smallint NOT NULL,
                updated_at timestamp with time zone NOT NULL,
                scraped_at timestamp with time zone NOT NULL DEFAULT NOW(),
                PRIMARY KEY (id)
            );
        """
    )
    conn.execute(
        """
            CREATE TABLE IF NOT EXISTS device_analyses
            (
                id serial NOT NULL,
                device_id character varying(16) NOT NULL,
                name text NOT NULL,
                value text NOT NULL,
                priority integer NOT NULL DEFAULT 0,
                updated_at timestamp with time zone NOT NULL DEFAULT NOW(),
                PRIMARY KEY (id),
                CONSTRAINT unique_device_name UNIQUE (device_id, name)
            );
        """
    )
    conn.execute(
        """
            CREATE TABLE IF NOT EXISTS scrape_stats
            (
                id serial NOT NULL,
                name text NOT NULL,
                value text NOT NULL,
                priority integer NOT NULL DEFAULT 0,
                updated_at timestamp with time zone NOT NULL DEFAULT NOW(),
                PRIMARY KEY (id),
                CONSTRAINT unique_name UNIQUE (name)
            );
        """
    )

    logger.info(f"Creating indexes")
    conn.execute(
        """
            CREATE INDEX IF NOT EXISTS updated_at
            ON public.scrapes USING btree
            (updated_at ASC NULLS LAST);
        """
    )
    conn.execute(
        """
            CREATE INDEX IF NOT EXISTS scraped_at
            ON public.scrapes USING btree
            (scraped_at DESC NULLS FIRST, deveui ASC NULLS LAST);
        """
    )
    conn.execute(
        """
            CREATE INDEX IF NOT EXISTS deveui
            ON public.scrapes USING btree
            (deveui ASC NULLS LAST);
        """
    )
    conn.execute(
        """
            CREATE INDEX IF NOT EXISTS scraped_at_clustered
            ON public.scrapes USING btree
            (scraped_at DESC NULLS FIRST);

            ALTER TABLE IF EXISTS public.scrapes
            CLUSTER ON scraped_at_clustered;
        """
    )

    logger.info("Creating user(s)")
    conn.execute(
        """
            DO $$
            BEGIN
                IF NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'readaccess') THEN
                    CREATE ROLE readaccess;
                END IF;
            END $$;

            DO $$
            BEGIN
                IF NOT EXISTS (
                    SELECT 1 
                    FROM information_schema.role_table_grants 
                    WHERE grantee = 'readaccess' 
                    AND privilege_type = 'SELECT'
                    AND table_schema = 'public'
                ) THEN
                    GRANT USAGE ON SCHEMA public TO readaccess;
                    GRANT SELECT ON ALL TABLES IN SCHEMA public TO readaccess;
                    ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT SELECT ON TABLES TO readaccess;
                END IF;
            END $$;
        """
    )
    conn.execute(
        f"""
            DO $$
            BEGIN
                IF NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'read_only') THEN
                    CREATE USER read_only WITH PASSWORD '{DB_PASSWORD}';
                    GRANT readaccess TO read_only;
                END IF;
            END $$;
        """
    )

    count = conn.execute("SELECT COUNT(*) FROM devices").fetchone()[0]
    if count == 0:
        logger.info("No devices found, importing from csv")
        count = 0
        with open("./devs.csv", "r") as file:
            reader = csv.DictReader(file)
            cursor = conn.cursor()
            with cursor.copy(
                "COPY devices (name, hashedname, deveui) FROM STDIN"
            ) as copy:
                for d in reader:
                    copy.write_row(list(d.values()))
                    count += 1
            conn.commit()
            cursor.close()
        logger.info(f"Imported {count} device(s)")

    conn.commit()
    conn.close()


def get_db() -> psycopg.Connection:
    conn = psycopg.connect(
        user=DB_USER,
        password=DB_PASSWORD,
        host=DB_HOST,
        port=DB_PORT,
        dbname=DB_DATABASE,
        row_factory=psycopg.rows.dict_row,
        autocommit=True,
    )
    conn.execute(f"SET timezone TO '{TIMEZONE}'")
    return conn
