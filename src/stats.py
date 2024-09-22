import logging
from repository import get_db

logger = logging.getLogger(__name__)


def generate_stats():
    logger.info("generation stats...")
    db = get_db()

    q = """
        INSERT INTO scrape_stats (name, value, priority, updated_at)
        VALUES ('{n}', ({q}), {p}, NOW())
        ON CONFLICT (name)
        DO UPDATE SET
            value = EXCLUDED.value,
            updated_at = EXCLUDED.updated_at,
            priority = EXCLUDED.priority;
    """

    db.execute(
        q.format(
            n="database size",
            q=f"SELECT pg_size_pretty(pg_database_size('{db.info.dbname}'))",
            p=11,
        )
    )

    db.execute(
        q.format(
            n="scrape count",
            q="SELECT COUNT(id) FROM scrapes",
            p=12,
        )
    )

    db.execute(
        q.format(
            n="batch count",
            q="SELECT MAX(batch_id) from scrapes",
            p=13,
        )
    )

    db.execute(
        q.format(
            n="latest scrape",
            q="SELECT TO_CHAR(MAX(scraped_at), 'YYYY-MM-DD HH24:MI:SS') from scrapes",
            p=14,
        )
    )

    db.execute(
        q.format(
            n="device count",
            q="SELECT COUNT(*) FROM devices",
            p=15,
        )
    )

    db.execute(
        q.format(
            n="defect count",
            q="""
                SELECT COUNT(*) FROM device_analyses
                WHERE name = 'is_defect' and value = 'true'
            """,
            p=16,
        )
    )

    db.commit()
    db.close()
    logger.info("stats generated")
