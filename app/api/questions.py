from typing import List, Optional
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Query, status, BackgroundTasks
from sqlalchemy.orm import Session
from uuid import UUID

from app.db.database import get_db
from app.db.repositories import questions as questions_repository
from app.db.repositories import topics as topics_repository
from app.db.repositories import analytics as analytics_repository
from app.schemas.analytics import QuestionViewCreate
from app.schemas.question import (
    QuestionResponse,
    QuestionCreate,
    QuestionUpdate,
    QuestionsList,
)
from app.api.dependencies import get_current_user, get_optional_current_user
from app.models.user import User

router = APIRouter()

@router.get("", response_model=QuestionsList)
async def get_questions(
    db: Session = Depends(get_db),
    topic: Optional[str] = None,
    page: int = Query(1, ge=1),
    size: int = Query(10, ge=1, le=100),
    sort: str = "latest",
):
    """
    List all legal questions with optional filtering
    """
    skip = (page - 1) * size

    # Check if topic is provided as UUID or slug
    topic_id = None
    topic_slug = None

    if topic:
        try:
            # Try to parse as UUID
            topic_id = UUID(topic)
        except ValueError:
            # Not a valid UUID, treat as slug
            topic_slug = topic

    # Get questions and total count
    questions, total = questions_repository.get_questions(
        db=db,
        skip=skip,
        limit=size,
        topic_id=topic_id,
        topic_slug=topic_slug,
        sort=sort,
    )

    # Calculate total pages
    pages = (total + size - 1) // size  # Ceiling division

    # Convert to response format
    response_questions = []
    for question in questions:
        # Get topic IDs
        topic_ids = [topic.id for topic in question.topics]

        # Get answer count
        answer_count = len(question.answers)

        # Format author info
        author = {
            "name": f"{question.user.first_name or ''} {question.user.last_name or ''}".strip(),
            "location": question.location or "Unknown",
        }

        response_questions.append(
            QuestionResponse(
                **{
                    "id": question.id,
                    "title": question.title,
                    "content": question.content,
                    "author": author,
                    "date": question.created_at,
                    "topic_ids": topic_ids,
                    "answer_count": answer_count,
                    "view_count": question.view_count,
                    "user_id": question.user_id,
                    "created_at": question.created_at,
                    "updated_at": question.updated_at,
                    "location": question.location,
                }
            )
        )

    return QuestionsList(
        questions=response_questions, total=total, page=page, size=size, pages=pages
    )


@router.get("/{question_id}", response_model=QuestionResponse)
async def get_question(
    question_id: UUID,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_optional_current_user),
    background_tasks: BackgroundTasks = BackgroundTasks(),
):
    """
    Retrieve a specific question by ID
    """
    question = questions_repository.get_question_by_id(db, question_id)
    if question is None:
        raise HTTPException(status_code=404, detail="Question not found")

    # Increment view count
    question = questions_repository.increment_view_count(db, question)

    # Track question view via analytics
    view_data = {
        "question_id": question_id,
        "user_id": current_user.id if current_user else None,
        "timestamp": datetime.now(),
    }

    # Use background task to track view
    background_tasks.add_task(
        analytics_repository.create_question_view,
        db=db,
        view=QuestionViewCreate(**view_data),
    )

    # Format author info
    author = {
        "name": f"{question.user.first_name or ''} {question.user.last_name or ''}".strip(),
        "location": question.location or "Unknown",
    }

    # Get topic IDs
    topic_ids = [topic.id for topic in question.topics]

    # Get answer count
    answer_count = len(question.answers)

    return QuestionResponse(
        **{
            "id": question.id,
            "title": question.title,
            "content": question.content,
            "user_id": question.user_id,
            "location": question.location,
            "plan_to_hire": question.plan_to_hire,
            "view_count": question.view_count,
            "created_at": question.created_at,
            "updated_at": question.updated_at,
            "author": author,
            "date": question.created_at,
            "topic_ids": topic_ids,
            "answer_count": answer_count,
        }
    )


@router.post("", response_model=QuestionResponse, status_code=status.HTTP_201_CREATED)
async def create_question(
    question: QuestionCreate,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_optional_current_user),
):
    """
    Create a new legal question
    """
    # Validate that all topics exist
    for topic_id in question.topic_ids:
        topic = topics_repository.get_topic_by_id(db, topic_id)
        if not topic:
            raise HTTPException(
                status_code=404, detail=f"Topic with ID {topic_id} not found"
            )

    current_user_id = None
    if current_user:
        current_user_id = current_user.id

    # Create the question
    db_question = questions_repository.create_question(db, question, current_user_id)

    # Format the response
    author = {
        "name": f"{current_user.first_name or ''} {current_user.last_name or ''}".strip(),
        "location": question.location or "Unknown",
    }

    return QuestionResponse(
        **{
            "id": db_question.id,
            "title": db_question.title,
            "content": db_question.content,
            "user_id": db_question.user_id,
            "location": db_question.location,
            "plan_to_hire": db_question.plan_to_hire,
            "view_count": db_question.view_count,
            "created_at": db_question.created_at,
            "updated_at": db_question.updated_at,
            "author": author,
            "date": db_question.created_at,
            "topic_ids": question.topic_ids,
            "answer_count": 0,
        }
    )


@router.patch("/{question_id}", response_model=QuestionResponse)
async def update_question(
    question_id: UUID,
    question: QuestionUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Update a legal question
    """
    db_question = questions_repository.get_question_by_id(db, question_id)
    if db_question is None:
        raise HTTPException(status_code=404, detail="Question not found")

    # Check if the current user is the author of the question
    if db_question.user_id != current_user.id:
        raise HTTPException(
            status_code=403, detail="Not authorized to update this question"
        )

    # Validate topics if provided
    if question.topic_ids:
        for topic_id in question.topic_ids:
            topic = topics_repository.get_topic_by_id(db, topic_id)
            if not topic:
                raise HTTPException(
                    status_code=404, detail=f"Topic with ID {topic_id} not found"
                )

    # Update the question
    updated_question = questions_repository.update_question(db, db_question, question)

    # Format the response
    author = {
        "name": f"{db_question.user.first_name or ''} {db_question.user.last_name or ''}".strip(),
        "location": updated_question.location or "Unknown",
    }

    # Get topic IDs
    topic_ids = questions_repository.get_topic_ids_for_question(db, updated_question.id)

    # Get answer count
    answer_count = len(updated_question.answers)

    return QuestionResponse(
        **{
            "id": updated_question.id,
            "title": updated_question.title,
            "content": updated_question.content,
            "user_id": updated_question.user_id,
            "location": updated_question.location,
            "plan_to_hire": updated_question.plan_to_hire,
            "view_count": updated_question.view_count,
            "created_at": updated_question.created_at,
            "updated_at": updated_question.updated_at,
            "author": author,
            "date": updated_question.created_at,
            "topic_ids": topic_ids,
            "answer_count": answer_count,
        }
    )


@router.delete("/{question_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_question(
    question_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Delete a legal question
    """
    db_question = questions_repository.get_question_by_id(db, question_id)
    if db_question is None:
        raise HTTPException(status_code=404, detail="Question not found")

    # Check if the current user is the author of the question
    if db_question.user_id != current_user.id:
        raise HTTPException(
            status_code=403, detail="Not authorized to delete this question"
        )

    questions_repository.delete_question(db, question_id)
    return None
