import logging
import pandas as pd
import psycopg2


logger = logging.getLogger(__name__)

UPSERT_INDICATOR_QUERY = """
INSERT INTO indicators (indicator_symbol, indicator_name, indicator_source, indicator_unit)
VALUES (%s, %s, %s, %s)
ON CONFLICT (indicator_symbol, indicator_name)
DO UPDATE SET
    indicator_source = EXCLUDED.indicator_source,
    indicator_unit = EXCLUDED.indicator_unit;
"""

UPSERT_OBSERVATION_QUERY = """
INSERT INTO observations (date, indicator_id, value)
VALUES (%s, %s, %s)
ON CONFLICT (date, indicator_id)
DO UPDATE SET 
    value = EXCLUDED.value;
"""


def load_indicators(conn, indicators: list) -> None:

    """
    Loads indicator metadata into the database. Uses an upsert strategy to avoid duplicates based on the indicator_symbol.
    Caller function is responsible for creating the connection and committing the transaction after calling this function.

    Args:
        conn: A psycopg2 database connection object.
        indicators: A list of indicator metadata dictionaries to be loaded.
    """

    records = [
        (
            indicator["indicator_symbol"],
            indicator["indicator_name"],
            indicator["indicator_source"],
            indicator["indicator_unit"]
        ) 
        for indicator in indicators
    ]

    try:
        with conn.cursor() as cursor:
            cursor.executemany(UPSERT_INDICATOR_QUERY, records)

    except psycopg2.DatabaseError as e:
        logger.error("Error loading indicators: %s", e)
        raise


def get_indicator_id(conn, indicator_name) -> int | None:

    """
    Retrieves the ID of an indicator from the database based on its symbol.
    Args:
        conn: A psycopg2 database connection object.
        indicator_symbol: The symbol of the indicator for which the ID is being retrieved.

    Returns:
        The ID of the indicator, or None if not found.
    """

    try:
        with conn.cursor() as cursor:
            cursor.execute(
                "SELECT indicator_id FROM indicators WHERE indicator_name = %s", 
                (indicator_name,)
            )

            result = cursor.fetchone()
            
            return result[0] if result else None
        
    except psycopg2.DatabaseError as e:
        logger.error("Error retrieving indicator ID: %s", e)
        raise


def load_observations(conn, indicator_id: int, df: pd.DataFrame) -> None:

    """
    Loads indicator observations into the database. Uses an upsert strategy to avoid duplicates based on the combination of date and indicator_id.
    Caller function is responsible for creating the connection and committing the transaction after calling this function.

    Args:
        conn: A psycopg2 database connection object.
        indicator_id: The ID of the indicator for which observations are being loaded.
        df: A pandas DataFrame containing the observations to be loaded. Must have 'date' and 'value' columns.
    """

    required_columns = {"date", "value"}
    missing_columns = required_columns - set(df.columns)

    if missing_columns:
        raise ValueError(f"DataFrame is missing required columns: {missing_columns}")
    
    if df.empty:
        logger.warning("No observations to load for indicator_id %s", indicator_id)
        return

    records = [
        (row.date, indicator_id, row.value) 
        for row in df.itertuples(index=False)
    ]

    try:
        with conn.cursor() as cursor:
            cursor.executemany(UPSERT_OBSERVATION_QUERY, records)

    except psycopg2.DatabaseError as e:
        logger.error("Error loading observations: %s", e)
        raise

