from typing import Optional, List, Dict
from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, EmailStr


class ReviewBase(BaseModel):
    rating: int
    title: str
    content: str
    is_hired: bool = False
    is_anonymous: bool = False


class ReviewAuthor(BaseModel):
    name: str
    email: Optional[EmailStr] = None


class ReviewCreate(ReviewBase):
    author: ReviewAuthor
    user_id: Optional[UUID] = None


class ReviewUpdate(BaseModel):
    rating: Optional[int] = None
    title: Optional[str] = None
    content: Optional[str] = None
    is_hired: Optional[bool] = None
    is_anonymous: Optional[bool] = None


class ReviewInDB(ReviewBase):
    id: UUID
    author_name: str
    lawyer_id: UUID
    created_at: datetime
    user_id: Optional[UUID]

    class Config:
        from_attributes = True


class ReviewResponse(ReviewBase):
    """Review schema for API responses"""

    id: UUID
    author: ReviewAuthor
    lawyer_id: UUID
    created_at: datetime
    date: datetime
    user_id: Optional[UUID]


class ReviewStats(BaseModel):
    average: float
    total: int
    distribution: Dict[str, int]


class ReviewsResponse(BaseModel):
    reviews: List[ReviewResponse]
    stats: ReviewStats


class ReviewCreateResponse(BaseModel):
    success: bool
    review_id: str
    user_id: Optional[UUID]
