from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from uuid import UUID

from app.db.database import get_db
from app.db.repositories import messages as messages_repository
from app.db.repositories import lawyers as lawyers_repository
from app.schemas.message import MessageCreate, MessageCreateResponse
from app.api.dependencies import get_current_user, get_optional_current_user
from app.models.user import User

router = APIRouter()


@router.post("/{lawyer_id}/messages", status_code=status.HTTP_201_CREATED)
async def send_message_to_lawyer(
    lawyer_id: UUID,
    message: MessageCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Send a message to a lawyer
    """
    # Verify lawyer exists
    lawyer = lawyers_repository.get_lawyer_by_id(db, lawyer_id)
    if not lawyer:
        raise HTTPException(status_code=404, detail="Lawyer not found")

    # Ensure the user_id in the message matches the current user
    if message.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="User ID in message must match the authenticated user")

    # Create message
    db_message = messages_repository.create_message(db, message, lawyer_id)

    return MessageCreateResponse(
        success=True, 
        message_id=str(db_message.id), 
        user_id=db_message.user_id
    )