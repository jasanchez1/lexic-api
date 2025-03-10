#!/bin/bash
# scripts/seed_data.sh

set -e

echo "Make sure your PostgreSQL database is running locally before continuing."
echo "The script will connect to: postgresql://postgres:postgres@localhost:5432/lexic_db"

# Check if the database exists, if not create it
PGPASSWORD=postgres psql -h localhost -U postgres -tc "SELECT 1 FROM pg_database WHERE datname = 'lexic_db'" | grep -q 1 || PGPASSWORD=postgres psql -h localhost -U postgres -c "CREATE DATABASE lexic_db"

# Run migrations
echo "Running Alembic migrations..."
alembic upgrade head

echo "Seeding cities..."
python scripts/seed_cities.py

echo "Seeding legal topics..."
python scripts/seed_topics.py

echo "Seeding practice areas..."
python scripts/seed_practice_areas.py

echo "Seeding lawyers..."
python scripts/seed_lawyers.py

echo "Seeding questions..."
python scripts/seed_questions.py

echo "Seeding answers and replies..."
python scripts/seed_answers.py

echo "Seeding completed successfully!"