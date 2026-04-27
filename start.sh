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

echo "Starting dashboard..."
streamlit run src/app/main.py --server.port 8501 --server.address 0.0.0.0