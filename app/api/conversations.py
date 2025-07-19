from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from uuid import UUID

from app.db.database import get_db
from app.db.repositories import conversations as conversations_repository
from app.db.repositories import lawyers as lawyers_repository
from app.db.repositories import analytics as analytics_repository
from app.schemas.conversation import (
    ConversationResponse, 
    MessageResponse, 
    MessageCreate,
    ParticipantData,
    SuccessResponse
)
from app.schemas.analytics import MessageEventCreate
from app.api.dependencies import get_current_user
from app.models.user import User
from datetime import datetime

router = APIRouter()

@router.get("", response_model=List[ConversationResponse])
async def list_user_conversations(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    List all conversations for the authenticated user, ordered by most recent message
    """
    conversations = conversations_repository.get_conversations_for_user(db, current_user.id)
    
    response = []
    for conversation in conversations:
        # Get the other participant
        other_participant = conversation.get_other_participant(current_user.id)
        
        if other_participant:
            # Create participant data with fallback logic for different user types
            participant_data = ParticipantData(
                id=other_participant.id,
                name=getattr(other_participant, 'name', None) or 
                     f"{getattr(other_participant, 'first_name', '')} {getattr(other_participant, 'last_name', '')}".strip() or 
                     other_participant.email,
                title=getattr(other_participant, 'title', 'User'),
                image_url=getattr(other_participant, 'image_url', None)
            )
            
            response.append(
                ConversationResponse(
                    id=conversation.id,
                    other_participant=participant_data,
                    last_message=conversation.last_message,
                    last_message_date=conversation.last_message_date
                )
            )
    
    return response

@router.get("/{conversation_id}/messages", response_model=List[MessageResponse])
async def get_conversation_messages(
    conversation_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get all messages for a specific conversation
    """
    conversation = conversations_repository.get_conversation_by_id(db, conversation_id)
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")
    
    # Check if user is a participant
    if not conversation.is_participant(current_user.id):
        raise HTTPException(status_code=403, detail="Not authorized to access this conversation")
    
    # Get messages
    messages = conversations_repository.get_messages_by_conversation(db, conversation_id)
    
    # Mark conversation as read (mark messages from others as read)
    conversations_repository.mark_conversation_as_read(db, conversation_id, current_user.id)
    
    # Format response with is_from_me
    response = []
    for message in messages:
        response.append(
            MessageResponse(
                id=message.id,
                conversation_id=message.conversation_id,
                sender_id=message.sender_id,
                content=message.content,
                is_from_me=message.is_from_me(current_user.id),
                read=message.read,
                timestamp=message.timestamp
            )
        )
    
    return response

@router.post("/{conversation_id}/messages", response_model=MessageResponse, status_code=status.HTTP_201_CREATED)
async def send_reply_in_conversation(
    conversation_id: UUID,
    message: MessageCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Send a new message in an existing conversation - SIMPLE!
    """
    conversation = conversations_repository.get_conversation_by_id(db, conversation_id)
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")
    
    # Check if user is a participant
    if not conversation.is_participant(current_user.id):
        raise HTTPException(status_code=403, detail="Not authorized to send messages in this conversation")
    
    # Create the message - super simple!
    db_message = conversations_repository.create_message(
        db, 
        conversation_id, 
        current_user.id,  # sender
        message.content
    )
    
    return MessageResponse(
        id=db_message.id,
        conversation_id=db_message.conversation_id,
        sender_id=db_message.sender_id,
        content=db_message.content,
        is_from_me=True,  # Always true since current user sent it
        read=db_message.read,
        timestamp=db_message.timestamp
    )

@router.post("/lawyers/{lawyer_id}/messages", response_model=MessageResponse, status_code=status.HTTP_201_CREATED)
async def send_message_to_lawyer(
    lawyer_id: UUID,
    message: MessageCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Send a message to a lawyer - creates conversation if it doesn't exist
    """
    # Get lawyer and their user_id
    lawyer = lawyers_repository.get_lawyer_by_id(db, lawyer_id)
    if not lawyer:
        raise HTTPException(status_code=404, detail="Lawyer not found")
    
    if not lawyer.user_id:
        raise HTTPException(status_code=400, detail="Lawyer does not have an associated user account")
    
    # Check if conversation already exists between current user and lawyer's user account
    conversation = conversations_repository.get_conversation_by_participants(
        db, current_user.id, lawyer.user_id
    )
    
    if not conversation:
        # Create new conversation between current user and lawyer's user account
        conversation = conversations_repository.create_conversation(
            db, current_user.id, lawyer.user_id
        )
    
    # Create the message
    db_message = conversations_repository.create_message(
        db, 
        conversation.id, 
        current_user.id,
        message.content
    )
    
    return MessageResponse(
        id=db_message.id,
        conversation_id=db_message.conversation_id,
        sender_id=db_message.sender_id,
        content=db_message.content,
        is_from_me=True,
        read=db_message.read,
        timestamp=db_message.timestamp
    )

@router.post("/{conversation_id}/read", response_model=SuccessResponse)
async def mark_conversation_as_read_endpoint(
    conversation_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Marks all unread messages in the conversation as read for the user
    """
    result = conversations_repository.mark_conversation_as_read(db, conversation_id, current_user.id)
    if not result:
        raise HTTPException(status_code=404, detail="Conversation not found")
    
    return {"success": True}

@router.get("/unread", response_model=dict)
async def get_unread_message_count(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get the total number of unread messages across all conversations
    """
    unread_count = conversations_repository.get_unread_count(db, current_user.id)
    
    return {"unread_count": unread_count}