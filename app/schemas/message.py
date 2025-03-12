from typing import Optional
from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, EmailStr


class MessageBase(BaseModel):
    name: str
    email: EmailStr
    phone: Optional[str] = None
    message: str


class MessageCreate(MessageBase):
    user_id: UUID


class MessageInDB(MessageBase):
    id: UUID
    lawyer_id: UUID
    user_id: UUID
    read: bool
    created_at: datetime

    class Config:
        from_attributes = True


class MessageCreateResponse(BaseModel):
    success: bool
    message_id: str
    user_id: UUID


class CallCreate(BaseModel):
    completed: bool
    timestamp: datetime


class CallInDB(BaseModel):
    id: UUID
    lawyer_id: UUID
    completed: bool
    timestamp: datetime
    created_at: datetime

    class Config:
        from_attributes = True


class CallCreateResponse(BaseModel):
    success: bool
