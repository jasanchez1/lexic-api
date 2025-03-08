# Lexic API

Backend API for Lexic, a platform for connecting with lawyers in Chile.

## Features

- FastAPI framework with automatic OpenAPI documentation
- PostgreSQL database with SQLAlchemy ORM
- Alembic for database migrations
- JWT authentication with access and refresh tokens
- Environment-aware deployment configuration
- Docker and docker-compose for easy development and deployment

## Setup

### Prerequisites

- Docker and Docker Compose
- Python 3.11+ (for local development without Docker)

### Quick Start with Docker

1. Clone the repository:
```bash
git clone https://github.com/yourusername/lexic-api.git
cd lexic-api
```

2. Create the appropriate `.env` file for your environment:

**For local development:**
```bash
cat > .env << EOF
DATABASE_URL=postgresql://postgres:postgres@db:5432/lexic_db
SECRET_KEY=supersecretkey
ACCESS_TOKEN_EXPIRE_MINUTES=30
ENVIRONMENT=development
EOF
```

**For production/staging (with external database):**
```bash
cat > .env << EOF
DATABASE_URL=postgresql://postgres:your-password@your-rds-endpoint:5432/lexic_db
SECRET_KEY=$(openssl rand -hex 32)
ACCESS_TOKEN_EXPIRE_MINUTES=30
ENVIRONMENT=production
EOF
```

3. Run the application using the run script:
```bash
chmod +x run.sh
./run.sh
```

The script will automatically detect your environment and start the appropriate services:
- In `development`: API, PostgreSQL database, and pgAdmin
- In `production` or `staging`: Only the API, connecting to your external database

4. Access the services:
   - API: http://localhost:8000
   - API documentation: http://localhost:8000/docs
   - pgAdmin (development only): http://localhost:5050 (login with admin@lexic.com / admin)

## Environment Configuration

The application uses the `ENVIRONMENT` variable to determine its behavior:

- `development`: Uses a local PostgreSQL database running in Docker
- `staging`: Uses an external database (like AWS RDS) 
- `production`: Uses an external database (like AWS RDS)

### Database Migrations

Migrations are automatically run on startup. To manually create and run database migrations:

```bash
# Enter the API container
docker-compose exec api bash

# Create a new migration
alembic revision --autogenerate -m "description of changes"

# Run migrations
alembic upgrade head
```

## Deployment

### AWS EC2 with RDS Deployment

1. **Set up RDS PostgreSQL database**
2. **Launch an EC2 instance**
3. **Install Docker and Git on EC2**
   ```bash
   sudo apt update
   sudo apt install -y docker.io docker-compose git
   sudo usermod -aG docker ubuntu
   newgrp docker
   ```
4. **Clone the repository and set up environment**
   ```bash
   git clone https://github.com/yourusername/lexic-api.git
   cd lexic-api
   
   # Create production environment file
   cat > .env << EOF
   DATABASE_URL=postgresql://postgres:password@your-rds-endpoint:5432/lexic_db
   SECRET_KEY=$(openssl rand -hex 32)
   ACCESS_TOKEN_EXPIRE_MINUTES=30
   ENVIRONMENT=production
   EOF
   ```
5. **Run the application**
   ```bash
   ./run.sh
   ```

### SSH Tunnel for Database Access

To connect to your RDS database via DBeaver while keeping it not publicly accessible:

1. Configure your RDS to be private (no public access)
2. Set up an SSH tunnel through your EC2 instance in DBeaver:
   - Host: Your RDS endpoint
   - Port: 5432
   - Username: postgres
   - Password: your-password
   - SSH tunnel: Enabled
   - SSH Host: Your EC2 public IP/DNS
   - SSH User: ubuntu
   - SSH Authentication: Private key

## API Documentation

The API documentation is automatically generated and can be accessed at:

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Development

### Project Structure

```
lexic-api/
├── app/
│   ├── api/            # API routes
│   ├── core/           # Core functionality (config, security)
│   ├── db/             # Database models and repositories
│   ├── models/         # SQLAlchemy models
│   ├── schemas/        # Pydantic schemas
│   ├── services/       # Business logic
│   └── main.py         # FastAPI application
├── alembic/            # Database migrations
├── tests/              # Tests
├── docker-compose.yml  # Docker Compose configuration
├── Dockerfile          # Docker image definition
├── run.sh              # Environment-aware startup script
└── requirements.txt    # Python dependencies
```

### Authentication Flow

1. User signs up or logs in to receive an access token and a refresh token
2. Access token is used for API requests (short-lived)
3. Refresh token is used to obtain a new access token when it expires (long-lived)

### Running Tests

```bash
# Run tests inside the container
docker-compose exec api pytest

# Run with coverage
docker-compose exec api pytest --cov=app
```

## License

[MIT License](LICENSE)