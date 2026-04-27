import logging
import psycopg2
import pandas as pd
from src.db.connection import get_db_connection
from src.config import DB_CONFIG


logger = logging.getLogger(__name__)

GET_INDICATORS_QUERY = """
SELECT * 
FROM indicators
ORDER BY indicator_name;
"""

GET_OBSERVATIONS_QUERY = """
SELECT o.date, i.indicator_symbol, i.indicator_name, i.indicator_unit, o.value
FROM observations o
JOIN indicators i ON o.indicator_id = i.indicator_id
WHERE
    o.date >= %s AND o.date <= %s
    AND
    i.indicator_id = ANY(%s)
ORDER BY o.date;
"""


def get_indicators() -> pd.DataFrame:

    """
    Retrieves all indicators from the database.
    """

    conn = None

    try:
        conn = get_db_connection(DB_CONFIG)
        with conn.cursor() as cursor:
            cursor.execute(GET_INDICATORS_QUERY)
            data = cursor.fetchall()
            return pd.DataFrame(data, columns=[desc[0] for desc in cursor.description])
        
    except psycopg2.DatabaseError as e:
        logger.error("Error retrieving indicators: %s"  , e)
        return pd.DataFrame(columns=["indicator_id", "indicator_name", "indicator_symbol"])
    
    finally:
        if conn:
            conn.close()


def get_observations(start_date: str, end_date: str, indicator_ids: list[int]) -> pd.DataFrame:
    
    """
    Retrieves observations for the specified date range and indicator IDs from the database.
    """

    conn = None

    try:
        conn = get_db_connection(DB_CONFIG)
        with conn.cursor() as cursor:
            cursor.execute(GET_OBSERVATIONS_QUERY, (start_date, end_date, indicator_ids))
            data = cursor.fetchall()
            return pd.DataFrame(data, columns=[desc[0] for desc in cursor.description])
        
    except psycopg2.DatabaseError as e:
        logger.error("Error retrieving observations: %s", e)
        return pd.DataFrame(columns=["date", "indicator_symbol", "indicator_name", "indicator_unit", "value"])

    finally:
        if conn:
            conn.close()