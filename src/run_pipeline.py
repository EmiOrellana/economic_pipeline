import logging
import pandas as pd
from time import sleep
from src.config import DB_CONFIG
from src.config import INDICATORS
from src.extract.fred import get_fred_data
from src.extract.alpha_vantage import get_commodities, get_gold_silver
from src.load.load import load_indicators, get_indicator_id, load_observations
from src.transform.transform import transform_fred_data, transform_alpha_vantage_data
from src.db.connection import get_db_connection


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def get_transformed_data(indicator: dict) -> pd.DataFrame | None:

    """
    Fetch and transform data based on the indicator source and symbol.

    Returns the transformed data or None if the transformation fails.
    """

    source = indicator["indicator_source"]
    symbol = indicator["indicator_symbol"]

    if source == "FRED":
        raw_data = get_fred_data(symbol)
        return transform_fred_data(raw_data)

    elif source == "ALPHA_VANTAGE":
        if symbol == "GOLD_SILVER_HISTORY":
            raw_data = get_gold_silver(indicator["symbol"])
        else:
            raw_data = get_commodities(symbol)
        return transform_alpha_vantage_data(raw_data)

    else:
        logger.warning(
            "Unknown data source for indicator %s: %s",
            symbol,
            source
        )
        return None


def run_pipeline():
    logger.info("Starting the pipeline...")
    conn = None

    try:
        conn = get_db_connection(DB_CONFIG)
        with conn:
            load_indicators(conn, INDICATORS)

        for i, indicator in enumerate(INDICATORS):
            symbol = indicator["indicator_symbol"]
            name = indicator["indicator_name"]
            logger.info("Processing indicator: %s (%s)", 
                        name, 
                        symbol)

            # Fetch and transform data (no DB interaction, outside transaction)
            transformed_data = get_transformed_data(indicator)

            if transformed_data is None:
                logger.warning("No data to load for %s. Skipping.", symbol)
                continue

            # Atomic transaction per indicator:
            # get_indicator_id + load_observations succeed together or rollback together
            try:
                with conn:
                    indicator_id = get_indicator_id(conn, name)
                    load_observations(conn, indicator_id, transformed_data)
                logger.info(
                    "Loaded observations for %s into the database.", symbol
                )

            except Exception as e:
                # The context manager already did rollback.
                # Log and continue with the next indicator.
                logger.error(
                    "Failed to load observations for %s: %s",
                    symbol,
                    e,
                )

            if i > 0:
                logger.info(
                    "Sleeping for 0.5 second to respect API rate limits..."
                )
                sleep(0.5)

    except Exception as e:
        logger.error("Pipeline error: %s", e, exc_info=True)

    finally:
        if conn:
            conn.close()


if __name__ == "__main__":
    run_pipeline()
