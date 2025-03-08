from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import auth, health
from app.core.config import settings
from app.db.database import create_tables

app = FastAPI(
    title="Lexic API",
    description="Backend API for Lexic, a platform to connect with lawyers in Chile",
    version="0.1.0",
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(health.router, tags=["health"])
app.include_router(auth.router, prefix="/auth", tags=["auth"])

# Create database tables on startup (for development)
@app.on_event("startup")
async def startup_event():
    create_tables()