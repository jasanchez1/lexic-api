# Lexic API

Backend API for the Lexic platform, a service connecting lawyers with potential clients.

## Technology Stack

- FastAPI
- PostgreSQL
- SQLAlchemy
- Alembic
- Docker
- JWT Authentication

## Development Setup

### Prerequisites

- Docker and Docker Compose
- Python 3.9+
- PostgreSQL 14+

### Environment Variables

Create a `.env` file in the root directory:

```env
# Database
DATABASE_URL=postgresql://postgres:postgres@db:5432/lawyers_db

# JWT
JWT_SECRET_KEY=your-secret-key-at-least-32-characters
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# CORS
CORS_ORIGINS=["http://localhost:3000"]

# Environment
ENV=development
```

### Running with Docker

1. Start the services:
```bash
docker compose up --build
```

2. Run migrations:
```bash
docker compose exec api alembic upgrade head
```

The API will be available at `http://localhost:8000`

### Local Development Setup

1. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # or `venv\Scripts\activate` on Windows
```

2. Install dependencies:
```bash
pip install -e .
```

3. Run migrations:
```bash
alembic upgrade head
```

4. Start the development server:
```bash
uvicorn src.main:app --reload
```

## API Documentation

Once the server is running, you can access:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Database Migrations

Create a new migration:
```bash
alembic revision --autogenerate -m "description of changes"
```

Apply migrations:
```bash
alembic upgrade head
```

Rollback one migration:
```bash
alembic downgrade -1
```

## Project Structure

```
lexic-api/
├── src/
│   ├── core/           # Core functionality, config, security
│   ├── models/         # SQLAlchemy models
│   ├── schemas/        # Pydantic schemas
│   ├── services/       # Business logic
│   ├── routers/        # API endpoints
│   └── main.py         # Application entry point
├── tests/              # Test files
├── migrations/         # Alembic migrations
├── docker-compose.yml  # Docker compose configuration
├── Dockerfile         # Docker build file
├── requirements.txt   # Python dependencies
└── pyproject.toml    # Project metadata and dependencies
```

## Testing

Run tests:
```bash
pytest
```

## Production Deployment

1. Set environment variables for production:
```bash
ENV=production
DATABASE_URL=your-production-db-url
JWT_SECRET_KEY=your-production-secret
CORS_ORIGINS=["https://your-frontend-domain.com"]
```

2. Build and run:
```bash
docker compose up --build
```

## Contributing

1. Fork the repository
2. Create a new branch for your feature
3. Make your changes
4. Submit a pull request

## License

[Add your license information here]