import logging
import psycopg2

import streamlit as st
import pandas as pd

from src.db.connection import get_db_connection
from src.config import DB_CONFIG


logger = logging.getLogger(__name__)

GET_INDICATORS_QUERY = """
SELECT 
    indicator_id, 
    indicator_name, 
    indicator_unit, 
    category, 
    frequency, 
    start_date, 
    end_date,
    available_grains 
FROM analytics.mart_indicators
ORDER BY category, indicator_name;
"""

GET_OBSERVATIONS_QUERY = """
SELECT 
    observation_date, 
    indicator_name, 
    indicator_unit,
    value, 
    pop_change, 
    pop_pct, 
    yoy_change, 
    yoy_pct
FROM analytics.mart_observations
WHERE grain = %s
    AND indicator_id = ANY(%s)
    AND observation_date BETWEEN %s AND %s
ORDER BY observation_date;
"""

@st.cache_resource
def _get_cached_connection():

    """
    Returns the cached connection, in autocommit mode.

    Without autocommit, psycopg2 opens a transaction on the first read and nothing
    closes it: the cached connection then sits idle in transaction, holding a lock on
    the marts that blocks dbt from swapping the tables during a build.
    """

    conn = get_db_connection(DB_CONFIG)
    conn.autocommit = True
    return conn


def _discard_connection(conn) -> None:

    """
    Leaves the cached connection usable after a failed query.

    A failed statement aborts the transaction, so the connection rejects every
    later query until it is rolled back. If it dropped altogether, the cached
    object is dead and has to be discarded so the next call reconnects.
    """

    if conn is None:
        return

    if conn.closed:
        _get_cached_connection.clear()
        return

    try:
        conn.rollback()
    except psycopg2.Error:
        _get_cached_connection.clear()


@st.cache_data(ttl=3600)
def get_indicators() -> pd.DataFrame:

    """
    Retrieves all indicators from the database.
    """

    conn = None

    try:
        conn = _get_cached_connection()
        with conn.cursor() as cursor:
            cursor.execute(GET_INDICATORS_QUERY)
            data = cursor.fetchall()
            return pd.DataFrame(data, columns=[desc[0] for desc in cursor.description])
        
    except psycopg2.Error as e:
        logger.error("Error retrieving indicators: %s", e)
        _discard_connection(conn)
        raise


@st.cache_data(ttl=3600)
def get_observations(grain: str, indicator_ids: list[int], start_date: str, end_date: str) -> pd.DataFrame:
    
    """
    Retrieves observations for the specified date range and indicator IDs from the database.
    """

    conn = None

    try:
        conn = _get_cached_connection()
        with conn.cursor() as cursor:
            cursor.execute(GET_OBSERVATIONS_QUERY, (grain, indicator_ids, start_date, end_date))
            data = cursor.fetchall()
            df = pd.DataFrame(data, columns=[desc[0] for desc in cursor.description])

            numeric_columns = ["value", "pop_change", "pop_pct", "yoy_change", "yoy_pct"]
            df["observation_date"] = pd.to_datetime(df["observation_date"])
            df[numeric_columns] = df[numeric_columns].astype(float)

            return df
        
    except psycopg2.Error as e:
        logger.error("Error retrieving observations: %s", e)
        _discard_connection(conn)
        raise