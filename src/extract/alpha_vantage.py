import logging
import os
import requests
import json
import time

from src.config import ALPHA_VANTAGE_API_KEY


logger = logging.getLogger(__name__)
url = 'https://www.alphavantage.co/query'
MAX_ATTEMPTS = 3
RETRY_DELAY_SECONDS = 10


def _get_with_retry(params: dict, label: str) -> requests.Response | None:

    """
    Send the request and retry the failures that a retry can fix: 429, 5xx and
    connection errors. Any other 4xx is a bad request on our side and fails at once.

    Args:
        params (dict): The query string parameters for the Alpha Vantage request.
        label (str): The commodity or symbol being fetched, used for logging.

    Returns:
        requests.Response | None: The successful response, or None if every attempt failed.
    """

    for attempt in range(1, MAX_ATTEMPTS + 1):
        try:
            response = requests.get(url, params=params)
            response.raise_for_status()
            return response

        except requests.exceptions.RequestException as e:
            failed = e.response
            if failed is not None and failed.status_code < 500 and failed.status_code != 429:
                logger.error("Error fetching data from Alpha Vantage API: %s", e)
                return None

            if attempt == MAX_ATTEMPTS:
                logger.error(
                    "Error fetching data from Alpha Vantage API after %s attempts: %s",
                    MAX_ATTEMPTS,
                    e
                )
                return None

            logger.warning(
                "Attempt %s of %s failed for %s, retrying in %ss: %s",
                attempt,
                MAX_ATTEMPTS,
                label,
                RETRY_DELAY_SECONDS,
                e
            )
            time.sleep(RETRY_DELAY_SECONDS)


def get_commodities(function: str, interval: str = 'daily') -> dict | None:

    """
    Fetch commodity data from the Alpha Vantage API for a specific function.
    Uses local cache if available, otherwise makes an API request and saves the response to a local file.

    Args:
        function (str): The Alpha Vantage function to fetch (e.g. 'WTI', 'BRENT', 'CORN').
        interval (str): The time interval for the data (e.g. 'daily', 'weekly', 'monthly'). Default is 'daily'.

    Returns:
        dict | None: The JSON response from the Alpha Vantage API as a dictionary, or None if an error occurs.
    """

    path = f'data/raw/alpha_vantage/{function}.json'
    os.makedirs(os.path.dirname(path), exist_ok=True)

    if os.path.exists(path) and time.time() - os.path.getmtime(path) < 86400:
        logger.info("Using cached data for: %s", function)
        with open(path, 'r') as file:
            return json.load(file)

    params = {
        'function': function,
        'interval': interval,
        'datatype': 'json',
        'apikey': ALPHA_VANTAGE_API_KEY
    }

    logger.info("Sleeping for 15 seconds to respect API rate limits...")
    time.sleep(15)
    
    response = _get_with_retry(params, function)

    if response is None:
        return None

    raw_data = response.json()

    if 'data' not in raw_data:
        logger.error(
            "Alpha Vantage returned no data for %s: %s", function, raw_data
        )
        return None


    with open(path, 'w') as file:
        json.dump(raw_data, file)
        logger.info("Imported data for: %s", function)

    return raw_data


def get_gold_silver(symbol: str, interval: str = 'daily') -> dict | None:

    """
    Fetch gold or silver spot price data from the Alpha Vantage API.
    Uses local cache if available, otherwise makes an API request and saves the response to a local file.

    Args:
        symbol (str): The symbol for the commodity ('GOLD' or 'SILVER').
        interval (str): The time interval for the data (e.g., 'daily', 'weekly', 'monthly'). Default is 'daily'.

    Returns:
        dict | None: The JSON response from the Alpha Vantage API as a dictionary, or None if an error occurs.
    """

    path = f'data/raw/alpha_vantage/{symbol}_HISTORY.json'
    os.makedirs(os.path.dirname(path), exist_ok=True)

    if os.path.exists(path) and time.time() - os.path.getmtime(path) < 86400:
        logger.info("Using cached data for: %s HISTORY", symbol)
        with open(path, 'r') as file:
            return json.load(file)
        
    params = {
        'function': 'GOLD_SILVER_HISTORY',
        'symbol': symbol,
        'interval': interval,
        'apikey': ALPHA_VANTAGE_API_KEY
    }

    logger.info("Sleeping for 15 seconds to respect API rate limits...")
    time.sleep(15)

    response = _get_with_retry(params, symbol)

    if response is None:
        return None

    raw_data = response.json()

    if 'data' not in raw_data:
        logger.error(
            "Alpha Vantage returned no data for %s: %s", symbol, raw_data
        )
        return None
    
    with open(path, 'w') as file:
        json.dump(raw_data, file)
        logger.info("Imported data for: %s HISTORY", symbol)

    return raw_data
