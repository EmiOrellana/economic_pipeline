import logging
import os
import requests
import json
from src.config import FRED_API_KEY


logger = logging.getLogger(__name__)
url = 'https://api.stlouisfed.org/fred/series/observations'


def get_fred_data(series_id: str, observation_start: str = '1776-07-04') -> dict | None:

    """
    Fetch data from the FRED API for a specific series ID.
    Uses local cache if available, otherwise makes an API request and saves the response to a local file.

    Args:
        series_id (str): The ID of the FRED series to fetch.
        observation_start (str): The start date for observations in 'YYYY-MM-DD' format. Default is '2010-01-01'.
    
    Returns:
        dict | None: The JSON response from the FRED API as a dictionary, or None if an error occurs.
    """
    
    path = f'data/raw/fred/{series_id}.json'
    os.makedirs(os.path.dirname(path), exist_ok=True)

    if os.path.exists(path):
        logger.info(f"Using cached data for series_id: {series_id}")
        with open(path, 'r') as file:
            return json.load(file)

    params = {
        'series_id': series_id,
        'api_key': FRED_API_KEY,
        'file_type': 'json',
        'observation_start': observation_start
    }

    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        
    except requests.exceptions.RequestException as e:
        logger.error(f"Error fetching data from FRED API: {e}")
        return None    
    
    raw_data = response.json()

    with open(path, 'w') as file:
        json.dump(raw_data, file)
        logger.info(f"Imported data for series_id: {series_id}")

    return raw_data
