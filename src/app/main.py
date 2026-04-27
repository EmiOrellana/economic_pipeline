import pandas as pd
import streamlit as st
from datetime import date
import plotly.express as px
from src.app.queries import get_indicators, get_observations
from src.app.transforms import to_base_100, to_pct_change, to_resample

st.set_page_config(
    page_title="Economic Indicators Dashboard",
    page_icon="📈",
    layout="wide"
)

st.title("Economic Indicators Dashboard")
st.write("Use the sidebar to select indicators, time interval and date range, and view the corresponding observations in the main area.")
st.write("This project tracks key macroeconomic and financial indicators sourced from FRED and Alpha Vantage APIs, stored in a PostgreSQL database and updated automatically via a scheduled ETL pipeline.")

st.sidebar.subheader("Filters")
indicators_query = get_indicators()

indicator_options = st.sidebar.multiselect(
    "Select indicators", 
    options=indicators_query.to_dict('records'), 
    format_func=lambda x: f"{x['indicator_name']} ({x['indicator_unit']})",
    help="Choose one or more indicators to display"
)

start_date = st.sidebar.date_input("Start date", value=date(2010, 1, 1), help="Select the start date for the observations", min_value=date(1900, 1, 1), max_value=date.today())
end_date = st.sidebar.date_input("End date", value=date.today(), help="Select the end date for the observations", min_value=date(1900, 1, 1), max_value=date.today())

st.sidebar.subheader("Transformations")
transformation = st.sidebar.radio(
    "Transformation",
    options=["Absolute values", "Base 100", "Percentage change"],
    help="Select the transformation to apply to the data"
)

st.sidebar.subheader("Resampling")
resample_interval = st.sidebar.radio(
    "Resample interval",
    options=["Daily", "Monthly", "Quarterly", "Yearly"],
    help="Select the resampling interval"
)

if not indicator_options:
    st.info("Select at least one indicator to display the charts.")
else:
    indicator_ids = [indicator['indicator_id'] for indicator in indicator_options]
    df = get_observations(start_date, end_date, indicator_ids)
    df['display_unit'] = df['indicator_unit']  # Add display_unit column for hover info

    if df.empty:
        st.warning("No data found for the selected indicators and date range.")
        st.stop()
        
    value_col = 'value'

    if resample_interval != "Daily":
        interval_map = {
            "Monthly": 'ME',
            "Quarterly": 'QE',
            "Yearly": 'YE'
        }
        df = to_resample(df, interval_map[resample_interval], 'value')

    if transformation == "Base 100":
        df = to_base_100(df)
        value_col = 'base_100_value'

    elif transformation == "Percentage change":
        df = to_pct_change(df)
        value_col = 'pct_change_value'

    units = df['indicator_unit'].unique()

    chart_title = f"Economic Indicators — {transformation} ({resample_interval})"

    if transformation == "Absolute values" and len(df['indicator_unit'].unique()) > 1:
        st.warning("The selected indicators have different units. Consider using Base 100 or Percentage change for better comparison.")
    elif transformation == "Base 100":
        df['display_unit'] = 'Base 100 index'
    elif transformation == "Percentage change":
        df['display_unit'] = '% Change'

    y_label = df['display_unit'].iloc[0] if len(df['display_unit'].unique()) == 1 else 'Value'

    fig = px.line(
        df, 
        x='date', 
        y=value_col, 
        color='indicator_name', 
        title=chart_title,
        hover_data=['display_unit'],
        labels={value_col: y_label, 'date': "Date", 'indicator_name': "Indicator", 'display_unit': "Unit"}
    )

    fig.update_traces(hovertemplate='<b>%{fullData.name}</b><br>Date: %{x}<br>Value: %{y:.2f} %{customdata[0]}<extra></extra>')

    st.plotly_chart(fig, use_container_width=True)