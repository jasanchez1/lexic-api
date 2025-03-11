from typing import List, Optional
from uuid import UUID
from sqlalchemy.orm import Session
from datetime import datetime

from app.models.message import Message, Call
from app.schemas.message import MessageCreate, CallCreate

def get_message_by_id(db: Session, message_id: UUID) -> Optional[Message]:
    """
    Get a message by ID
    """
    return db.query(Message).filter(Message.id == message_id).first()

def get_messages_by_lawyer(db: Session, lawyer_id: UUID) -> List[Message]:
    """
    Get all messages for a lawyer
    """
    return db.query(Message).filter(Message.lawyer_id == lawyer_id).order_by(Message.created_at.desc()).all()

def create_message(db: Session, message: MessageCreate, lawyer_id: UUID) -> Message:
    """
    Create a new message
    """
    db_message = Message(
        name=message.name,
        email=message.email,
        phone=message.phone,
        message=message.message,
        lawyer_id=lawyer_id,
        read=False
    )
    db.add(db_message)
    db.commit()
    db.refresh(db_message)
    return db_message

def mark_message_as_read(db: Session, message: Message) -> Message:
    """
    Mark a message as read
    """
    message.read = True
    db.add(message)
    db.commit()
    db.refresh(message)
    return message

def delete_message(db: Session, message_id: UUID) -> None:
    """
    Delete a message
    """
    message = db.query(Message).filter(Message.id == message_id).first()
    if message:
        db.delete(message)
        db.commit()
    return None

def get_call_by_id(db: Session, call_id: UUID) -> Optional[Call]:
    """
    Get a call by ID
    """
    return db.query(Call).filter(Call.id == call_id).first()

def get_calls_by_lawyer(db: Session, lawyer_id: UUID) -> List[Call]:
    """
    Get all calls for a lawyer
    """
    return db.query(Call).filter(Call.lawyer_id == lawyer_id).order_by(Call.timestamp.desc()).all()

def create_call(db: Session, call: CallCreate, lawyer_id: UUID) -> Call:
    """
    Create a new call entry
    """
    db_call = Call(
        completed=call.completed,
        timestamp=call.timestamp,
        lawyer_id=lawyer_id
    )
    db.add(db_call)
    db.commit()
    db.refresh(db_call)
    return db_call

def delete_call(db: Session, call_id: UUID) -> None:
    """
    Delete a call entry
    """
    call = db.query(Call).filter(Call.id == call_id).first()
    if call:
        db.delete(call)
        db.commit()
    return None
