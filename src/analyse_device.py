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
            p=10,
        )
    )
    db.execute(
        q.format(
            n="max_temp_24h",
            q=query_get_max_24h.format(t="temp"),
            p=10,
        )
    )
    db.execute(
        q.format(
            n="max_humidity_24h",
            q=query_get_max_24h.format(t="humi"),
            p=1000000,
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
            p=1000,
        )
    )
    logger.info("Making/updating materialized view")
    db.execute(
        """
            DO $$
            DECLARE
                cols text;
                query text;
            BEGIN
                SELECT string_agg(quote_ident(name) || ' text', ', ')
                INTO cols
                FROM (
                    SELECT name
                    FROM (SELECT DISTINCT name, priority FROM device_analyses) AS o
                    ORDER BY priority DESC
                ) AS o;
                
                BEGIN
                    EXECUTE 'DROP MATERIALIZED VIEW IF EXISTS device_analysis_summary';
                    query := format('
                        CREATE MATERIALIZED VIEW device_analysis_summary AS
                        SELECT *
                        FROM crosstab(
                            ''SELECT d.deveui, da.name, da.value
                            FROM devices d
                            LEFT JOIN device_analyses da ON d.deveui = da.device_id
                            ORDER BY d.deveui, da.name'',
                            ''SELECT name
                            FROM (SELECT DISTINCT name, priority FROM device_analyses) AS o
                            ORDER BY priority DESC''
                        ) AS ct(deveui text, %s);
                    ', cols);
                    EXECUTE query;
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
