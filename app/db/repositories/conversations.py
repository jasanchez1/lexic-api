from typing import List, Optional, Tuple
from uuid import UUID
from datetime import datetime, timezone
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import desc, or_, and_, func

from app.models.conversation import Conversation, ConversationMessage

def get_conversation_by_id(db: Session, conversation_id: UUID) -> Optional[Conversation]:
    """
    Get a conversation by ID with participants loaded
    """
    return db.query(Conversation).options(
        joinedload(Conversation.participant_1),
        joinedload(Conversation.participant_2),
        joinedload(Conversation.messages)
    ).filter(Conversation.id == conversation_id).first()

def get_conversation_by_participants(db: Session, user1_id: UUID, user2_id: UUID) -> Optional[Conversation]:
    """
    Get a conversation between two users (order doesn't matter)
    """
    return db.query(Conversation).filter(
        or_(
            and_(
                Conversation.participant_1_id == user1_id,
                Conversation.participant_2_id == user2_id
            ),
            and_(
                Conversation.participant_1_id == user2_id,
                Conversation.participant_2_id == user1_id
            )
        )
    ).first()

def get_conversations_for_user(db: Session, user_id: UUID, skip: int = 0, limit: int = 100) -> List[Conversation]:
    """
    Get all conversations where user is a participant
    """
    return db.query(Conversation).options(
        joinedload(Conversation.participant_1),
        joinedload(Conversation.participant_2)
    ).filter(
        or_(
            Conversation.participant_1_id == user_id,
            Conversation.participant_2_id == user_id
        )
    ).order_by(
        desc(Conversation.last_message_date)
    ).offset(skip).limit(limit).all()

def create_conversation(db: Session, participant_1_id: UUID, participant_2_id: UUID) -> Conversation:
    """
    Create a new conversation between two users
    """
    db_conversation = Conversation(
        participant_1_id=participant_1_id,
        participant_2_id=participant_2_id
    )
    db.add(db_conversation)
    db.commit()
    db.refresh(db_conversation)
    return db_conversation

def get_message_by_id(db: Session, message_id: UUID) -> Optional[ConversationMessage]:
    """
    Get a message by ID
    """
    return db.query(ConversationMessage).options(
        joinedload(ConversationMessage.sender)
    ).filter(ConversationMessage.id == message_id).first()

def get_messages_by_conversation(db: Session, conversation_id: UUID, skip: int = 0, limit: int = 100) -> List[ConversationMessage]:
    """
    Get all messages for a conversation
    """
    return db.query(ConversationMessage).options(
        joinedload(ConversationMessage.sender)
    ).filter(
        ConversationMessage.conversation_id == conversation_id
    ).order_by(
        ConversationMessage.timestamp
    ).offset(skip).limit(limit).all()

def create_message(
    db: Session, 
    conversation_id: UUID,
    sender_id: UUID,
    content: str
) -> ConversationMessage:
    """
    Create a new message in a conversation - SIMPLE!
    """
    # Create message
    db_message = ConversationMessage(
        conversation_id=conversation_id,
        sender_id=sender_id,
        content=content,
        read=False
    )
    db.add(db_message)
    
    # Update conversation with last message
    conversation = db.query(Conversation).filter(Conversation.id == conversation_id).first()
    if conversation:
        conversation.last_message = content
        conversation.last_message_date = db_message.timestamp or datetime.now(timezone.utc)
        db.add(conversation)
    
    db.commit()
    db.refresh(db_message)
    return db_message

def mark_conversation_as_read(db: Session, conversation_id: UUID, user_id: UUID) -> Optional[Conversation]:
    """
    Mark all messages NOT sent by the current user as read
    """
    conversation = db.query(Conversation).filter(Conversation.id == conversation_id).first()
    
    if not conversation or not conversation.is_participant(user_id):
        return None
    
    # Mark all messages NOT sent by current user as read
    db.query(ConversationMessage).filter(
        and_(
            ConversationMessage.conversation_id == conversation_id,
            ConversationMessage.sender_id != user_id,
            ConversationMessage.read == False
        )
    ).update({"read": True})
    
    db.commit()
    db.refresh(conversation)
    return conversation

def get_unread_count(db: Session, user_id: UUID) -> int:
    """
    Get total unread messages for a user (messages sent TO them)
    """
    return db.query(ConversationMessage).join(Conversation).filter(
        and_(
            or_(
                Conversation.participant_1_id == user_id,
                Conversation.participant_2_id == user_id
            ),
            ConversationMessage.sender_id != user_id,  # Not sent by current user
            ConversationMessage.read == False
        )
    ).count()