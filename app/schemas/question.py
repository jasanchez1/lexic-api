from typing import Optional, List
from datetime import datetime
from uuid import UUID
from enum import Enum
from pydantic import BaseModel, Field

class PlanToHire(str, Enum):
    yes = "yes"
    no = "no"
    maybe = "maybe"

class QuestionAuthor(BaseModel):
    name: str
    location: Optional[str] = None

class QuestionBase(BaseModel):
    title: str
    content: str
    location: Optional[str] = None
    plan_to_hire: PlanToHire = PlanToHire.maybe

class QuestionCreate(QuestionBase):
    topic_ids: List[UUID]
    
    class Config:
        use_enum_values = True

class QuestionUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    location: Optional[str] = None
    plan_to_hire: Optional[PlanToHire] = None
    topic_ids: Optional[List[UUID]] = None

class QuestionInDB(QuestionBase):
    id: UUID
    user_id: Optional[UUID] = None
    view_count: int = 0
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class QuestionResponse(QuestionInDB):
    """Question schema for API responses"""
    date: datetime
    topic_ids: List[UUID] = []
    answer_count: int = 0
    author: Optional[QuestionAuthor] = None

class QuestionsList(BaseModel):
    """List of questions with pagination"""
    questions: List[QuestionResponse]
    total: int
    page: int
    size: int
    pages: int

