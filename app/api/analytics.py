from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from uuid import UUID

from app.db.database import get_db
from app.db.repositories import messages as messages_repository
from app.db.repositories import lawyers as lawyers_repository
from app.schemas.message import CallCreate, CallCreateResponse
from app.models.user import User

router = APIRouter()

@router.post("/lawyers/{lawyer_id}/call", status_code=status.HTTP_201_CREATED)
async def track_lawyer_call(
    lawyer_id: UUID,
    call: CallCreate,
    db: Session = Depends(get_db)
):
    """
    Track a call to a lawyer (analytics)
    """
    # Verify lawyer exists
    lawyer = lawyers_repository.get_lawyer_by_id(db, lawyer_id)
    if not lawyer:
        raise HTTPException(status_code=404, detail="Lawyer not found")
    
    # Create call tracking record
    messages_repository.create_call(db, call, lawyer_id)
    
    return CallCreateResponse(success=True)
