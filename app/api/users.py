from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from uuid import UUID
from app.api.dependencies import get_current_user
from app.db.database import get_db
from app.db.repositories import users as users_repository
from app.schemas.review import ReviewAuthor, ReviewResponse, ReviewsResponse
from app.schemas.user import User, UserUpdate
import app.db.repositories.reviews as reviews_repository


router = APIRouter()

@router.get("/", response_model=List[User])
async def get_users(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100
):
    """
    Get a list of users
    """
    users = users_repository.get_users(db, skip=skip, limit=limit)
    return users


@router.patch("/{user_id}", response_model=User)
async def update_user(
    user_id: UUID,
    user: UserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Update a user
    """
    # Verify that the current user is the owner of the user
    if current_user.id != user_id:
        raise HTTPException(
            status_code=403, detail="You can only update your own user"
        )

    # Update user
    updated_user = users_repository.update_user(db, current_user, user)

    if not updated_user:
        raise HTTPException(status_code=404, detail="User not found")

    return updated_user



@router.get("/{user_id}/reviews", response_model=ReviewsResponse)
async def get_user_reviews(
    user_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Get reviews for a specific user
    """
    # Verify that the current user is the owner of the review
    if current_user.id != user_id:
        raise HTTPException(
            status_code=403, detail="You can only view your own reviews"
        )

    # Get reviews
    reviews = reviews_repository.get_reviews_by_user(db, user_id)

    stats = reviews_repository.get_review_stats_by_user(db, user_id)

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
