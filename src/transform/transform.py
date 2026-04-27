import logging
import pandas as pd


logger = logging.getLogger(__name__)


def transform_fred_data(raw_data: dict) -> pd.DataFrame | None:

    """
    Transforms raw FRED API data into a pandas DataFrame.

    Args:
        raw_data (dict): The raw JSON data returned by the FRED API.

    Returns:
        pd.DataFrame: A DataFrame containing the transformed FRED data.
        None: If the input data is None or invalid.
    """
    
    if raw_data is None:
        logger.error("No data to transform")
        return None
    
    try:
        df = pd.DataFrame(raw_data['observations'])
        df = df[['date', 'value']]
        df['date'] = pd.to_datetime(df['date'])
        df['value'] = pd.to_numeric(df['value'], errors='coerce')
        df['value'] = df['value'].ffill()

    except KeyError as e:
        logger.error("Unexpected data format, missing key: %s", e)
        return None
    
    except (ValueError, AttributeError) as e:
        logger.error("Error processing data: %s", e)
        return None

    logger.info("Transformed FRED data:\n%s", df.head())

    return df


def transform_alpha_vantage_data(raw_data: dict) -> pd.DataFrame | None:

    """
    Transforms raw Alpha Vantage API data into a pandas DataFrame.

    Args:
        raw_data (dict): The raw JSON data returned by the Alpha Vantage API.

    Returns:
        pd.DataFrame: A DataFrame containing the transformed Alpha Vantage data.
        None: If the input data is None or invalid.
    """
    
    if raw_data is None:
        logger.error("No data to transform")
        return None

    try:
        df = pd.DataFrame(raw_data['data'])

        if 'value' in df.columns:
            value_column = 'value'
        elif 'price' in df.columns:
            value_column = 'price'
        else:
            logger.error("Unexpected data format, missing 'value' or 'price' column")
            return None

        df = df[['date', value_column]].rename(columns={value_column: 'value'})

        df['date'] = pd.to_datetime(df['date'])
        df['value'] = pd.to_numeric(df['value'], errors='coerce')
        df['value'] = df['value'].ffill()

    except KeyError as e:
        logger.error("Unexpected data format, missing key: %s", e)
        return None

    except (ValueError, AttributeError) as e:
        logger.error("Error processing data: %s", e)
        return None
    
    logger.info("Transformed Alpha Vantage data:\n%s", df.head())

    return df

