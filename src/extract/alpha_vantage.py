import logging
import os
import requests
import json
import time
from src.config import ALPHA_VANTAGE_API_KEY


logger = logging.getLogger(__name__)
url = 'https://www.alphavantage.co/query'


def get_commodities(function: str, interval: str = 'daily') -> dict | None:

    """
    Fetch data from the Alpha Vantage API for a specific series ID.
    Uses local cache if available, otherwise makes an API request and saves the response to a local file.

    Args:
        series_id (str): The ID of the Alpha Vantage series to fetch.
        observation_start (str): The start date for observations in 'YYYY-MM-DD' format. Default is '2010-01-01'.

    Returns:
        dict | None: The JSON response from the Alpha Vantage API as a dictionary, or None if an error occurs.
    """

    path = f'data/raw/alpha_vantage/{function}.json'
    os.makedirs(os.path.dirname(path), exist_ok=True)

    if os.path.exists(path) and time.time() - os.path.getmtime(path) < 86400:
        logger.info(f"Using cached data for: {function}")
        with open(path, 'r') as file:
            return json.load(file)

    params = {
        'function': function,
        'interval': interval,
        'datatype': 'json',
        'apikey': ALPHA_VANTAGE_API_KEY
    }

    try:
        response = requests.get(url, params=params)
        response.raise_for_status()

    except requests.exceptions.RequestException as e:
        logger.error(f"Error fetching data from Alpha Vantage API: {e}")
        return None

    raw_data = response.json()

    with open(path, 'w') as file:
        json.dump(raw_data, file)
        logger.info(f"Imported data for: {function}")

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
        logger.info(f"Using cached data for: {symbol} HISTORY")
        with open(path, 'r') as file:
            return json.load(file)
        
    params = {
        'function': 'GOLD_SILVER_HISTORY',
        'symbol': symbol,
        'interval': interval,
        'apikey': ALPHA_VANTAGE_API_KEY
    }

    try:
        response = requests.get(url, params=params)
        response.raise_for_status()

    except requests.exceptions.RequestException as e:
        logger.error(f"Error fetching data from Alpha Vantage API: {e}")
        return None
    
    raw_data = response.json()

    with open(path, 'w') as file:
        json.dump(raw_data, file)
        logger.info(f"Imported data for: {symbol} SPOT")

    return raw_data
