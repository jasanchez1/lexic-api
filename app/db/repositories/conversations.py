from typing import List, Optional, Tuple
from uuid import UUID
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import desc, or_, and_, func

from app.models.conversation import Conversation, ConversationMessage
from app.models.lawyer import Lawyer
from app.schemas.conversation import ConversationCreate, MessageCreate

def get_conversation_by_id(db: Session, conversation_id: UUID) -> Optional[Conversation]:
    """
    Get a conversation by ID
    """
    return db.query(Conversation).options(
        joinedload(Conversation.lawyer),
        joinedload(Conversation.messages)
    ).filter(Conversation.id == conversation_id).first()

def get_conversation_by_user_and_lawyer(db: Session, user_id: UUID, lawyer_id: UUID) -> Optional[Conversation]:
    """
    Get a conversation between a user and a lawyer
    """
    return db.query(Conversation).filter(
        and_(
            Conversation.user_id == user_id,
            Conversation.lawyer_id == lawyer_id
        )
    ).first()

def get_conversations_for_user(db: Session, user_id: UUID, skip: int = 0, limit: int = 100) -> List[Conversation]:
    """
    Get all conversations for a user
    """
    return db.query(Conversation).options(
        joinedload(Conversation.lawyer)
    ).filter(
        Conversation.user_id == user_id
    ).order_by(
        desc(Conversation.last_message_date)
    ).offset(skip).limit(limit).all()

def create_conversation(db: Session, conversation: ConversationCreate) -> Conversation:
    """
    Create a new conversation
    """
    db_conversation = Conversation(**conversation.dict())
    db.add(db_conversation)
    db.commit()
    db.refresh(db_conversation)
    return db_conversation

def get_message_by_id(db: Session, message_id: UUID) -> Optional[ConversationMessage]:
    """
    Get a message by ID
    """
    return db.query(ConversationMessage).filter(ConversationMessage.id == message_id).first()

def get_messages_by_conversation(db: Session, conversation_id: UUID, skip: int = 0, limit: int = 100) -> List[ConversationMessage]:
    """
    Get all messages for a conversation
    """
    return db.query(ConversationMessage).filter(
        ConversationMessage.conversation_id == conversation_id
    ).order_by(
        ConversationMessage.timestamp
    ).offset(skip).limit(limit).all()

def create_message(
    db: Session, 
    message: MessageCreate, 
    conversation_id: UUID, 
    from_lawyer: bool = False
) -> ConversationMessage:
    """
    Create a new message in a conversation
    """
    # Create message
    db_message = ConversationMessage(
        conversation_id=conversation_id,
        content=message.content,
        from_lawyer=from_lawyer,
        read=from_lawyer  # Messages from the user are marked as read by default
    )
    db.add(db_message)
    
    # Update conversation with last message
    conversation = db.query(Conversation).filter(Conversation.id == conversation_id).first()
    if conversation:
        conversation.last_message = message.content
        conversation.last_message_date = db_message.timestamp
        
        # Increment unread count if message is from lawyer
        if from_lawyer:
            conversation.unread_count += 1
            
        db.add(conversation)
    
    db.commit()
    db.refresh(db_message)
    return db_message

def mark_conversation_as_read(db: Session, conversation_id: UUID, user_id: UUID) -> Conversation:
    """
    Mark all messages in a conversation as read for a user
    """
    # Verify the conversation belongs to the user
    conversation = db.query(Conversation).filter(
        and_(
            Conversation.id == conversation_id,
            Conversation.user_id == user_id
        )
    ).first()
    
    if not conversation:
        return None
    
    # Mark messages from lawyer as read
    db.query(ConversationMessage).filter(
        and_(
            ConversationMessage.conversation_id == conversation_id,
            ConversationMessage.from_lawyer == True,
            ConversationMessage.read == False
        )
    ).update({"read": True})
    
    # Reset unread count
    conversation.unread_count = 0
    db.add(conversation)
    db.commit()
    db.refresh(conversation)
    
    return conversation

def get_unread_count(db: Session, user_id: UUID) -> int:
    """
    Get the total number of unread messages for a user
    """
    result = db.query(Conversation).filter(
        Conversation.user_id == user_id
    ).with_entities(
        func.sum(Conversation.unread_count)
    ).scalar()
    
    return result or 0