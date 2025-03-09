#!/bin/bash
set -e

# Function to print colored output
print_colored() {
  COLOR=$1
  MESSAGE=$2
  
  case $COLOR in
    "red") echo -e "\033[0;31m$MESSAGE\033[0m" ;;
    "green") echo -e "\033[0;32m$MESSAGE\033[0m" ;;
    "yellow") echo -e "\033[0;33m$MESSAGE\033[0m" ;;
    "blue") echo -e "\033[0;34m$MESSAGE\033[0m" ;;
    *) echo "$MESSAGE" ;;
  esac
}

# Check if .env file exists
if [ ! -f .env ]; then
  print_colored "red" "Error: .env file not found. Please create one with the ENVIRONMENT variable set."
  exit 1
fi

# Source the .env file to get the environment
source .env

# Check if ENVIRONMENT is set
if [ -z "$ENVIRONMENT" ]; then
  print_colored "red" "Error: ENVIRONMENT variable not set in .env file. It should be 'development', 'staging', or 'production'."
  exit 1
fi

print_colored "blue" "Starting Lexic API in $ENVIRONMENT mode..."

# Create docker-compose command based on environment
if [ "$ENVIRONMENT" = "development" ]; then
  print_colored "green" "Development mode: Starting API with local database"
  
  # Check if DATABASE_URL is set correctly for development
  if [[ "$DATABASE_URL" != *"@db:"* ]]; then
    print_colored "yellow" "Warning: Your DATABASE_URL doesn't point to the local container. Make sure it contains '@db:' for local development."
  fi
  
  # Start with development profile to include DB and pgAdmin
  docker-compose --profile development up -d
  
elif [ "$ENVIRONMENT" = "staging" ] || [ "$ENVIRONMENT" = "production" ]; then
  print_colored "green" "$ENVIRONMENT mode: Starting API with external database"
  
  # Check if DATABASE_URL is set and doesn't point to local container
  if [ -z "$DATABASE_URL" ]; then
    print_colored "red" "Error: DATABASE_URL not set in .env file. It should point to your RDS instance."
    exit 1
  fi
  
  if [[ "$DATABASE_URL" == *"@db:"* ]]; then
    print_colored "red" "Error: Your DATABASE_URL points to a local container (@db:) but you're in $ENVIRONMENT mode. It should point to your RDS instance."
    exit 1
  fi
  
  # Start without any profile (only API will start)
  docker-compose up -d api
  
else
  print_colored "red" "Error: Invalid ENVIRONMENT value '$ENVIRONMENT'. Must be 'development', 'staging', or 'production'."
  exit 1
fi

# Check if the containers are running
if [ "$ENVIRONMENT" = "development" ]; then
  if docker-compose ps | grep -q "lexic-api\|lexic-db\|lexic-pgadmin"; then
    print_colored "green" "✅ Lexic API started successfully in development mode with local database"
    print_colored "blue" "📊 Access API at: http://localhost:8000"
    print_colored "blue" "📊 Access API docs at: http://localhost:8000/docs"
    print_colored "blue" "📊 Access pgAdmin at: http://localhost:5050"
  else
    print_colored "red" "❌ Failed to start services"
    exit 1
  fi
else
  if docker-compose ps | grep -q "lexic-api"; then
    print_colored "green" "✅ Lexic API started successfully in $ENVIRONMENT mode"
    print_colored "blue" "📊 Access API at: http://localhost:8000"
    print_colored "blue" "📊 Access API docs at: http://localhost:8000/docs"
  else
    print_colored "red" "❌ Failed to start services"
    exit 1
  fi
fi

# Show logs option
print_colored "yellow" "To view logs, run: docker-compose logs -f api"