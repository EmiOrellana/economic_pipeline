# Economic Indicators Dashboard

> **Portfolio Project** — A production-style data engineering project that tracks key macroeconomic and financial indicators through a fully automated ETL pipeline and an interactive dashboard.

---

## Overview

This project pulls data from two public financial APIs, processes and stores it in a relational database, and exposes it through an interactive web dashboard. The goal is to demonstrate a real-world data engineering workflow — from raw API responses to a queryable database to a visual interface.

**End-to-end flow:**

```
FRED API ──────────┐
                   ├──► ETL Pipeline (Python) ──► PostgreSQL ──► Streamlit Dashboard
Alpha Vantage API ─┘
```

The pipeline runs automatically every day at midnight via a Cron scheduler inside the Docker container, keeping the data fresh without manual intervention.

**Indicators tracked:**
| Symbol | Name | Source | Unit |
|---|---|---|---|
| FEDFUNDS | Federal Funds Rate | FRED | Percent |
| CPIAUCSL | Consumer Price Index | FRED | Index |
| SP500 | S&P 500 Index | FRED | Index |
| GDPC1 | Real GDP | FRED | Chained 2017 USD |
| WTI | West Texas Intermediate Crude Oil | Alpha Vantage | USD per Barrel |
| BRENT | Brent Crude Oil | Alpha Vantage | USD per Barrel |
| NATURAL_GAS | Natural Gas | Alpha Vantage | USD per MMBtu |
| WHEAT | Wheat | Alpha Vantage | USD per Bushel |
| CORN | Corn | Alpha Vantage | USD per Bushel |
| GOLD | Gold | Alpha Vantage | USD per Ounce |
| SILVER | Silver | Alpha Vantage | USD per Ounce |

---

## Tech Stack

- **Python** — ETL pipeline, data transformation, dashboard
- **PostgreSQL** — relational storage for indicators and observations
- **Streamlit** — interactive web dashboard
- **Plotly** — interactive charts
- **pandas** — data transformation
- **psycopg2** — PostgreSQL adapter
- **Docker & Docker Compose** — containerized deployment
- **Cron** — daily pipeline scheduling

---

## Project Architecture

```
economic_pipeline/
├── run_pipeline.py         # Pipeline entry point
├── setup_db.py             # Database schema setup
├── start.sh                # Container startup script
├── Dockerfile              # App container definition
├── docker-compose.yml      # Multi-container orchestration
├── crontab                 # Cron schedule definition
├── src/
│   ├── config.py           # API keys, DB config, indicator definitions
│   ├── app/
│   │   ├── main.py         # Streamlit dashboard
│   │   ├── queries.py      # DB read queries
│   │   └── transforms.py   # Data transformations (Base 100, % change, resample)
│   ├── db/
│   │   └── connection.py   # PostgreSQL connection handler
│   ├── extract/
│   │   ├── fred.py         # FRED API extractor
│   │   └── alpha_vantage.py # Alpha Vantage API extractor
│   ├── transform/
│   │   └── transform.py    # Raw data cleaning and normalization
│   └── load/
│       └── load.py         # DB upsert logic
├── sql/
│   └── create_tables.sql   # DB schema
├── data/raw/               # Local cache for API responses (gitignored)
└── .env.example            # Environment variable template
```

---

## Setup

### Prerequisites
- [Docker](https://www.docker.com/) and Docker Compose installed
- A free API key from [FRED](https://fred.stlouisfed.org/docs/api/api_key.html)
- A free API key from [Alpha Vantage](https://www.alphavantage.co/support/#api-key)

### 1. Clone the repository

```bash
git clone https://github.com/EmiOrellana/economic_pipeline.git
cd economic_pipeline
```

### 2. Configure environment variables

```bash
cp .env.example .env
```

Edit `.env` and fill in your credentials:

```env
FRED_API_KEY=your_fred_api_key
ALPHA_VANTAGE_API_KEY=your_alpha_vantage_api_key

DB_HOST=db
DB_PORT=5432
DB_NAME=economic_pipeline
DB_USER=postgres
DB_PASSWORD=your_password
```

> **Note:** `DB_HOST=db` is the correct value for Docker. If running locally without Docker, change it to `localhost`.

### 3. Start the services

```bash
docker compose up --build
```

This will:
- Start a PostgreSQL container
- Create the database schema automatically
- Run the ETL pipeline to load initial data
- Start the Cron scheduler for daily updates
- Start the Streamlit dashboard

### 4. Open the dashboard

Navigate to [http://localhost:8501](http://localhost:8501)

---

## Usage

Use the sidebar to configure the chart:

- **Select indicators** — choose one or more indicators to display
- **Date range** — filter observations by start and end date
- **Transformation** — view absolute values, Base 100 index, or percentage change
- **Resample interval** — aggregate data by day, month, quarter, or year

> **Note:** When mixing indicators with different units in "Absolute values" mode, the dashboard will suggest switching to Base 100 or Percentage change for a meaningful comparison.

---

## Data Updates

The pipeline runs automatically every day at midnight (UTC) via Cron. To trigger a manual update:

```bash
docker compose exec app python run_pipeline.py
```

Pipeline logs are saved to `/var/log/pipeline.log` inside the container.

---

## Notes

- Alpha Vantage free tier is limited to 25 API calls per day. The pipeline uses local JSON caching with a 24-hour TTL to avoid unnecessary requests.
- FRED API is unlimited in practice.
- Data starts from January 1, 2010.
