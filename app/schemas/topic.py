from typing import Optional, List
from uuid import UUID
from pydantic import BaseModel

class TopicBase(BaseModel):
    name: str
    slug: str
    description: Optional[str] = None

class TopicCreate(TopicBase):
    parent_id: Optional[UUID] = None

class TopicUpdate(BaseModel):
    name: Optional[str] = None
    slug: Optional[str] = None
    description: Optional[str] = None
    parent_id: Optional[UUID] = None

class TopicInDB(TopicBase):
    id: UUID
    parent_id: Optional[UUID] = None
    
    class Config:
        from_attributes = True

class SubtopicResponse(TopicInDB):
    questions_count: Optional[int] = 0

class TopicResponse(TopicInDB):
    """Topic schema for API responses"""
    subtopics: List[SubtopicResponse] = []
    questions_count: Optional[int] = 0

class TopicsList(BaseModel):
    """List of topics"""
    topics: List[TopicResponse]

