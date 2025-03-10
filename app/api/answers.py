from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status, Body
from sqlalchemy.orm import Session
from uuid import UUID

from app.db.database import get_db
from app.db.repositories import answers as answers_repository
from app.db.repositories import questions as questions_repository
from app.schemas.answer import (
    AnswerResponse,
    AnswerCreate,
    AnswerUpdate,
    AnswerAuthor,
    ReplyResponse,
    ReplyCreate,
    AnswerHelpfulResponse,
)
from app.api.dependencies import get_current_user, get_optional_current_user
from app.models.user import User

router = APIRouter()


@router.get("/questions/{question_id}/answers", response_model=List[AnswerResponse])
async def get_answers_for_question(
    question_id: UUID,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_optional_current_user),
):
    """
    Lists all answers for a specific question
    """
    # Verify the question exists
    question = questions_repository.get_question_by_id(db, question_id)
    if not question:
        raise HTTPException(status_code=404, detail="Question not found")

    # Get all answers for the question
    answers = answers_repository.get_answers_by_question(db, question_id)

    # Format the response
    response_answers = []
    for answer in answers:
        # Format author info
        if answer.lawyer:
            author = AnswerAuthor(
                **{
                    "id": answer.lawyer.id,
                    "name": answer.lawyer.name,
                    "title": answer.lawyer.title,
                    "image_url": answer.lawyer.image_url,
                    "rating": 4.8,  # Placeholder value
                    "review_count": 123,  # Placeholder value
                    "is_verified": answer.lawyer.is_verified,
                }
            )
        else:
            author = AnswerAuthor(
                **{
                    "id": answer.user.id,
                    "name": f"{answer.user.first_name or ''} {answer.user.last_name or ''}".strip(),
                    "title": None,
                    "image_url": None,
                    "rating": None,
                    "review_count": None,
                    "is_verified": False,
                }
            )

        # Get helpful count and status
        helpful_count = answers_repository.get_helpful_count(db, answer.id)
        is_helpful = False
        if current_user:
            is_helpful = answers_repository.is_helpful_for_user(
                db, answer.id, current_user.id
            )

        # Get reply count
        reply_count = len(answer.replies)

        response_answers.append(
            AnswerResponse(
                **{
                    "id": answer.id,
                    "content": answer.content,
                    "question_id": answer.question_id,
                    "user_id": answer.user_id,
                    "lawyer_id": answer.lawyer_id,
                    "is_accepted": answer.is_accepted,
                    "created_at": answer.created_at,
                    "updated_at": answer.updated_at,
                    "author": author,
                    "date": answer.created_at,
                    "helpful_count": helpful_count,
                    "is_helpful": is_helpful,
                    "reply_count": reply_count,
                }
            )
        )

    return response_answers


