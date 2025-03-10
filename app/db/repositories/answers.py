from typing import List, Optional, Tuple
from uuid import UUID
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func, desc, asc

from app.models.answer import Answer, Reply, answer_helpful_votes
from app.models.user import User
from app.schemas.answer import AnswerCreate, AnswerUpdate, ReplyCreate

def get_answer_by_id(db: Session, answer_id: UUID) -> Optional[Answer]:
    """
    Get an answer by ID with eager-loaded relationships
    """
    return db.query(Answer).options(
        joinedload(Answer.user),
        joinedload(Answer.lawyer),
        joinedload(Answer.replies).joinedload(Reply.user)
    ).filter(Answer.id == answer_id).first()

def get_answers_by_question(db: Session, question_id: UUID) -> List[Answer]:
    """
    Get all answers for a question
    """
    return db.query(Answer).options(
        joinedload(Answer.user),
        joinedload(Answer.lawyer),
        joinedload(Answer.replies)
    ).filter(Answer.question_id == question_id).order_by(
        desc(Answer.is_accepted),
        desc(Answer.created_at)
    ).all()

def create_answer(db: Session, answer_in: AnswerCreate, question_id: UUID, user_id: UUID) -> Answer:
    """
    Create a new answer
    """
    db_answer = Answer(
        content=answer_in.content,
        question_id=question_id,
        user_id=user_id,
        lawyer_id=answer_in.lawyer_id
    )
    db.add(db_answer)
    db.commit()
    db.refresh(db_answer)
    return db_answer

def update_answer(db: Session, answer: Answer, answer_in: AnswerUpdate) -> Answer:
    """
    Update an answer
    """
    update_data = answer_in.dict(exclude_unset=True)
    
    for key, value in update_data.items():
        setattr(answer, key, value)
        
    db.add(answer)
    db.commit()
    db.refresh(answer)
    return answer

def delete_answer(db: Session, answer_id: UUID) -> None:
    """
    Delete an answer
    """
    answer = db.query(Answer).filter(Answer.id == answer_id).first()
    if answer:
        db.delete(answer)
        db.commit()
    return None

def mark_as_accepted(db: Session, answer: Answer) -> Answer:
    """
    Mark an answer as accepted and unmark any previously accepted answers
    """
    # First, unmark any previously accepted answers for this question
    db.query(Answer).filter(
        Answer.question_id == answer.question_id,
        Answer.is_accepted == True
    ).update({"is_accepted": False})
    
    # Now mark this answer as accepted
    answer.is_accepted = True
    db.add(answer)
    db.commit()
    db.refresh(answer)
    return answer

def toggle_helpful(db: Session, answer_id: UUID, user_id: UUID) -> Tuple[bool, int]:
    """
    Toggle the helpful status of an answer for a user
    Returns (is_helpful, helpful_count)
    """
    # Check if the user has already marked this answer as helpful
    existing = db.query(answer_helpful_votes).filter(
        answer_helpful_votes.c.answer_id == answer_id,
        answer_helpful_votes.c.user_id == user_id
    ).first()
    
    if existing:
        # Remove the helpful mark
        db.execute(
            answer_helpful_votes.delete().where(
                answer_helpful_votes.c.answer_id == answer_id,
                answer_helpful_votes.c.user_id == user_id
            )
        )
        is_helpful = False
    else:
        # Add the helpful mark
        db.execute(
            answer_helpful_votes.insert().values(
                answer_id=answer_id,
                user_id=user_id
            )
        )
        is_helpful = True
    
    db.commit()
    
    # Get the updated count
    helpful_count = db.query(func.count(answer_helpful_votes.c.user_id)).filter(
        answer_helpful_votes.c.answer_id == answer_id
    ).scalar()
    
    return is_helpful, helpful_count

def is_helpful_for_user(db: Session, answer_id: UUID, user_id: UUID) -> bool:
    """
    Check if an answer is marked as helpful by a user
    """
    return db.query(answer_helpful_votes).filter(
        answer_helpful_votes.c.answer_id == answer_id,
        answer_helpful_votes.c.user_id == user_id
    ).first() is not None

def get_helpful_count(db: Session, answer_id: UUID) -> int:
    """
    Get the helpful count for an answer
    """
    return db.query(func.count(answer_helpful_votes.c.user_id)).filter(
        answer_helpful_votes.c.answer_id == answer_id
    ).scalar()

# Reply methods
def get_reply_by_id(db: Session, reply_id: UUID) -> Optional[Reply]:
    """
    Get a reply by ID
    """
    return db.query(Reply).options(
        joinedload(Reply.user)
    ).filter(Reply.id == reply_id).first()

def get_replies_by_answer(db: Session, answer_id: UUID) -> List[Reply]:
    """
    Get all replies for an answer
    """
    return db.query(Reply).options(
        joinedload(Reply.user)
    ).filter(Reply.answer_id == answer_id).order_by(
        asc(Reply.created_at)
    ).all()

def create_reply(db: Session, reply_in: ReplyCreate, answer_id: UUID, user_id: UUID) -> Reply:
    """
    Create a new reply
    """
    db_reply = Reply(
        content=reply_in.content,
        answer_id=answer_id,
        user_id=user_id
    )
    db.add(db_reply)
    db.commit()
    db.refresh(db_reply)
    return db_reply

def update_reply(db: Session, reply: Reply, content: str) -> Reply:
    """
    Update a reply
    """
    reply.content = content
    db.add(reply)
    db.commit()
    db.refresh(reply)
    return reply

def delete_reply(db: Session, reply_id: UUID) -> None:
    """
    Delete a reply
    """
    reply = db.query(Reply).filter(Reply.id == reply_id).first()
    if reply:
        db.delete(reply)
        db.commit()
    return None

