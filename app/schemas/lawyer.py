from typing import List, Optional
from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, EmailStr

class LawyerAreaAssociation(BaseModel):
    area_id: UUID
    experience_score: int = 0

class LawyerPracticeArea(BaseModel):
    id: str
    name: str
    slug: str
    experience_score: int = 0

class LawyerBase(BaseModel):
    name: str
    email: EmailStr
    title: Optional[str] = None
    bio: Optional[str] = None
    phone: Optional[str] = None
    city: Optional[str] = None
    image_url: Optional[str] = None
    languages: Optional[List[str]] = None
    catchphrase: Optional[str] = None
    professional_start_date: Optional[datetime] = None

class LawyerCreate(LawyerBase):
    user_id: Optional[UUID] = None
    areas: Optional[List[LawyerAreaAssociation]] = None

class LawyerUpdate(BaseModel):
    name: Optional[str] = None
    title: Optional[str] = None
    bio: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[EmailStr] = None
    city: Optional[str] = None
    image_url: Optional[str] = None
    languages: Optional[List[str]] = None
    catchphrase: Optional[str] = None
    professional_start_date: Optional[datetime] = None
    areas: Optional[List[LawyerAreaAssociation]] = None

class LawyerInDB(LawyerBase):
    id: UUID
    user_id: Optional[UUID] = None
    is_verified: bool = False
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class Lawyer(LawyerInDB):
    """Lawyer schema for API responses"""
    areas: List[LawyerPracticeArea] = []
    review_score: float = 0.0
    review_count: int = 0

class LawyerDetail(Lawyer):
    """Detailed lawyer schema with all information"""
    pass

class LawyerList(BaseModel):
    """Schema for listing lawyers with pagination"""
    lawyers: List[Lawyer]
    total: int
    page: int
    size: int
    pages: int

class LawyerSearchParams(BaseModel):
    """Schema for lawyer search parameters"""
    area: Optional[str] = None
    city: Optional[str] = None
    query: Optional[str] = None
    sort: Optional[str] = "best_match"  # best_match, highest_rating, most_experience
    page: int = 1
    size: int = 10