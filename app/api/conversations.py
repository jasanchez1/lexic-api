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
    ConversationList, 
    MessageResponse, 
    MessageList,
    MessageCreate,
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
    # Get user's conversations
    conversations = conversations_repository.get_conversations_for_user(db, current_user.id)
    
    # Format the response
    response = []
    for conversation in conversations:
        # Prepare lawyer data
        lawyer_data = {
            "id": conversation.lawyer.id,
            "name": conversation.lawyer.name,
            "title": conversation.lawyer.title,
            "image_url": conversation.lawyer.image_url
        }
        
        # Create conversation response
        response.append(
            ConversationResponse(
                id=conversation.id,
                lawyer=lawyer_data,
                last_message=conversation.last_message,
                last_message_date=conversation.last_message_date,
                unread_count=conversation.unread_count
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
    # Get the conversation
    conversation = conversations_repository.get_conversation_by_id(db, conversation_id)
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")
    
    # Verify the current user is part of the conversation
    if conversation.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to access this conversation")
    
    # Get messages
    messages = conversations_repository.get_messages_by_conversation(db, conversation_id)
    
    # Track message read event
    for message in messages:
        if message.from_lawyer and not message.read:
            # Track in analytics
            event_data = MessageEventCreate(
                lawyer_id=conversation.lawyer_id,
                user_id=current_user.id,
                status="read",
                timestamp=datetime.now()
            )
            analytics_repository.create_message_event(db, event_data)
    
    # Mark conversation as read
    conversations_repository.mark_conversation_as_read(db, conversation_id, current_user.id)
    
    return messages

@router.post("/{conversation_id}/messages", response_model=MessageResponse, status_code=status.HTTP_201_CREATED)
async def send_reply_in_conversation(
    conversation_id: UUID,
    message: MessageCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Send a new message in an existing conversation
    """
    # Get the conversation
    conversation = conversations_repository.get_conversation_by_id(db, conversation_id)
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")
    
    # Verify the current user is part of the conversation
    if conversation.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to send messages in this conversation")
    
    # Set user_id from current user
    message.user_id = current_user.id
    
    # Create the message
    db_message = conversations_repository.create_message(db, message, conversation_id, from_lawyer=False)
    
    # Track message sent event
    event_data = MessageEventCreate(
        lawyer_id=conversation.lawyer_id,
        user_id=current_user.id,
        status="sent",
        timestamp=datetime.now()
    )
    analytics_repository.create_message_event(db, event_data)
    
    return db_message

@router.post("/lawyers/{lawyer_id}/messages", status_code=status.HTTP_201_CREATED)
async def send_initial_message_to_lawyer(
    lawyer_id: UUID,
    message: MessageCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Send a new message to a lawyer, creating a conversation if one doesn't exist.
    This is used for the initial contact with a lawyer.
    """
    # Verify lawyer exists
    lawyer = lawyers_repository.get_lawyer_by_id(db, lawyer_id)
    if not lawyer:
        raise HTTPException(status_code=404, detail="Lawyer not found")
    
    # Set user_id from current user
    message.user_id = current_user.id
    
    # Check if a conversation already exists
    conversation = conversations_repository.get_conversation_by_user_and_lawyer(
        db, current_user.id, lawyer_id
    )
    
    if not conversation:
        # Create a new conversation
        from app.schemas.conversation import ConversationCreate
        conversation_data = ConversationCreate(
            user_id=current_user.id,
            lawyer_id=lawyer_id
        )
        conversation = conversations_repository.create_conversation(db, conversation_data)
    
    # Create the message
    db_message = conversations_repository.create_message(db, message, conversation.id, from_lawyer=False)
    
    # Track message sent event
    event_data = MessageEventCreate(
        lawyer_id=lawyer_id,
        user_id=current_user.id,
        status="sent",
        timestamp=datetime.now()
    )
    analytics_repository.create_message_event(db, event_data)
    
    return {
        "id": str(db_message.id),
        "conversation_id": str(conversation.id),
        "content": db_message.content,
        "timestamp": db_message.timestamp,
        "success": True
    }

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