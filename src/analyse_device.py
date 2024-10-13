import logging
from repository import get_db

logger = logging.getLogger(__name__)


def generate_analysis():
    logger.info("Making analysis...")
    db = get_db()

    q = """
        INSERT INTO device_analyses (device_id, name, value, priority, updated_at)
        SELECT
            d.deveui AS device_id,
            '{n}' AS name,
            d.v AS value,
            {p} as priority,
            NOW() as updated_at
        FROM (
            {q}
        ) AS d
        ON CONFLICT (device_id, name)
        DO UPDATE SET
            value = EXCLUDED.value,
            updated_at = EXCLUDED.updated_at,
            priority = EXCLUDED.priority;
    """
    query_get_max_24h = """
        SELECT
            max({t}) AS v,
            deveui
        FROM scrapes
        WHERE scraped_at > NOW() - interval '24h'
        GROUP BY deveui
    """
    db.execute(
        q.format(
            n="max_co2_24h",
            q=query_get_max_24h.format(t="co2"),
            p=12,
        )
    )
    db.execute(
        q.format(
            n="max_temp_24h",
            q=query_get_max_24h.format(t="temp"),
            p=13,
        )
    )
    db.execute(
        q.format(
            n="max_humidity_24h",
            q=query_get_max_24h.format(t="humi"),
            p=11,
        )
    )

    db.execute(
        q.format(
            n="is_defect",
            q="""
                SELECT
                    MAX(co2) = MIN(co2) and
                    MAX(temp) = MIN(temp) and
                    MAX(humi) = MIN(humi) as v,
                    deveui
                FROM scrapes
                GROUP BY deveui
            """,
            p=1_000_000,
        )
    )
    logger.info("Making/updating materialized view")
    db.execute(
        """
            DO $$
            DECLARE
                cols text;
                query1 text;
                query2 text;
            BEGIN
                SELECT string_agg(quote_ident(name) || ' text', ', ')
                INTO cols
                FROM (
                    SELECT name
                    FROM (SELECT DISTINCT name, priority FROM device_analyses) AS o
                    ORDER BY priority DESC
                ) AS o;

                BEGIN
                    DROP MATERIALIZED VIEW IF EXISTS device_analysis_summary;
                    query1 := format('
                        SELECT *
                        FROM crosstab(
                            ''SELECT d.deveui, da.name, da.value
                            FROM devices d
                            LEFT JOIN device_analyses da ON d.deveui = da.device_id
                            ORDER BY d.deveui, da.name'',
                            ''SELECT name
                            FROM (SELECT DISTINCT name, priority FROM device_analyses) AS o
                            ORDER BY priority DESC''
                        ) AS ct(deveui text, %s)
                    ', cols);
                    SELECT string_agg('ala.' || quote_ident(name), ', ')
                    INTO cols
                    FROM (
                        SELECT name
                        FROM (SELECT DISTINCT name, priority FROM device_analyses) AS o
                        ORDER BY priority DESC
                    ) AS o;
                    query2 := format('
                        CREATE MATERIALIZED VIEW device_analysis_summary AS
                        WITH LatestScrape AS (
                            SELECT
                                d.deveui,
                                MAX(s.scraped_at) AS latest_time_scraped
                            FROM
                                devices d
                                LEFT JOIN scrapes s ON d.deveui = s.deveui AND s.scraped_at >= NOW() - ''1 hour\''::INTERVAL
                            GROUP BY
                                d.deveui
                        ),
                        RankedScrapeData AS (
                            SELECT
                                d.deveui,
                                d.name,
                                d.hashedname,
                                COALESCE(s.temp, -1) AS temp,
                                COALESCE(s.co2, -1) AS co2,
                                COALESCE(s.humi, -1) AS humidity,
                                COALESCE(s.scraped_at, NOW()) AS scraped_at,
                                ROW_NUMBER() OVER (PARTITION BY d.deveui ORDER BY s.scraped_at DESC) AS rn
                            FROM
                                devices d
                                LEFT JOIN scrapes s ON d.deveui = s.deveui AND s.scraped_at = (SELECT latest_time_scraped FROM LatestScrape WHERE deveui = d.deveui)
                        ),
                        ala AS (
                            %s
                        )
                        SELECT
                            r.deveui,
                            name,
                            hashedname,
                            temp,
                            co2,
                            humidity,
                            %s
                        FROM
                            RankedScrapeData as r
                        JOIN ala on r.deveui = ala.deveui
                        WHERE
                            rn = 1;
                    ', query1, cols);
                    EXECUTE query2;
                EXCEPTION
                    WHEN OTHERS THEN
                        RAISE NOTICE 'Error creating materialized view: %', SQLERRM;
                        ROLLBACK;
                        RETURN;
                END;
            END $$;
        """
    )
    db.commit()
    db.close()
    logger.info("analysis are done")
