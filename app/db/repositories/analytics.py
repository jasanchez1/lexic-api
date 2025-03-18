from typing import Optional
from uuid import UUID
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.models.analytics import (
    ProfileView, ProfileViewCount, 
    MessageEvent, MessageEventCount,
    CallEvent, CallEventCount,
    ProfileImpression, ProfileImpressionCount,
    ListingClick, ListingClickCount,
    GuideView, GuideViewCount,
    QuestionView, QuestionViewCount
)
from app.schemas.analytics import (
    ProfileViewCreate, MessageEventCreate, CallEventCreate,
    ProfileImpressionCreate, ListingClickCreate,
    GuideViewCreate, QuestionViewCreate
)

# Profile View repository functions
def create_profile_view(db: Session, view: ProfileViewCreate) -> ProfileView:
    """
    Record a profile view and update the count
    """
    # Create profile view record
    db_view = ProfileView(
        lawyer_id=view.lawyer_id,
        user_id=view.user_id,
        source=view.source,
        timestamp=view.timestamp
    )
    db.add(db_view)
    
    # Update profile view count
    db_count = db.query(ProfileViewCount).filter(
        ProfileViewCount.lawyer_id == view.lawyer_id
    ).first()
    
    if db_count:
        db_count.count += 1
        db_count.updated_at = datetime.now()
    else:
        db_count = ProfileViewCount(
            lawyer_id=view.lawyer_id,
            count=1
        )
        db.add(db_count)
    
    db.commit()
    db.refresh(db_view)
    return db_view

def get_profile_view_count(db: Session, lawyer_id: UUID) -> int:
    """
    Get the profile view count for a lawyer
    """
    db_count = db.query(ProfileViewCount).filter(
        ProfileViewCount.lawyer_id == lawyer_id
    ).first()
    
    return db_count.count if db_count else 0

# Message Event repository functions
def create_message_event(db: Session, event: MessageEventCreate) -> MessageEvent:
    """
    Record a message event and update the count
    """
    # Create message event record
    db_event = MessageEvent(
        lawyer_id=event.lawyer_id,
        user_id=event.user_id,
        status=event.status,
        timestamp=event.timestamp
    )
    db.add(db_event)
    
    # Update message event count
    db_count = db.query(MessageEventCount).filter(
        MessageEventCount.lawyer_id == event.lawyer_id,
        MessageEventCount.status == event.status
    ).first()
    
    if db_count:
        db_count.count += 1
        db_count.updated_at = datetime.now()
    else:
        db_count = MessageEventCount(
            lawyer_id=event.lawyer_id,
            status=event.status,
            count=1
        )
        db.add(db_count)
    
    db.commit()
    db.refresh(db_event)
    return db_event

def get_message_event_count(db: Session, lawyer_id: UUID, status: Optional[str] = None) -> int:
    """
    Get the message event count for a lawyer
    """
    query = db.query(func.sum(MessageEventCount.count)).filter(
        MessageEventCount.lawyer_id == lawyer_id
    )
    
    if status:
        query = query.filter(MessageEventCount.status == status)
    
    count = query.scalar() or 0
    return count

# Call Event repository functions
def create_call_event(db: Session, event: CallEventCreate) -> CallEvent:
    """
    Record a call event and update the count
    """
    # Create call event record
    db_event = CallEvent(
        lawyer_id=event.lawyer_id,
        user_id=event.user_id,
        completed=event.completed,
        timestamp=event.timestamp
    )
    db.add(db_event)
    
    # Update call event count
    db_count = db.query(CallEventCount).filter(
        CallEventCount.lawyer_id == event.lawyer_id
    ).first()
    
    if db_count:
        db_count.count += 1
        if event.completed:
            db_count.completed_count += 1
        db_count.updated_at = datetime.now()
    else:
        db_count = CallEventCount(
            lawyer_id=event.lawyer_id,
            count=1,
            completed_count=1 if event.completed else 0
        )
        db.add(db_count)
    
    db.commit()
    db.refresh(db_event)
    return db_event

