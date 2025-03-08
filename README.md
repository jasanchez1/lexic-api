# Lexic API

Backend API for Lexic, a platform for connecting with lawyers in Chile.

## Features

- FastAPI framework with automatic OpenAPI documentation
- PostgreSQL database with SQLAlchemy ORM
- Alembic for database migrations
- JWT authentication with access and refresh tokens
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

2. Create a `.env` file from the example:
```bash
cp .env.example .env
```

3. Start the Docker containers:
```bash
docker-compose up -d
```

4. The API will be available at http://localhost:8000
5. The OpenAPI documentation will be available at http://localhost:8000/docs
6. pgAdmin will be available at http://localhost:5050 (login with admin@lexic.com / admin)

### Database Migrations

To create and run database migrations:

```bash
# Enter the API container
docker-compose exec api bash

# Create a new migration
alembic revision --autogenerate -m "description of changes"

# Run migrations
alembic upgrade head
```

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
├── Dockerfile
├── docker-compose.yml
└── requirements.txt
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