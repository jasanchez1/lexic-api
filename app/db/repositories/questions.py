from typing import List, Optional, Dict, Tuple
from uuid import UUID
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func, or_, and_, desc, asc

from app.models.question import Question
from app.models.topic import Topic, QuestionTopic
from app.models.user import User
from app.models.answer import Answer
from app.schemas.question import QuestionCreate, QuestionUpdate

def get_question_by_id(db: Session, question_id: UUID) -> Optional[Question]:
    """
    Get a question by ID with eager-loaded relationships
    """
    return db.query(Question).options(
        joinedload(Question.user),
        joinedload(Question.topics),
        joinedload(Question.answers)
    ).filter(Question.id == question_id).first()

def increment_view_count(db: Session, question: Question) -> Question:
    """
    Increment the view count of a question
    """
    question.view_count += 1
    db.add(question)
    db.commit()
    db.refresh(question)
    return question

def get_questions(
    db: Session,
    skip: int = 0,
    limit: int = 10,
    topic_id: Optional[UUID] = None,
    topic_slug: Optional[str] = None,
    user_id: Optional[UUID] = None,
    sort: str = "latest"
) -> Tuple[List[Question], int]:
    """
    Get questions with filtering and pagination
    """
    # Base query with eager loads
    query = db.query(Question).options(
        joinedload(Question.user),
        joinedload(Question.topics)
    )
    
    # Apply filters
    if topic_id:
        query = query.join(QuestionTopic).filter(QuestionTopic.topic_id == topic_id)
    
    if topic_slug:
        query = query.join(QuestionTopic).join(Topic).filter(Topic.slug == topic_slug)

    if user_id:
        query = query.filter(Question.user_id == user_id)
    
    # Get total count before pagination
    total = query.count()

    # Apply sorting
    if sort == "latest":
        query = query.order_by(desc(Question.created_at))
    elif sort == "oldest":
        query = query.order_by(asc(Question.created_at))
    elif sort == "most_views":
        query = query.order_by(desc(Question.view_count))
    elif sort == "most_answers":
        # Subquery to count answers
        answer_count = db.query(
            Answer.question_id,
            func.count(Answer.id).label('count')
        ).group_by(Answer.question_id).subquery()
        
        query = query.outerjoin(
            answer_count,
            Question.id == answer_count.c.question_id
        ).order_by(desc(answer_count.c.count.nullsfirst()))
    
    # Apply pagination
    questions = query.offset(skip).limit(limit).all()
    
    return questions, total

def create_question(db: Session, question_in: QuestionCreate, user_id: UUID) -> Question:
    """
    Create a new question with topic relationships
    """
    # Create question first
    db_question = Question(
        title=question_in.title,
        content=question_in.content,
        user_id=user_id,
        location=question_in.location,
        plan_to_hire=question_in.plan_to_hire
    )
    db.add(db_question)
    db.flush()  # Flush to get the ID
    
    # Now add topic relationships
    for topic_id in question_in.topic_ids:
        db.add(QuestionTopic(question_id=db_question.id, topic_id=topic_id))
    
    db.commit()
    db.refresh(db_question)
    return db_question

def update_question(db: Session, question: Question, question_in: QuestionUpdate) -> Question:
    """
    Update a question and its topic relationships
    """
    # Update basic fields
    update_data = question_in.dict(exclude={"topic_ids"}, exclude_unset=True)
    for key, value in update_data.items():
        setattr(question, key, value)
    
    # Update topic relationships if provided
    if question_in.topic_ids is not None:
        # Remove existing relationships
        db.query(QuestionTopic).filter(QuestionTopic.question_id == question.id).delete()
        
        # Add new relationships
        for topic_id in question_in.topic_ids:
            db.add(QuestionTopic(question_id=question.id, topic_id=topic_id))
    
    db.add(question)
    db.commit()
    db.refresh(question)
    return question

def delete_question(db: Session, question_id: UUID) -> None:
    """
    Delete a question
    """
    question = db.query(Question).filter(Question.id == question_id).first()
    if question:
        db.delete(question)
        db.commit()
    return None

def get_topic_ids_for_question(db: Session, question_id: UUID) -> List[UUID]:
    """
    Get the topic IDs for a question
    """
    topic_ids = db.query(QuestionTopic.topic_id).filter(
        QuestionTopic.question_id == question_id
    ).all()
    return [topic_id for (topic_id,) in topic_ids]

