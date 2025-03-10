from typing import Optional, List
from datetime import datetime
from uuid import UUID
from pydantic import BaseModel

class AnswerAuthor(BaseModel):
    id: UUID
    name: str
    title: Optional[str] = None
    image_url: Optional[str] = None
    rating: Optional[float] = None
    review_count: Optional[int] = None
    is_verified: bool = False

class ReplyBase(BaseModel):
    content: str

class ReplyCreate(ReplyBase):
    pass

class ReplyInDB(ReplyBase):
    id: UUID
    answer_id: UUID
    user_id: UUID
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class ReplyResponse(ReplyInDB):
    """Reply schema for API responses"""
    author: AnswerAuthor
    date: datetime

class AnswerBase(BaseModel):
    content: str

class AnswerCreate(AnswerBase):
    lawyer_id: Optional[UUID] = None

class AnswerUpdate(BaseModel):
    content: Optional[str] = None

class AnswerInDB(AnswerBase):
    id: UUID
    question_id: UUID
    user_id: UUID
    lawyer_id: Optional[UUID] = None
    is_accepted: bool = False
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class AnswerResponse(AnswerInDB):
    """Answer schema for API responses"""
    author: AnswerAuthor
    date: datetime
    helpful_count: int = 0
    is_helpful: bool = False
    reply_count: int = 0

class AnswersList(BaseModel):
    """List of answers"""
    answers: List[AnswerResponse]

class AnswerHelpfulResponse(BaseModel):
    """Response for marking an answer as helpful"""
    success: bool
    is_helpful: bool
    helpful_count: int

class RepliesList(BaseModel):
    """List of replies"""
    replies: List[ReplyResponse]

