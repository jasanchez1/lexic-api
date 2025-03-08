from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from sqlalchemy import text

from app.db.database import get_db

router = APIRouter()


@router.get("/health", status_code=status.HTTP_200_OK)
async def health_check():
    """
    Health check endpoint to verify the API is running
    """
    return {"status": "ok", "message": "Lexic API is running"}


@router.get("/health/db", status_code=status.HTTP_200_OK)
async def database_health_check(db: Session = Depends(get_db)):
    """
    Database health check endpoint to verify the database connection
    """
    try:
        # Execute a simple query to check database connection
        db.execute(text("SELECT 1"))
        return {"status": "ok", "message": "Database connection is healthy"}
    except Exception as e:
        return {
            "status": "error",
            "message": f"Database connection error: {str(e)}"
        }, status.HTTP_500_INTERNAL_SERVER_ERROR