from datetime import datetime
from typing import Optional
from uuid import UUID

from fastapi import BackgroundTasks, Depends
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.db.repositories import analytics as analytics_repository
from app.schemas.analytics import (
    ProfileViewCreate,
    MessageEventCreate,
    CallEventCreate,
    ProfileImpressionCreate,
    ListingClickCreate,
    GuideViewCreate,
    QuestionViewCreate,
)
from app.models.user import User


def track_profile_view_async(
    background_tasks: BackgroundTasks,
    lawyer_id: UUID,
    user_id: Optional[UUID] = None,
    source: Optional[str] = None,
    db: Session = None,
):
    """
    Track a profile view asynchronously
    """
    view = ProfileViewCreate(
        lawyer_id=lawyer_id, user_id=user_id, source=source, timestamp=datetime.now()
    )

    background_tasks.add_task(analytics_repository.create_profile_view, db, view)


def track_message_event_async(
    background_tasks: BackgroundTasks,
    lawyer_id: UUID,
    status: str,
    user_id: Optional[UUID] = None,
    db: Session = None,
):
    """
    Track a message event asynchronously
    """
    event = MessageEventCreate(
        lawyer_id=lawyer_id, user_id=user_id, status=status, timestamp=datetime.now()
    )

    background_tasks.add_task(analytics_repository.create_message_event, db, event)


def track_call_event_async(
    background_tasks: BackgroundTasks,
    lawyer_id: UUID,
    completed: bool = False,
    user_id: Optional[UUID] = None,
    db: Session = None,
):
    """
    Track a call event asynchronously
    """
    event = CallEventCreate(
        lawyer_id=lawyer_id,
        user_id=user_id,
        completed=completed,
        timestamp=datetime.now(),
    )

    background_tasks.add_task(analytics_repository.create_call_event, db, event)


def track_profile_impression_async(
    background_tasks: BackgroundTasks,
    lawyer_id: UUID,
    search_query: Optional[str] = None,
    area_slug: Optional[str] = None,
    city_slug: Optional[str] = None,
    position: Optional[int] = None,
    user_id: Optional[UUID] = None,
    db: Session = None,
):
    """
    Track a profile impression asynchronously
    """
    impression = ProfileImpressionCreate(
        lawyer_id=lawyer_id,
        user_id=user_id,
        search_query=search_query,
        area_slug=area_slug,
        city_slug=city_slug,
        position=position,
        timestamp=datetime.now(),
    )

    background_tasks.add_task(
        analytics_repository.create_profile_impression, db, impression
    )


def track_listing_click_async(
    background_tasks: BackgroundTasks,
    lawyer_id: UUID,
    search_query: Optional[str] = None,
    area_slug: Optional[str] = None,
    city_slug: Optional[str] = None,
    position: Optional[int] = None,
    user_id: Optional[UUID] = None,
    db: Session = None
):
    """
    Track a listing click asynchronously
    """
    click = ListingClickCreate(
        lawyer_id=lawyer_id,
        user_id=user_id,
        search_query=search_query,
        area_slug=area_slug,
        city_slug=city_slug,
        position=position,
        timestamp=datetime.now()
    )
    
    background_tasks.add_task(analytics_repository.create_listing_click, db, click)


def track_guide_view_async(
    background_tasks: BackgroundTasks,
    guide_id: UUID,
    user_id: Optional[UUID] = None,
    db: Session = None,
):
    """
    Track a guide view asynchronously
    """
    view = GuideViewCreate(guide_id=guide_id, user_id=user_id, timestamp=datetime.now())

    background_tasks.add_task(analytics_repository.create_guide_view, db, view)


def track_question_view_async(
    background_tasks: BackgroundTasks,
    question_id: UUID,
    user_id: Optional[UUID] = None,
    db: Session = None,
):
    """
    Track a question view asynchronously
    """
    view = QuestionViewCreate(
        question_id=question_id, user_id=user_id, timestamp=datetime.now()
    )

    background_tasks.add_task(analytics_repository.create_question_view, db, view)
