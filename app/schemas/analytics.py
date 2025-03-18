from datetime import datetime
from typing import Optional
from uuid import UUID
from pydantic import BaseModel


# Base response models
class SuccessResponse(BaseModel):
    success: bool = True


class ErrorResponse(BaseModel):
    success: bool = False
    error: str


# Profile View
class ProfileViewCreate(BaseModel):
    lawyer_id: UUID
    user_id: Optional[UUID] = None
    source: Optional[str] = None
    timestamp: datetime


class ProfileViewResponse(SuccessResponse):
    data: Optional[dict] = None


# Message Event
class MessageEventCreate(BaseModel):
    lawyer_id: UUID
    user_id: Optional[UUID] = None
    status: str  # "opened", "sent", etc.
    timestamp: datetime


class MessageEventResponse(SuccessResponse):
    data: Optional[dict] = None


# Call Event
class CallEventCreate(BaseModel):
    lawyer_id: UUID
    user_id: Optional[UUID] = None
    completed: bool = False
    timestamp: datetime


class CallEventResponse(SuccessResponse):
    data: Optional[dict] = None


# Profile Impression
class ProfileImpressionCreate(BaseModel):
    lawyer_id: UUID
    user_id: Optional[UUID] = None
    search_query: Optional[str] = None
    area_slug: Optional[str] = None
    city_slug: Optional[str] = None
    position: Optional[int] = None
    timestamp: datetime


class ProfileImpressionResponse(SuccessResponse):
    data: Optional[dict] = None


class ListingClickCreate(BaseModel):
    lawyer_id: UUID
    user_id: Optional[UUID] = None
    search_query: Optional[str] = None
    area_slug: Optional[str] = None
    city_slug: Optional[str] = None
    position: Optional[int] = None  # Position in search results
    timestamp: datetime


class ListingClickResponse(SuccessResponse):
    data: Optional[dict] = None


# Guide View
class GuideViewCreate(BaseModel):
    guide_id: UUID
    user_id: Optional[UUID] = None
    timestamp: datetime


class GuideViewResponse(SuccessResponse):
    data: Optional[dict] = None


# Question View
class QuestionViewCreate(BaseModel):
    question_id: UUID
    user_id: Optional[UUID] = None
    timestamp: datetime


class QuestionViewResponse(SuccessResponse):
    data: Optional[dict] = None
