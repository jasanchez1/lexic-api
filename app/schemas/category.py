from typing import Optional, List, Any
from uuid import UUID
from pydantic import BaseModel

class PracticeAreaCategoryBase(BaseModel):
    name: str
    slug: str

class PracticeAreaCategoryCreate(PracticeAreaCategoryBase):
    pass

class PracticeAreaCategoryUpdate(BaseModel):
    name: Optional[str] = None
    slug: Optional[str] = None

class PracticeAreaCategoryInDB(PracticeAreaCategoryBase):
    id: UUID
    
    class Config:
        from_attributes = True

class PracticeAreaCategory(PracticeAreaCategoryInDB):
    """Practice area category schema for API responses"""
    pass

class PracticeAreaCategoryWithAreas(PracticeAreaCategory):
    """Practice area category with areas included"""
    areas: List = []