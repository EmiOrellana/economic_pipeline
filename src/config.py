import os
from dotenv import load_dotenv


load_dotenv()

FRED_API_KEY = os.getenv('FRED_API_KEY')
ALPHA_VANTAGE_API_KEY = os.getenv('ALPHA_VANTAGE_API_KEY')

INDICATORS = [
    {'indicator_symbol': 'FEDFUNDS', 'indicator_name': 'Federal Funds Rate', 'indicator_source': 'FRED',
     'indicator_unit': 'Percent', 'category': 'macro', 'frequency': 'monthly'},
    {'indicator_symbol': 'UNRATE', 'indicator_name': 'Unemployment Rate', 'indicator_source': 'FRED',
     'indicator_unit': 'Percent', 'category': 'macro', 'frequency': 'monthly'},
    {'indicator_symbol': 'CPIAUCSL', 'indicator_name': 'Consumer Price Index for All Urban Consumers: All Items', 'indicator_source': 'FRED',
     'indicator_unit': 'Index', 'category': 'macro', 'frequency': 'monthly'},
    {'indicator_symbol': 'SP500', 'indicator_name': 'S&P 500 Index', 'indicator_source': 'FRED',
     'indicator_unit': 'Index', 'category': 'financial', 'frequency': 'business_daily'},
    {'indicator_symbol': 'GDPC1', 'indicator_name': 'Real Gross Domestic Product', 'indicator_source': 'FRED',
     'indicator_unit': 'Billion of Chained 2017 Dollars', 'category': 'macro', 'frequency': 'quarterly'},
    {'indicator_symbol': 'NASDAQCOM', 'indicator_name': 'NASDAQ Composite Index', 'indicator_source': 'FRED',
     'indicator_unit': 'Index', 'category': 'financial', 'frequency': 'business_daily'},
    {'indicator_symbol': 'WTI', 'indicator_name': 'West Texas Intermediate Crude Oil', 'indicator_source': 'ALPHA_VANTAGE',
     'indicator_unit': 'USD per Barrel', 'category': 'commodity', 'frequency': 'business_daily'},
    {'indicator_symbol': 'BRENT', 'indicator_name': 'Brent Crude Oil', 'indicator_source': 'ALPHA_VANTAGE',
     'indicator_unit': 'USD per Barrel', 'category': 'commodity', 'frequency': 'business_daily'},
    {'indicator_symbol': 'NATURAL_GAS', 'indicator_name': 'Natural Gas', 'indicator_source': 'ALPHA_VANTAGE',
     'indicator_unit': 'USD per MMBtu', 'category': 'commodity', 'frequency': 'business_daily'},
    {'indicator_symbol': 'WHEAT', 'indicator_name': 'Wheat', 'indicator_source': 'ALPHA_VANTAGE',
     'indicator_unit': 'USD per Metric Ton', 'category': 'commodity', 'frequency': 'monthly'},
    {'indicator_symbol': 'CORN', 'indicator_name': 'Corn', 'indicator_source': 'ALPHA_VANTAGE',
     'indicator_unit': 'USD per Metric Ton', 'category': 'commodity', 'frequency': 'monthly'},
    {'indicator_symbol': 'GOLD_SILVER_HISTORY', 'symbol': 'GOLD', 'indicator_name': 'Gold', 'indicator_source': 'ALPHA_VANTAGE',
     'indicator_unit': 'USD per Ounce', 'category': 'commodity', 'frequency': 'daily'},
    {'indicator_symbol': 'GOLD_SILVER_HISTORY', 'symbol': 'SILVER', 'indicator_name': 'Silver', 'indicator_source': 'ALPHA_VANTAGE',
     'indicator_unit': 'USD per Ounce', 'category': 'commodity', 'frequency': 'daily'},
]

DB_CONFIG = {
    'host': os.getenv('DB_HOST'),
    'port': os.getenv('DB_PORT'),
    'database': os.getenv('DB_NAME'),
    'user': os.getenv('DB_USER'),
    'password': os.getenv('DB_PASSWORD')
}