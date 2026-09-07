import pandas as pd
import streamlit as st
from datetime import date
import plotly.express as px

from src.app.queries import get_indicators, get_observations
from src.app.transforms import to_base_100


GRAIN_VALUES = {"Daily": "day", "Monthly": "month",
                "Quarterly": "quarter", "Yearly": "year"}

METRICS = {
    "Absolute values": "value",
    "Base 100": "base_100_value",
    "Change vs previous period (%)": "pop_pct",
    "Change vs previous period": "pop_change",
    "Year-over-year (%)": "yoy_pct",
    "Year-over-year": "yoy_change",
}


st.set_page_config(
    page_title="Economic Indicators Dashboard",
    page_icon="📈",
    layout="wide"
)

st.title("Economic Indicators Dashboard")
st.write("Use the sidebar to select indicators, time interval and date range, and view the corresponding observations in the main area.")
st.write("This project tracks key macroeconomic and financial indicators sourced from FRED and Alpha Vantage APIs, stored in a PostgreSQL database and updated automatically via a scheduled ETL pipeline.")

st.sidebar.subheader("Filters")
try:
    indicators_query = get_indicators()
except Exception:
    st.error("Could not reach the database. Please try again in a moment.")
    st.stop()

indicator_options = st.sidebar.multiselect(
    "Select indicators", 
    options=indicators_query.to_dict('records'), 
    format_func=lambda x: f"{x['category']} · {x['indicator_name']} ({x['indicator_unit']})",
    help="Choose one or more indicators to display"
)

start_date = st.sidebar.date_input("Start date", value=date(2010, 1, 1), help="Select the start date for the observations", min_value=date(1900, 1, 1), max_value=date.today())
end_date = st.sidebar.date_input("End date", value=date.today(), help="Select the end date for the observations", min_value=date(1900, 1, 1), max_value=date.today())

if indicator_options:
    available = set.intersection(*(set(i["available_grains"]) for i in indicator_options))
else:
    available = set(GRAIN_VALUES.values())

grain_options = [label for label, value in GRAIN_VALUES.items() if value in available]

st.sidebar.subheader("Resampling")
resample_interval = st.sidebar.radio(
    "Resample interval",
    options=grain_options,
    help="Select the resampling interval"
)

grain = GRAIN_VALUES[resample_interval]

metric_options = [
    label for label, column in METRICS.items()
    if not (grain == "day" and column.startswith("yoy_"))
]

st.sidebar.subheader("Transformations")
transformation = st.sidebar.radio(
    "Transformation",
    options=metric_options,
    help="Select the transformation to apply to the data"
)

value_col = METRICS[transformation]

if not indicator_options:
    st.info("Select at least one indicator to display the charts.")
else:
    indicator_ids = [indicator['indicator_id'] for indicator in indicator_options]
    try:
        df = get_observations(grain, indicator_ids, start_date, end_date)
    except Exception:
        st.error("Could not retrieve the data. Please try again in a moment.")
        st.stop()
    df['display_unit'] = df['indicator_unit']  # Add display_unit column for hover info

    if df.empty:
        st.warning("No data found for the selected indicators and date range.")
        st.stop()

    if transformation == "Base 100":
        common_start = max(i["start_date"] for i in indicator_options)
        base_date = max(pd.Timestamp(start_date), pd.Timestamp(common_start))
        df = df[df["observation_date"] >= base_date]
        df = to_base_100(df, base_date)
        if base_date > pd.Timestamp(start_date):
            st.caption(f"Rebased to {base_date.date()}, the earliest date shared by all selected series.")

    if value_col.endswith("_pct"):
        df['display_unit'] = "% change"
    elif value_col == "base_100_value":
        df['display_unit'] = "Base 100 index"
    elif value_col.endswith("_change"):
        df['display_unit'] = df['indicator_unit'].where(
            df['indicator_unit'] != 'Percent', 'percentage points'
        )

    if (value_col == "value" or value_col.endswith("_change")) and df['indicator_unit'].nunique() > 1:
        st.warning(
            "The selected indicators are measured in different units, so their "
            "levels are not directly comparable. Use Base 100 or a percentage "
            "metric to compare them on the same scale."
        )

    chart_title = f"Economic Indicators — {transformation} ({resample_interval})"

    y_label = df['display_unit'].iloc[0] if len(df['display_unit'].unique()) == 1 else 'Value'

    fig = px.line(
        df, 
        x='observation_date', 
        y=value_col, 
        color='indicator_name', 
        title=chart_title,
        hover_data=['display_unit'],
        labels={value_col: y_label, 'observation_date': "Date", 'indicator_name': "Indicator", 'display_unit': "Unit"}
    )

    fig.update_traces(hovertemplate='<b>%{fullData.name}</b><br>Date: %{x}<br>Value: %{y:.2f} %{customdata[0]}<extra></extra>')

    st.plotly_chart(fig, use_container_width=True)