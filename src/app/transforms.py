import pandas as pd


def to_base_100(df: pd.DataFrame, base_date) -> pd.DataFrame:

    """
    Rebases every series to 100 at a single shared date.

    The base is the same date for all series in the chart, not each series' own
    first observation: two series starting at different times must not both be
    drawn from 100 as if they had started together. Where a series has no row on
    base_date, its first row after it is used, which costs at most a day.

    Parameters:
    df (pandas.DataFrame): observations, with observation_date, indicator_name
        and value columns.
    base_date: the date that becomes 100. Accepts anything pd.Timestamp reads.

    Returns:
    pandas.DataFrame: a copy with an added 'base_100_value' column. Series whose
        base value is zero come back as NA rather than raising.
    """

    if df.empty:
        return df

    df = df.copy()
    df = df.sort_values(by='observation_date')

    base_date = pd.Timestamp(base_date)
    base_values = (
        df[df['observation_date'] >= base_date]
        .groupby('indicator_name')['value']
        .first()
        .replace(0, pd.NA)
    )

    df['base_100_value'] = df['value'] / df['indicator_name'].map(base_values) * 100

    return df
