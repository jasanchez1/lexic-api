from typing import List, Optional
from datetime import datetime
from uuid import UUID
from pydantic import BaseModel

# Participant data (can be any user)
class ParticipantData(BaseModel):
    id: UUID
    name: str
    title: Optional[str] = None
    image_url: Optional[str] = None

# Conversation schemas
class ConversationResponse(BaseModel):
    id: UUID
    other_participant: ParticipantData  # The other person in the conversation
    last_message: Optional[str] = None
    last_message_date: Optional[datetime] = None

    class Config:
        from_attributes = True

# Message schemas
class MessageCreate(BaseModel):
    content: str

class MessageResponse(BaseModel):
    id: UUID
    conversation_id: UUID
    sender_id: UUID
    content: str
    is_from_me: bool
    read: bool
    timestamp: datetime

    class Config:
        from_attributes = True

# Response with a list of conversations
class ConversationList(BaseModel):
    conversations: List[ConversationResponse]

# Response with a list of messages
class MessageList(BaseModel):
    messages: List[MessageResponse]

# Simple response for operations
class SuccessResponse(BaseModel):
    success: bool = True