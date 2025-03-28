from typing import List, Optional
from datetime import datetime
from uuid import UUID
from pydantic import BaseModel

# Lawyer response schema (simplified)
class LawyerData(BaseModel):
    id: UUID
    name: str
    title: Optional[str] = None
    image_url: Optional[str] = None

# Conversation schemas
class ConversationBase(BaseModel):
    user_id: UUID
    lawyer_id: UUID

class ConversationCreate(ConversationBase):
    pass

class ConversationResponse(BaseModel):
    id: UUID
    lawyer: LawyerData
    last_message: Optional[str] = None
    last_message_date: Optional[datetime] = None
    unread_count: int = 0

    class Config:
        from_attributes = True

# Message schemas
class MessageBase(BaseModel):
    content: str

class MessageCreate(MessageBase):
    user_id: Optional[UUID] = None  # Will be extracted from token if not provided

class MessageInDB(MessageBase):
    id: UUID
    conversation_id: UUID
    from_lawyer: bool
    read: bool
    timestamp: datetime

    class Config:
        from_attributes = True

class MessageResponse(MessageInDB):
    pass

# Response with a list of conversations
class ConversationList(BaseModel):
    conversations: List[ConversationResponse]

# Response with a list of messages
class MessageList(BaseModel):
    messages: List[MessageResponse]

# Simple response for operations
class SuccessResponse(BaseModel):
    success: bool = True