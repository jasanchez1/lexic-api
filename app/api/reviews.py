from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from uuid import UUID

from app.api.dependencies import get_current_user, get_optional_current_user
from app.db.database import get_db
from app.db.repositories import reviews as reviews_repository
from app.db.repositories import lawyers as lawyers_repository
from app.models.user import User
from app.schemas.review import (
    ReviewResponse,
    ReviewCreate,
    ReviewUpdate,
    ReviewsResponse,
    ReviewAuthor,
)

router = APIRouter()


@router.get("/{lawyer_id}/reviews", response_model=ReviewsResponse)
async def get_lawyer_reviews(lawyer_id: UUID, db: Session = Depends(get_db)):
    """
    Get reviews for a specific lawyer
    """
    # Verify lawyer exists
    lawyer = lawyers_repository.get_lawyer_by_id(db, lawyer_id)
    if not lawyer:
        raise HTTPException(status_code=404, detail="Lawyer not found")

    # Get reviews
    reviews = reviews_repository.get_reviews_by_lawyer(db, lawyer_id)

    # Get review statistics
    stats = reviews_repository.get_review_stats(db, lawyer_id)

    # Format response
    reviews_response = []
    for review in reviews:
        author_name = "Anonymous" if review.is_anonymous else review.author

        reviews_response.append(
            ReviewResponse(
                id=review.id,
                rating=review.rating,
                title=review.title,
                content=review.content,
                author=ReviewAuthor(
                    name=author_name,
                    email=review.author_email,
                ),
                lawyer_id=review.lawyer_id,
                user_id=review.user_id,
                is_hired=review.is_hired,
                is_anonymous=review.is_anonymous,
                created_at=review.created_at,
                date=review.created_at,
            )
        )

    return ReviewsResponse(reviews=reviews_response, stats=stats)


@router.post("/{lawyer_id}/reviews", status_code=status.HTTP_201_CREATED)
async def create_lawyer_review(
    lawyer_id: UUID,
    review: ReviewCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_optional_current_user),
):
    """
    Create a new review for a lawyer
    """
    # Verify lawyer exists
    lawyer = lawyers_repository.get_lawyer_by_id(db, lawyer_id)
    if not lawyer:
        raise HTTPException(status_code=404, detail="Lawyer not found")

    # Ensure the user_id in the review matches the current user
    if current_user and review.user_id != current_user.id:
        raise HTTPException(
            status_code=403,
            detail="User ID in review must match the authenticated user",
        )

    # Create review
    db_review = reviews_repository.create_review(db, review, lawyer_id)

    # update lawyer review score
    lawyers_repository.update_lawyer_review_score(db, lawyer_id, db_review.rating)

    return {
        "success": True,
        "review_id": str(db_review.id),
        "user_id": db_review.user_id,
    }


@router.patch("/{lawyer_id}/reviews/{review_id}", response_model=ReviewResponse)
async def update_lawyer_review(
    lawyer_id: UUID,
    review_id: UUID,
    review: ReviewUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Update an existing review
    """
    # Verify lawyer exists
    lawyer = lawyers_repository.get_lawyer_by_id(db, lawyer_id)
    if not lawyer:
        raise HTTPException(status_code=404, detail="Lawyer not found")

    # Verify review exists and belongs to the lawyer
    db_review = reviews_repository.get_review_by_id(db, review_id)
    if not db_review:
        raise HTTPException(status_code=404, detail="Review not found")

    if db_review.lawyer_id != lawyer_id:
        raise HTTPException(
            status_code=400, detail="Review does not belong to this lawyer"
        )

    # Verify that the current user is the owner of the review
    if db_review.user_id != current_user.id:
        raise HTTPException(
            status_code=403, detail="You can only update your own reviews"
        )

    # Update review
    updated_review = reviews_repository.update_review(db, db_review, review)

    # Format response
    author_name = "Anonymous" if updated_review.is_anonymous else updated_review.author

    return ReviewResponse(
        id=updated_review.id,
        rating=updated_review.rating,
        title=updated_review.title,
        content=updated_review.content,
        author=ReviewAuthor(
            name=author_name,
            email=updated_review.author_email,
        ),
        lawyer_id=updated_review.lawyer_id,
        user_id=updated_review.user_id,  # Added user_id
        is_hired=updated_review.is_hired,
        is_anonymous=updated_review.is_anonymous,
        created_at=updated_review.created_at,
        date=updated_review.created_at,
    )


@router.delete(
    "/{lawyer_id}/reviews/{review_id}", status_code=status.HTTP_204_NO_CONTENT
)
async def delete_lawyer_review(
    lawyer_id: UUID,
    review_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Delete a review
    """
    # Verify lawyer exists
    lawyer = lawyers_repository.get_lawyer_by_id(db, lawyer_id)
    if not lawyer:
        raise HTTPException(status_code=404, detail="Lawyer not found")

    # Verify review exists and belongs to the lawyer
    db_review = reviews_repository.get_review_by_id(db, review_id)
    if not db_review:
        raise HTTPException(status_code=404, detail="Review not found")

    if db_review.lawyer_id != lawyer_id:
        raise HTTPException(
            status_code=400, detail="Review does not belong to this lawyer"
        )

    # Verify that the current user is the owner of the review
    if db_review.user_id != current_user.id:
        raise HTTPException(
            status_code=403, detail="You can only delete your own reviews"
        )

    # Delete review
    reviews_repository.delete_review(db, review_id)
    return None
