from typing import List, Optional
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Query, status, BackgroundTasks
from sqlalchemy.orm import Session
from uuid import UUID

from app.db.database import get_db
from app.db.repositories import lawyers as lawyers_repository
from app.db.repositories import conversations as conversations_repository
from app.db.repositories import analytics as analytics_repository
from app.schemas.analytics import MessageEventCreate
from app.schemas.message import MessageCreate, MessageCreateResponse
from app.api.dependencies import get_current_user
from app.models.user import User

router = APIRouter()


@router.post("/{lawyer_id}/messages", status_code=status.HTTP_201_CREATED)
async def send_message_to_lawyer(
    lawyer_id: UUID,
    message: MessageCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    background_tasks: BackgroundTasks = BackgroundTasks(),
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
        raise HTTPException(
            status_code=403,
            detail="User ID in message must match the authenticated user",
        )

    # Get lawyer's user_id first
    lawyer_user_id = lawyer.user_id if lawyer.user_id else None
    if not lawyer_user_id:
        raise HTTPException(
            status_code=400, 
            detail="Lawyer does not have an associated user account"
        )

    # Check if a conversation already exists
    conversation = conversations_repository.get_conversation_by_participants(
        db, current_user.id, lawyer_user_id
    )
    
    if not conversation:
        # Create a new conversation
        conversation = conversations_repository.create_conversation(
            db, current_user.id, lawyer_user_id
        )
    
    # Create the message
    db_message = conversations_repository.create_message(
        db, 
        conversation.id, 
        current_user.id,
        message.content
    )

    # Track message sent event via analytics
    event_data = MessageEventCreate(
        lawyer_id=lawyer_id,
        user_id=current_user.id,
        status="sent",
        timestamp=datetime.now(),
    )

    # Use background task to track event
    background_tasks.add_task(
        analytics_repository.create_message_event,
        db=db,
        event=event_data,
    )

    return MessageCreateResponse(
        success=True, 
        message_id=str(db_message.id), 
        user_id=current_user.id,
        conversation_id=str(conversation.id)
    )