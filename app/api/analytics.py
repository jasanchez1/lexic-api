from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status, Body
from sqlalchemy.orm import Session
from uuid import UUID

from app.db.database import get_db
from app.db.repositories import analytics as analytics_repository
from app.db.repositories import lawyers as lawyers_repository
from app.db.repositories import guides as guides_repository
from app.db.repositories import questions as questions_repository
from app.schemas.analytics import (
    ProfileViewCreate, ProfileViewResponse,
    MessageEventCreate, MessageEventResponse,
    CallEventCreate, CallEventResponse,
    ProfileImpressionCreate, ProfileImpressionResponse,
    ListingClickCreate, ListingClickResponse,
    GuideViewCreate, GuideViewResponse,
    QuestionViewCreate, QuestionViewResponse
)
from app.schemas.message import CallCreate, CallCreateResponse
from app.api.dependencies import get_current_user, get_optional_current_user
from app.models.user import User
from app.models.lawyer import Lawyer as LawyerModel

router = APIRouter()

@router.post("/profile-view", response_model=ProfileViewResponse, status_code=status.HTTP_201_CREATED)
async def track_profile_view(
    view: ProfileViewCreate,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_optional_current_user)
):
    """
    Track a profile view
    """
    # Verify lawyer exists
    lawyer = lawyers_repository.get_lawyer_by_id(db, view.lawyer_id)
    if not lawyer:
        raise HTTPException(status_code=404, detail="Lawyer not found")
    
    # Set user_id from current_user if authenticated and not provided
    if current_user and not view.user_id:
        view.user_id = current_user.id
    
    # Create profile view record
    analytics_repository.create_profile_view(db, view)
    
    return ProfileViewResponse(success=True)

@router.post("/message-events", response_model=MessageEventResponse, status_code=status.HTTP_201_CREATED)
async def track_message_event(
    event: MessageEventCreate,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_optional_current_user)
):
    """
    Track a message event (opened, sent, etc.)
    """
    # Verify lawyer exists
    lawyer = lawyers_repository.get_lawyer_by_id(db, event.lawyer_id)
    if not lawyer:
        raise HTTPException(status_code=404, detail="Lawyer not found")
    
    # Set user_id from current_user if authenticated and not provided
    if current_user and not event.user_id:
        event.user_id = current_user.id
    
    # Create message event record
    analytics_repository.create_message_event(db, event)
    
    return MessageEventResponse(success=True)

@router.post("/call", response_model=CallEventResponse, status_code=status.HTTP_201_CREATED)
async def track_call_event(
    event: CallEventCreate,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_optional_current_user)
):
    """
    Track a call event
    """
    # Verify lawyer exists
    lawyer = lawyers_repository.get_lawyer_by_id(db, event.lawyer_id)
    if not lawyer:
        raise HTTPException(status_code=404, detail="Lawyer not found")
    
    # Set user_id from current_user if authenticated and not provided
    if current_user and not event.user_id:
        event.user_id = current_user.id
    
    # Create call event record
    analytics_repository.create_call_event(db, event)
    
    return CallEventResponse(success=True)


@router.post("/profile-impression", response_model=ProfileImpressionResponse, status_code=status.HTTP_201_CREATED)
async def track_profile_impression(
    impression: ProfileImpressionCreate,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_optional_current_user)
):
    """
    Track a profile impression in search results
    """
    # Verify lawyer exists
    lawyer = lawyers_repository.get_lawyer_by_id(db, impression.lawyer_id)
    if not lawyer:
        raise HTTPException(status_code=404, detail="Lawyer not found")
    
    # Set user_id from current_user if authenticated and not provided
    if current_user and not impression.user_id:
        impression.user_id = current_user.id
    
    # Create profile impression record
    analytics_repository.create_profile_impression(db, impression)
    
    return ProfileImpressionResponse(success=True)

@router.post("/listing-click", response_model=ListingClickResponse, status_code=status.HTTP_201_CREATED)
async def track_listing_click(
    click: ListingClickCreate,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_optional_current_user)
):
    """
    Track a click on a lawyer listing
    """
    # Verify lawyer exists
    lawyer = lawyers_repository.get_lawyer_by_id(db, click.lawyer_id)
    if not lawyer:
        raise HTTPException(status_code=404, detail="Lawyer not found")
    
    # Set user_id from current_user if authenticated and not provided
    if current_user and not click.user_id:
        click.user_id = current_user.id
    
    # Create listing click record
    analytics_repository.create_listing_click(db, click)
    
    return ListingClickResponse(success=True)

@router.post("/guide-view", response_model=GuideViewResponse, status_code=status.HTTP_201_CREATED)
async def track_guide_view(
    view: GuideViewCreate,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_optional_current_user)
):
    """
    Track a guide view
    """
    # Verify guide exists
    guide = guides_repository.get_guide_by_id(db, view.guide_id)
    if not guide:
        raise HTTPException(status_code=404, detail="Guide not found")
    
    # Set user_id from current_user if authenticated and not provided
    if current_user and not view.user_id:
        view.user_id = current_user.id
    
    # Create guide view record
    analytics_repository.create_guide_view(db, view)
    
    return GuideViewResponse(success=True)

