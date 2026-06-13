#!/bin/bash
set -e

echo "Waiting for PostgreSQL..."
until python -c "from src.db.connection import get_db_connection; from src.config import DB_CONFIG; get_db_connection(DB_CONFIG)" 2>/dev/null; do
    sleep 2
done

echo "PostgreSQL ready. Setting up database..."
python setup_db.py

echo "Running pipeline..."
python src/run_pipeline.py

echo "Snapshotting environment for cron..."
# Cron runs jobs with a minimal environment and does NOT inherit the
# container's variables (DB credentials, API keys) nor its PATH. We snapshot
# the variables the pipeline needs into a file that the cron job sources
# before running. See crontab.
printenv | grep -E '^(PATH|DB_|FRED_|ALPHA_VANTAGE_)' | sed 's/^/export /' > /app/cron.env

echo "Starting cron..."
cron

echo "Starting dashboard..."
streamlit run src/app/main.py --server.port 8501 --server.address 0.0.0.0