@router.post(
    "/questions/{question_id}/answers",
    response_model=AnswerResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_answer(
    question_id: UUID,
    answer: AnswerCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Creates a new answer for a question
    """
    # Verify the question exists
    question = questions_repository.get_question_by_id(db, question_id)
    if not question:
        raise HTTPException(status_code=404, detail="Question not found")

    # Create the answer
    db_answer = answers_repository.create_answer(
        db, answer, question_id, current_user.id
    )

    # Format author info
    if db_answer.lawyer:
        author = AnswerAuthor(
            **{
                "id": db_answer.lawyer.id,
                "name": db_answer.lawyer.name,
                "title": db_answer.lawyer.title,
                "image_url": db_answer.lawyer.image_url,
                "rating": 4.8,  # Placeholder value
                "review_count": 123,  # Placeholder value
                "is_verified": db_answer.lawyer.is_verified,
            }
        )
    else:
        author = AnswerAuthor(
            **{
                "id": current_user.id,
                "name": f"{current_user.first_name or ''} {current_user.last_name or ''}".strip(),
                "title": None,
                "image_url": None,
                "rating": None,
                "review_count": None,
                "is_verified": False,
            }
        )

    return AnswerResponse(
        **{
            "id": db_answer.id,
            "content": db_answer.content,
            "question_id": db_answer.question_id,
            "user_id": db_answer.user_id,
            "lawyer_id": db_answer.lawyer_id,
            "is_accepted": db_answer.is_accepted,
            "created_at": db_answer.created_at,
            "updated_at": db_answer.updated_at,
            "author": author,
            "date": db_answer.created_at,
            "helpful_count": 0,
            "is_helpful": False,
            "reply_count": 0,
        }
    )


@router.patch("/answers/{answer_id}", response_model=AnswerResponse)
async def update_answer(
    answer_id: UUID,
    answer: AnswerUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Updates an existing answer
    """
    # Verify the answer exists
    db_answer = answers_repository.get_answer_by_id(db, answer_id)
    if not db_answer:
        raise HTTPException(status_code=404, detail="Answer not found")

    # Check if the current user is the author of the answer
    if db_answer.user_id != current_user.id:
        raise HTTPException(
            status_code=403, detail="Not authorized to update this answer"
        )

    # Update the answer
    updated_answer = answers_repository.update_answer(db, db_answer, answer)

    # Format author info
    if updated_answer.lawyer:
        author = AnswerAuthor(
            **{
                "id": updated_answer.lawyer.id,
                "name": updated_answer.lawyer.name,
                "title": updated_answer.lawyer.title,
                "image_url": updated_answer.lawyer.image_url,
                "rating": 4.8,  # Placeholder value
                "review_count": 123,  # Placeholder value
                "is_verified": updated_answer.lawyer.is_verified,
            }
        )
    else:
        author = AnswerAuthor(
            **{
                "id": current_user.id,
                "name": f"{current_user.first_name or ''} {current_user.last_name or ''}".strip(),
                "title": None,
                "image_url": None,
                "rating": None,
                "review_count": None,
                "is_verified": False,
            }
        )

    # Get helpful count and status
    helpful_count = answers_repository.get_helpful_count(db, updated_answer.id)
    is_helpful = answers_repository.is_helpful_for_user(
        db, updated_answer.id, current_user.id
    )

    # Get reply count
    reply_count = len(updated_answer.replies)

    return AnswerResponse(
        **{
            "id": updated_answer.id,
            "content": updated_answer.content,
            "question_id": updated_answer.question_id,
            "user_id": updated_answer.user_id,
            "lawyer_id": updated_answer.lawyer_id,
            "is_accepted": updated_answer.is_accepted,
            "created_at": updated_answer.created_at,
            "updated_at": updated_answer.updated_at,
            "author": author,
            "date": updated_answer.created_at,
            "helpful_count": helpful_count,
            "is_helpful": is_helpful,
            "reply_count": reply_count,
        }
    )


@router.delete("/answers/{answer_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_answer(
    answer_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Deletes an answer
    """
    # Verify the answer exists
    db_answer = answers_repository.get_answer_by_id(db, answer_id)
    if not db_answer:
        raise HTTPException(status_code=404, detail="Answer not found")

    # Check if the current user is the author of the answer
    if db_answer.user_id != current_user.id:
        raise HTTPException(
            status_code=403, detail="Not authorized to delete this answer"
        )

    answers_repository.delete_answer(db, answer_id)
    return None


@router.post("/answers/{answer_id}/accept", response_model=AnswerResponse)
async def accept_answer(
    answer_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Mark an answer as accepted
    """
    # Verify the answer exists
    db_answer = answers_repository.get_answer_by_id(db, answer_id)
    if not db_answer:
        raise HTTPException(status_code=404, detail="Answer not found")

    # Get the question
    question = questions_repository.get_question_by_id(db, db_answer.question_id)
    if not question:
        raise HTTPException(status_code=404, detail="Question not found")

    # Check if the current user is the author of the question
    if question.user_id != current_user.id:
        raise HTTPException(
            status_code=403, detail="Only the question author can accept an answer"
        )

    # Mark the answer as accepted
    accepted_answer = answers_repository.mark_as_accepted(db, db_answer)

    # Format author info
    if accepted_answer.lawyer:
        author = AnswerAuthor(
            **{
                "id": accepted_answer.lawyer.id,
                "name": accepted_answer.lawyer.name,
                "title": accepted_answer.lawyer.title,
                "image_url": accepted_answer.lawyer.image_url,
                "rating": 4.8,  # Placeholder value
                "review_count": 123,  # Placeholder value
                "is_verified": accepted_answer.lawyer.is_verified,
            }
        )
    else:
        user = accepted_answer.user
        author = AnswerAuthor(
            **{
                "id": user.id,
                "name": f"{user.first_name or ''} {user.last_name or ''}".strip(),
                "title": None,
                "image_url": None,
                "rating": None,
                "review_count": None,
                "is_verified": False,
            }
        )

    # Get helpful count and status
    helpful_count = answers_repository.get_helpful_count(db, accepted_answer.id)
    is_helpful = answers_repository.is_helpful_for_user(
        db, accepted_answer.id, current_user.id
    )

    # Get reply count
    reply_count = len(accepted_answer.replies)

    return AnswerResponse(
        **{
            "id": accepted_answer.id,
            "content": accepted_answer.content,
            "question_id": accepted_answer.question_id,
            "user_id": accepted_answer.user_id,
            "lawyer_id": accepted_answer.lawyer_id,
            "is_accepted": accepted_answer.is_accepted,
            "created_at": accepted_answer.created_at,
            "updated_at": accepted_answer.updated_at,
            "author": author,
            "date": accepted_answer.created_at,
            "helpful_count": helpful_count,
            "is_helpful": is_helpful,
            "reply_count": reply_count,
        }
    )


@router.post("/answers/{answer_id}/helpful", response_model=AnswerHelpfulResponse)
async def toggle_helpful(
    answer_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Marks an answer as helpful or unhelpful (toggles state)
    """
    # Verify the answer exists
    db_answer = answers_repository.get_answer_by_id(db, answer_id)
    if not db_answer:
        raise HTTPException(status_code=404, detail="Answer not found")

    # Toggle helpful status
    is_helpful, helpful_count = answers_repository.toggle_helpful(
        db, answer_id, current_user.id
    )

    return AnswerHelpfulResponse(
        **{"success": True, "is_helpful": is_helpful, "helpful_count": helpful_count}
    )


@router.get("/answers/{answer_id}/replies", response_model=List[ReplyResponse])
async def get_replies_for_answer(answer_id: UUID, db: Session = Depends(get_db)):
    """
    Lists all replies for a specific answer
    """
    # Verify the answer exists
    db_answer = answers_repository.get_answer_by_id(db, answer_id)
    if not db_answer:
        raise HTTPException(status_code=404, detail="Answer not found")

    # Get all replies for the answer
    replies = answers_repository.get_replies_by_answer(db, answer_id)

    # Format the response
    response_replies = []
    for reply in replies:
        # Format author info
        author = {
            "id": reply.user.id,
            "name": f"{reply.user.first_name or ''} {reply.user.last_name or ''}".strip(),
            "title": None,
            "image_url": None,
            "rating": None,
            "review_count": None,
            "is_verified": False,
        }

        response_replies.append(
            {
                "id": reply.id,
                "content": reply.content,
                "answer_id": reply.answer_id,
                "user_id": reply.user_id,
                "created_at": reply.created_at,
                "updated_at": reply.updated_at,
                "author": author,
                "date": reply.created_at,
            }
        )

    return response_replies


@router.post(
    "/answers/{answer_id}/replies",
    response_model=ReplyResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_reply(
    answer_id: UUID,
    reply: ReplyCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Creates a new reply to an answer
    """
    # Verify the answer exists
    db_answer = answers_repository.get_answer_by_id(db, answer_id)
    if not db_answer:
        raise HTTPException(status_code=404, detail="Answer not found")

    # Create the reply
    db_reply = answers_repository.create_reply(db, reply, answer_id, current_user.id)

    # Format author info
    author = AnswerAuthor(
        **{
            "id": current_user.id,
            "name": f"{current_user.first_name or ''} {current_user.last_name or ''}".strip(),
            "title": None,
            "image_url": None,
            "rating": None,
            "review_count": None,
            "is_verified": False,
        }
    )

    return ReplyResponse(
        **{
            "id": db_reply.id,
            "content": db_reply.content,
            "answer_id": db_reply.answer_id,
            "user_id": db_reply.user_id,
            "created_at": db_reply.created_at,
            "updated_at": db_reply.updated_at,
            "author": author,
            "date": db_reply.created_at,
        }
    )


@router.delete("/replies/{reply_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_reply(
    reply_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Deletes a reply
    """
    # Verify the reply exists
    db_reply = answers_repository.get_reply_by_id(db, reply_id)
    if not db_reply:
        raise HTTPException(status_code=404, detail="Reply not found")

    # Check if the current user is the author of the reply
    if db_reply.user_id != current_user.id:
        raise HTTPException(
            status_code=403, detail="Not authorized to delete this reply"
        )

    answers_repository.delete_reply(db, reply_id)
    return None
