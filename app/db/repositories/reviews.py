from typing import List, Optional, Dict
from uuid import UUID
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.models.review import Review
from app.schemas.review import ReviewCreate, ReviewUpdate, ReviewStats

def get_review_by_id(db: Session, review_id: UUID) -> Optional[Review]:
    """
    Get a review by ID
    """
    return db.query(Review).filter(Review.id == review_id).first()

def get_reviews_by_lawyer(db: Session, lawyer_id: UUID) -> List[Review]:
    """
    Get all reviews for a lawyer
    """
    return db.query(Review).filter(Review.lawyer_id == lawyer_id).order_by(Review.created_at.desc()).all()

def get_review_stats(db: Session, lawyer_id: UUID) -> ReviewStats:
    """
    Get review statistics for a lawyer
    """
    reviews = db.query(Review).filter(Review.lawyer_id == lawyer_id).all()
    
    if not reviews:
        return ReviewStats(
            average=0.0,
            total=0,
            distribution={"5": 0, "4": 0, "3": 0, "2": 0, "1": 0}
        )
    
    total = len(reviews)
    average = sum(review.rating for review in reviews) / total if total > 0 else 0
    
    # Calculate distribution
    distribution = {"5": 0, "4": 0, "3": 0, "2": 0, "1": 0}
    for review in reviews:
        distribution[str(review.rating)] = distribution.get(str(review.rating), 0) + 1
    
    # Convert to percentages
    distribution = {k: round(v / total * 100) for k, v in distribution.items()}
    
    return ReviewStats(
        average=round(average, 1),
        total=total,
        distribution=distribution
    )

def create_review(db: Session, review: ReviewCreate, lawyer_id: UUID) -> Review:
    """
    Create a new review
    """
    db_review = Review(
        rating=review.rating,
        title=review.title,
        content=review.content,
        author=review.author.name,
        author_email=review.author.email,
        lawyer_id=lawyer_id,
        is_hired=review.is_hired,
        is_anonymous=review.is_anonymous
    )
    db.add(db_review)
    db.commit()
    db.refresh(db_review)
    return db_review

def update_review(db: Session, review: Review, review_data: ReviewUpdate) -> Review:
    """
    Update a review
    """
    update_data = review_data.dict(exclude_unset=True)
    
    for key, value in update_data.items():
        setattr(review, key, value)
        
    db.add(review)
    db.commit()
    db.refresh(review)
    return review

def delete_review(db: Session, review_id: UUID) -> None:
    """
    Delete a review
    """
    review = db.query(Review).filter(Review.id == review_id).first()
    if review:
        db.delete(review)
        db.commit()
    return None