def get_call_event_count(db: Session, lawyer_id: UUID, completed_only: bool = False) -> int:
    """
    Get the call event count for a lawyer
    """
    db_count = db.query(CallEventCount).filter(
        CallEventCount.lawyer_id == lawyer_id
    ).first()
    
    if not db_count:
        return 0
    
    return db_count.completed_count if completed_only else db_count.count

# Profile Impression repository functions
def create_profile_impression(db: Session, impression: ProfileImpressionCreate) -> ProfileImpression:
    """
    Record a profile impression and update the count
    """
    # Create profile impression record
    db_impression = ProfileImpression(
        lawyer_id=impression.lawyer_id,
        user_id=impression.user_id,
        search_query=impression.search_query,
        area_slug=impression.area_slug,
        city_slug=impression.city_slug,
        timestamp=impression.timestamp
    )
    db.add(db_impression)
    
    # Update profile impression count
    db_count = db.query(ProfileImpressionCount).filter(
        ProfileImpressionCount.lawyer_id == impression.lawyer_id
    ).first()
    
    if db_count:
        db_count.count += 1
        db_count.updated_at = datetime.now()
    else:
        db_count = ProfileImpressionCount(
            lawyer_id=impression.lawyer_id,
            count=1
        )
        db.add(db_count)
    
    db.commit()
    db.refresh(db_impression)
    return db_impression

def get_profile_impression_count(db: Session, lawyer_id: UUID) -> int:
    """
    Get the profile impression count for a lawyer
    """
    db_count = db.query(ProfileImpressionCount).filter(
        ProfileImpressionCount.lawyer_id == lawyer_id
    ).first()
    
    return db_count.count if db_count else 0

# Listing Click repository functions
def create_listing_click(db: Session, click: ListingClickCreate) -> ListingClick:
    """
    Record a listing click and update the count
    """
    # Create listing click record
    db_click = ListingClick(
        lawyer_id=click.lawyer_id,
        user_id=click.user_id,
        search_query=click.search_query,
        area_slug=click.area_slug,
        city_slug=click.city_slug,
        timestamp=click.timestamp
    )
    db.add(db_click)
    
    # Update listing click count
    db_count = db.query(ListingClickCount).filter(
        ListingClickCount.lawyer_id == click.lawyer_id
    ).first()
    
    if db_count:
        db_count.count += 1
        db_count.updated_at = datetime.now()
    else:
        db_count = ListingClickCount(
            lawyer_id=click.lawyer_id,
            count=1
        )
        db.add(db_count)
    
    db.commit()
    db.refresh(db_click)
    return db_click

def get_listing_click_count(db: Session, lawyer_id: UUID) -> int:
    """
    Get the listing click count for a lawyer
    """
    db_count = db.query(ListingClickCount).filter(
        ListingClickCount.lawyer_id == lawyer_id
    ).first()
    
    return db_count.count if db_count else 0

# Guide View repository functions
def create_guide_view(db: Session, view: GuideViewCreate) -> GuideView:
    """
    Record a guide view and update the count
    """
    # Create guide view record
    db_view = GuideView(
        guide_id=view.guide_id,
        user_id=view.user_id,
        timestamp=view.timestamp
    )
    db.add(db_view)
    
    # Update guide view count
    db_count = db.query(GuideViewCount).filter(
        GuideViewCount.guide_id == view.guide_id
    ).first()
    
    if db_count:
        db_count.count += 1
        db_count.updated_at = datetime.now()
    else:
        db_count = GuideViewCount(
            guide_id=view.guide_id,
            count=1
        )
        db.add(db_count)
    
    db.commit()
    db.refresh(db_view)
    return db_view

def get_guide_view_count(db: Session, guide_id: UUID) -> int:
    """
    Get the guide view count
    """
    db_count = db.query(GuideViewCount).filter(
        GuideViewCount.guide_id == guide_id
    ).first()
    
    return db_count.count if db_count else 0

