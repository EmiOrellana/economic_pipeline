import logging
import os
import requests
import json
import time
from src.config import FRED_API_KEY, MAX_ATTEMPTS, RETRY_DELAY_SECONDS


logger = logging.getLogger(__name__)
url = 'https://api.stlouisfed.org/fred/series/observations'


def get_fred_data(series_id: str, observation_start: str = '1776-07-04') -> dict | None:

    """
    Fetch data from the FRED API for a specific series ID.
    Uses local cache if available, otherwise makes an API request and saves the response to a local file.

    Args:
        series_id (str): The ID of the FRED series to fetch.
        observation_start (str): The start date for observations in 'YYYY-MM-DD' format. Default is '1776-07-04', which effectively fetches the full available history.

    Returns:
        dict | None: The JSON response from the FRED API as a dictionary, or None if an error occurs.
    """
    
    path = f'data/raw/fred/{series_id}.json'
    os.makedirs(os.path.dirname(path), exist_ok=True)

    if os.path.exists(path) and time.time() - os.path.getmtime(path) < 86400:
        logger.info("Using cached data for series_id: %s", series_id)
        with open(path, 'r') as file:
            return json.load(file)

    params = {
        'series_id': series_id,
        'api_key': FRED_API_KEY,
        'file_type': 'json',
        'observation_start': observation_start
    }

    for attempt in range(1, MAX_ATTEMPTS + 1):
        try:
            response = requests.get(url, params=params)
            response.raise_for_status()
            break

        except requests.exceptions.RequestException as e:
            # A 4xx other than 429 is our fault, not a hiccup: retrying changes nothing.
            failed = e.response
            if failed is not None and failed.status_code < 500 and failed.status_code != 429:
                logger.error("Error fetching data from FRED API: %s", e)
                return None

            if attempt == MAX_ATTEMPTS:
                logger.error(
                    "Error fetching data from FRED API after %s attempts: %s",
                    MAX_ATTEMPTS,
                    e
                )
                return None

            logger.warning(
                "Attempt %s of %s failed for series_id %s, retrying in %ss: %s",
                attempt,
                MAX_ATTEMPTS,
                series_id,
                RETRY_DELAY_SECONDS,
                e
            )
            time.sleep(RETRY_DELAY_SECONDS)
    
    raw_data = response.json()

    with open(path, 'w') as file:
        json.dump(raw_data, file)
        logger.info("Imported data for series_id: %s", series_id)

    return raw_data
