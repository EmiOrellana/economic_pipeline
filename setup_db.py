import logging

from pathlib import Path

from src.db.connection import get_db_connection
from src.config import DB_CONFIG

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

SCHEMA_PATH = Path(__file__).resolve().parent / 'sql' / 'schema.sql'

conn = None
try:
    conn = get_db_connection(DB_CONFIG)
    with conn:
        with conn.cursor() as cursor:
            with open(SCHEMA_PATH, 'r') as file:
                schema_sql = file.read()
            cursor.execute(schema_sql)
    logger.info("Database schema created successfully.")

except Exception as e:
    logger.error("Error creating database schema: %s", e, exc_info=True)
    raise

finally:
    if conn:
        conn.close()