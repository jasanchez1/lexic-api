from typing import Optional
from uuid import UUID
from pydantic import BaseModel

from app.schemas.category import PracticeAreaCategory

class PracticeAreaBase(BaseModel):
    name: str
    slug: str
    category_id: UUID
    description: Optional[str] = None

class PracticeAreaCreate(PracticeAreaBase):
    pass

class PracticeAreaUpdate(BaseModel):
    name: Optional[str] = None
    slug: Optional[str] = None
    category_id: Optional[UUID] = None
    description: Optional[str] = None

class PracticeAreaInDB(PracticeAreaBase):
    id: UUID
    
    class Config:
        from_attributes = True

class PracticeArea(PracticeAreaInDB):
    """Practice area schema for API responses"""
    pass

class PracticeAreaWithCount(PracticeArea):
    lawyer_count: int = 0