#!/bin/sh
# docker-entrypoint.sh
set -e

# Wait for database
echo "Waiting for database..."
python src/scripts/wait_for_db.py

# Run migrations
echo "Running database migrations..."
alembic upgrade head

if [ "$ENV" = "development" ]; then
    echo "Starting development server..."
    exec uvicorn src.main:app --host 0.0.0.0 --port 8000 --reload
else
    echo "Starting production server..."
    exec uvicorn src.main:app --host 0.0.0.0 --port 8000 --workers 4
fi