# Question View repository functions
def create_question_view(db: Session, view: QuestionViewCreate) -> QuestionView:
    """
    Record a question view and update the count
    """
    # Create question view record
    db_view = QuestionView(
        question_id=view.question_id,
        user_id=view.user_id,
        timestamp=view.timestamp
    )
    db.add(db_view)
    
    # Update question view count
    db_count = db.query(QuestionViewCount).filter(
        QuestionViewCount.question_id == view.question_id
    ).first()
    
    if db_count:
        db_count.count += 1
        db_count.updated_at = datetime.now()
    else:
        db_count = QuestionViewCount(
            question_id=view.question_id,
            count=1
        )
        db.add(db_count)
    
    db.commit()
    db.refresh(db_view)
    return db_view

def get_question_view_count(db: Session, question_id: UUID) -> int:
    """
    Get the question view count
    """
    db_count = db.query(QuestionViewCount).filter(
        QuestionViewCount.question_id == question_id
    ).first()
    
    return db_count.count if db_count else 0


def get_profile_impression_position_stats(db: Session, lawyer_id: UUID) -> dict:
    """
    Get statistics about the positions of a lawyer in search results
    Returns a dictionary with position ranges as keys and counts as values
    """
    from sqlalchemy import func, case, between
    
    # Define position ranges
    position_ranges = [
        (1, 3, "top_3"),
        (4, 10, "top_4_10"),
        (11, 20, "top_11_20"),
        (21, 50, "top_21_50"),
        (51, 100, "top_51_100"),
        (101, None, "below_100")
    ]
    
    # Create case statements for each range
    cases = []
    for start, end, label in position_ranges:
        if end:
            cases.append(
                (between(ProfileImpression.position, start, end), label)
            )
        else:
            cases.append(
                (ProfileImpression.position >= start, label)
            )
    
    # Create the query
    query = db.query(
        case(*cases, else_="unknown").label("position_range"),
        func.count().label("count")
    ).filter(
        ProfileImpression.lawyer_id == lawyer_id
    ).group_by(
        "position_range"
    ).order_by(
        "position_range"
    )
    
    # Execute and format results
    results = {}
    for row in query.all():
        results[row.position_range] = row.count
    
    return results

def get_listing_click_position_stats(db: Session, lawyer_id: UUID) -> dict:
    """
    Get statistics about the positions of clicks on lawyer listings in search results
    Returns a dictionary with position ranges as keys and counts as values
    """
    from sqlalchemy import func, case, between
    
    # Define position ranges
    position_ranges = [
        (1, 3, "top_3"),
        (4, 10, "top_4_10"),
        (11, 20, "top_11_20"),
        (21, 50, "top_21_50"),
        (51, 100, "top_51_100"),
        (101, None, "below_100")
    ]
    
    # Create case statements for each range
    cases = []
    for start, end, label in position_ranges:
        if end:
            cases.append(
                (between(ListingClick.position, start, end), label)
            )
        else:
            cases.append(
                (ListingClick.position >= start, label)
            )
    
    # Create the query
    query = db.query(
        case(*cases, else_="unknown").label("position_range"),
        func.count().label("count")
    ).filter(
        ListingClick.lawyer_id == lawyer_id
    ).group_by(
        "position_range"
    ).order_by(
        "position_range"
    )
    
    # Execute and format results
    results = {}
    for row in query.all():
        results[row.position_range] = row.count
    
    return results

def get_click_through_rate_by_position(db: Session, lawyer_id: UUID) -> dict:
    """
    Calculate click-through rate (CTR) by position range
    Returns a dictionary with position ranges as keys and CTR values as values
    """
    # Get impression and click stats
    impression_stats = get_profile_impression_position_stats(db, lawyer_id)
    click_stats = get_listing_click_position_stats(db, lawyer_id)
    
    # Calculate CTR for each position range
    ctr_stats = {}
    for position_range, impressions in impression_stats.items():
        clicks = click_stats.get(position_range, 0)
        ctr = (clicks / impressions * 100) if impressions > 0 else 0
        ctr_stats[position_range] = round(ctr, 2)  # Round to 2 decimal places
    
    return ctr_stats