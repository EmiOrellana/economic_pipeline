import pandas as pd


def to_base_100(df: pd.DataFrame, value_col: str = 'value') -> pd.DataFrame:

    """
    Transforms the values in the specified column of the DataFrame to a base 100 index.
    
    Parameters:
    df (pandas.DataFrame): The input DataFrame containing the data to be transformed.
    value_col (str): The name of the column containing the values to be transformed. Default is 'value'.
    
    Returns:
    pandas.DataFrame: A new DataFrame with the transformed values in a column named 'base_100_value'.
    """

    if df.empty:
        return df
    
    df = df.copy()
    
    first_values = df.groupby('indicator_name')[value_col].transform('first')
    if any(first_values == 0):
        raise ValueError("The base value for index calculation cannot be zero.")

    df['base_100_value'] = df.groupby('indicator_name')[value_col].transform(lambda x: (x / x.iloc[0]) * 100)

    return df


def to_pct_change(df: pd.DataFrame, value_col: str = 'value') -> pd.DataFrame:

    """
    Transforms the values in the specified column of the DataFrame to percentage change.
    
    Parameters:
    df (pandas.DataFrame): The input DataFrame containing the data to be transformed.
    value_col (str): The name of the column containing the values to be transformed. Default is 'value'.
    
    Returns:
    pandas.DataFrame: A new DataFrame with the transformed values in a column named 'pct_change_value'.
    """

    if df.empty:
        return df

    df = df.copy()

    df['pct_change_value'] = df.groupby('indicator_name')[value_col].transform(lambda x: x.pct_change() * 100)

    return df


def to_resample(df: pd.DataFrame, interval: str, value_col: str = 'value') -> pd.DataFrame:

    """
    Resamples the DataFrame to the specified interval and calculates the last value.

    Parameters:
    interval (str): The resampling interval (e.g., 'ME' for monthly, 'QE' for quarterly, 'YE' for yearly).

    Returns:
    pandas.DataFrame: A DataFrame that contains the resampled values for each indicator.
    """


    if df.empty:
        return df

    df = df.copy()
    df['date'] = pd.to_datetime(df['date'])
    df.set_index('date', inplace=True)
    resampled_df = df.groupby(['indicator_symbol', 'indicator_name', 'indicator_unit', 'display_unit']).resample(interval)[value_col].last().reset_index()

    return resampled_df