@router.post("/question-view", response_model=QuestionViewResponse, status_code=status.HTTP_201_CREATED)
async def track_question_view(
    view: QuestionViewCreate,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_optional_current_user)
):
    """
    Track a question view
    """
    # Verify question exists
    question = questions_repository.get_question_by_id(db, view.question_id)
    if not question:
        raise HTTPException(status_code=404, detail="Question not found")
    
    # Set user_id from current_user if authenticated and not provided
    if current_user and not view.user_id:
        view.user_id = current_user.id
    
    # Create question view record
    analytics_repository.create_question_view(db, view)
    
    return QuestionViewResponse(success=True)


@router.get("/lawyers/{lawyer_id}/position-stats", status_code=status.HTTP_200_OK)
async def get_lawyer_position_stats(
    lawyer_id: UUID,
    db: Session = Depends(get_db)
):
    """
    Get statistics about how a lawyer's position in search results affects impressions and clicks
    """
    # Verify lawyer exists
    lawyer = lawyers_repository.get_lawyer_by_id(db, lawyer_id)
    if not lawyer:
        raise HTTPException(status_code=404, detail="Lawyer not found")
    
    # Get position stats
    position_stats = analytics_repository.get_profile_impression_position_stats(db, lawyer_id)
    
    # Optional: Calculate additional metrics like click-through rates by position
    # This would require joining impression and click data
    
    return {
        "success": True,
        "data": {
            "position_stats": position_stats
        }
    }

@router.get("/lawyers/{lawyer_id}/position-stats", status_code=status.HTTP_200_OK)
async def get_lawyer_position_stats(
    lawyer_id: UUID,
    db: Session = Depends(get_db)
):
    """
    Get statistics about how a lawyer's position in search results affects impressions and clicks
    """
    # Verify lawyer exists
    lawyer = lawyers_repository.get_lawyer_by_id(db, lawyer_id)
    if not lawyer:
        raise HTTPException(status_code=404, detail="Lawyer not found")
    
    # Get position stats
    impression_stats = analytics_repository.get_profile_impression_position_stats(db, lawyer_id)
    click_stats = analytics_repository.get_listing_click_position_stats(db, lawyer_id)
    ctr_stats = analytics_repository.get_click_through_rate_by_position(db, lawyer_id)
    
    # Calculate totals
    total_impressions = sum(impression_stats.values())
    total_clicks = sum(click_stats.values())
    overall_ctr = (total_clicks / total_impressions * 100) if total_impressions > 0 else 0
    
    return {
        "success": True,
        "data": {
            "impression_stats": impression_stats,
            "click_stats": click_stats,
            "ctr_by_position": ctr_stats,
            "totals": {
                "impressions": total_impressions,
                "clicks": total_clicks,
                "overall_ctr": round(overall_ctr, 2)
            }
        }
    }


@router.get("/summary", status_code=status.HTTP_200_OK)
async def get_analytics_summary(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get a summary of all analytics data for the current user's lawyer profile
    """
    # Find the lawyer profile associated with this user
    lawyer = db.query(LawyerModel).filter(LawyerModel.user_id == current_user.id).first()
    if not lawyer:
        raise HTTPException(status_code=404, detail="No lawyer profile found for current user")
    
    lawyer_id = lawyer.id
    
    # Get all analytics data
    profile_view_count = analytics_repository.get_profile_view_count(db, lawyer_id)
    message_sent_count = analytics_repository.get_message_event_count(db, lawyer_id, "sent")
    message_read_count = analytics_repository.get_message_event_count(db, lawyer_id, "read")
    call_count = analytics_repository.get_call_event_count(db, lawyer_id)
    call_completed_count = analytics_repository.get_call_event_count(db, lawyer_id, completed_only=True)
    impression_count = analytics_repository.get_profile_impression_count(db, lawyer_id)
    
    # Get position-based statistics
    impression_stats = analytics_repository.get_profile_impression_position_stats(db, lawyer_id)
    click_stats = analytics_repository.get_listing_click_position_stats(db, lawyer_id)
    ctr_stats = analytics_repository.get_click_through_rate_by_position(db, lawyer_id)
    
    # Calculate engagement metrics
    total_clicks = sum(click_stats.values())
    message_rate = (message_sent_count / profile_view_count * 100) if profile_view_count > 0 else 0
    call_rate = (call_count / profile_view_count * 100) if profile_view_count > 0 else 0
    overall_ctr = (total_clicks / impression_count * 100) if impression_count > 0 else 0
    
    return {
        "success": True,
        "data": {
            "profile": {
                "name": lawyer.name,
                "title": lawyer.title,
                "id": str(lawyer.id)
            },
            "counts": {
                "profile_views": profile_view_count,
                "messages_sent": message_sent_count,
                "messages_read": message_read_count,
                "calls": call_count,
                "calls_completed": call_completed_count,
                "impressions": impression_count,
                "clicks": total_clicks
            },
            "rates": {
                "message_rate": round(message_rate, 2),
                "call_rate": round(call_rate, 2),
                "overall_ctr": round(overall_ctr, 2)
            },
            "position_data": {
                "impression_stats": impression_stats,
                "click_stats": click_stats,
                "ctr_by_position": ctr_stats
            }
        }
    }