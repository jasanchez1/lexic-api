from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os

from app.api import (
    auth,
    health,
    areas,
    lawyers,
    categories,
    cities,
    topics,
    questions,
    answers,
    analytics,
    guides,
    featured_items,
    navigation,
    conversations,  # Add new conversations router
)
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

# Create uploads directory if it doesn't exist
os.makedirs("uploads/guide_images", exist_ok=True)

# Mount static files directory for uploaded images
app.mount("/api/uploads", StaticFiles(directory="uploads"), name="uploads")

# Include routers
app.include_router(health.router, tags=["health"])
app.include_router(auth.router, prefix="/auth", tags=["auth"])
app.include_router(areas.router, prefix="/areas", tags=["areas"])
app.include_router(categories.router, prefix="/categories", tags=["categories"])
app.include_router(lawyers.router, prefix="/lawyers", tags=["lawyers"])
app.include_router(cities.router, prefix="/cities", tags=["cities"])
app.include_router(topics.router, prefix="/topics", tags=["topics"])
app.include_router(questions.router, prefix="/questions", tags=["questions"])
app.include_router(answers.router, tags=["answers"])
app.include_router(analytics.router, prefix="/analytics", tags=["analytics"])
app.include_router(guides.router, prefix="/guides", tags=["guides"])
app.include_router(
    featured_items.router, prefix="/admin/featured-items", tags=["admin"]
)
app.include_router(navigation.router, prefix="/navigation", tags=["navigation"])
app.include_router(conversations.router, prefix="/conversations", tags=["conversations"])