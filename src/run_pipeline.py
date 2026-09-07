import logging
import pandas as pd

from src.config import DB_CONFIG
from src.config import INDICATORS
from src.extract.fred import get_fred_data
from src.extract.alpha_vantage import get_commodities, get_gold_silver
from src.load.load import load_indicators, get_indicator_id, load_observations
from src.parse.parse import parse_fred_data, parse_alpha_vantage_data
from src.db.connection import get_db_connection


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def _get_parsed_data(indicator: dict) -> pd.DataFrame | None:

    """
    Fetch and parse data based on the indicator source and symbol.

    Returns the parsed data or None if the parsing fails.
    """

    source = indicator["indicator_source"]
    symbol = indicator["indicator_symbol"]

    if source == "FRED":
        raw_data = get_fred_data(symbol)
        return parse_fred_data(raw_data)

    elif source == "ALPHA_VANTAGE":
        if symbol == "GOLD_SILVER_HISTORY":
            raw_data = get_gold_silver(indicator["symbol"])
        else:
            raw_data = get_commodities(symbol)
        return parse_alpha_vantage_data(raw_data)

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
    failed = []

    try:
        conn = get_db_connection(DB_CONFIG)
        with conn:
            load_indicators(conn, INDICATORS)

        for indicator in INDICATORS:
            symbol = indicator["indicator_symbol"]
            name = indicator["indicator_name"]
            logger.info("Processing indicator: %s (%s)", 
                        name, 
                        symbol)

            # Fetch and parse data (no DB interaction, outside transaction)
            parsed_data = _get_parsed_data(indicator)

            if parsed_data is None:
                failed.append(name)
                logger.warning(
                    "No data to load for %s (%s). Skipping.", 
                    name, 
                    symbol
                )
                continue

            # Atomic transaction per indicator:
            # get_indicator_id + load_observations succeed together or rollback together
            try:
                with conn:
                    indicator_id = get_indicator_id(conn, name)
                    load_observations(conn, indicator_id, parsed_data)
                logger.info(
                    "Loaded observations for %s (%s) into the database.", 
                    name, 
                    symbol
                )

            except Exception as e:
                # The context manager already did rollback.
                # Log, record the failure and continue with the next indicator.
                failed.append(name)
                logger.error(
                    "Failed to load observations for %s (%s) into the database: %s",
                    name,
                    symbol,
                    e,
                    exc_info=True
                )
                

    except Exception as e:
        logger.error("Pipeline error: %s", e, exc_info=True)
        raise

    finally:
        if conn:
            conn.close()

    if failed:
        raise RuntimeError(
            f"{len(failed)} indicators failed: {', '.join(failed)}"
        )


if __name__ == "__main__":
    run_pipeline()
