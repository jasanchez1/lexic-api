from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import auth, health, areas, lawyers, categories
from app.core.config import settings

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
app.include_router(areas.router, prefix="/areas", tags=["areas"])
app.include_router(categories.router, prefix="/categories", tags=["categories"])
app.include_router(lawyers.router, prefix="/lawyers", tags=["lawyers"])