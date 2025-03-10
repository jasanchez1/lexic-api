from typing import List, Optional, Dict
from uuid import UUID
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func

from app.models.topic import Topic, QuestionTopic
from app.models.question import Question
from app.schemas.topic import TopicCreate, TopicUpdate

def get_topic_by_id(db: Session, topic_id: UUID) -> Optional[Topic]:
    """
    Get a topic by ID with eager-loaded subtopics
    """
    return db.query(Topic).options(
        joinedload(Topic.subtopics)
    ).filter(Topic.id == topic_id).first()

def get_topic_by_slug(db: Session, slug: str) -> Optional[Topic]:
    """
    Get a topic by slug with eager-loaded subtopics
    """
    return db.query(Topic).options(
        joinedload(Topic.subtopics)
    ).filter(Topic.slug == slug).first()

def get_topics_with_counts(db: Session) -> List[Dict]:
    """
    Get all topics with question counts
    """
    # Get top-level topics directly
    parent_topics = db.query(Topic).filter(Topic.parent_id.is_(None)).all()
    
    # Get all topic IDs, including both parent and subtopic IDs
    all_topic_ids = [topic.id for topic in parent_topics]
    
    # Create a map of parent_id to subtopics
    subtopics_map = {}
    
    # Get all subtopics for these parent topics
    subtopics = db.query(Topic).filter(Topic.parent_id.in_(all_topic_ids)).all()
    
    # Group subtopics by parent_id
    for subtopic in subtopics:
        if subtopic.parent_id not in subtopics_map:
            subtopics_map[subtopic.parent_id] = []
        subtopics_map[subtopic.parent_id].append(subtopic)
    
    # Count questions for each topic
    topic_counts = {}
    for topic_id, in db.query(QuestionTopic.topic_id).distinct():
        count = db.query(func.count(QuestionTopic.question_id)).filter(
            QuestionTopic.topic_id == topic_id
        ).scalar()
        topic_counts[str(topic_id)] = count
    
    # Build result with counts
    result = []
    for topic in parent_topics:
        topic_id_str = str(topic.id)
        question_count = topic_counts.get(topic_id_str, 0)
        
        # Process subtopics
        subtopics_with_counts = []
        for subtopic in subtopics_map.get(topic.id, []):
            subtopic_id_str = str(subtopic.id)
            subtopic_count = topic_counts.get(subtopic_id_str, 0)
            subtopics_with_counts.append({
                "id": subtopic.id,
                "name": subtopic.name,
                "slug": subtopic.slug,
                "description": subtopic.description,
                "questions_count": subtopic_count,
                "parent_id": subtopic.parent_id
            })
        
        result.append({
            "id": topic.id,
            "name": topic.name,
            "slug": topic.slug,
            "description": topic.description,
            "questions_count": question_count,
            "subtopics": subtopics_with_counts,
            "parent_id": topic.parent_id
        })
    
    return result

def get_topic_with_counts(db: Session, topic_id: UUID) -> Optional[Dict]:
    """
    Get a topic with question counts and subtopics
    """
    # Get the topic
    topic = db.query(Topic).filter(Topic.id == topic_id).first()
    
    if not topic:
        return None
    
    # Get subtopics for this topic
    subtopics = db.query(Topic).filter(Topic.parent_id == topic_id).all()
    
    # Count questions for this topic
    topic_count = db.query(func.count(QuestionTopic.question_id)).filter(
        QuestionTopic.topic_id == topic_id
    ).scalar() or 0
    
    # Process subtopics with counts
    subtopics_with_counts = []
    for subtopic in subtopics:
        subtopic_count = db.query(func.count(QuestionTopic.question_id)).filter(
            QuestionTopic.topic_id == subtopic.id
        ).scalar() or 0
        
        subtopics_with_counts.append({
            "id": subtopic.id,
            "name": subtopic.name,
            "slug": subtopic.slug,
            "description": subtopic.description,
            "questions_count": subtopic_count
        })
    
    # Create response dictionary
    result = {
        "id": topic.id,
        "name": topic.name,
        "slug": topic.slug,
        "description": topic.description,
        "parent_id": topic.parent_id,
        "questions_count": topic_count,
        "subtopics": subtopics_with_counts
    }
    
    return result


def create_topic(db: Session, topic_in: TopicCreate) -> Topic:
    """
    Create a new topic
    """
    db_topic = Topic(
        name=topic_in.name,
        slug=topic_in.slug,
        description=topic_in.description,
        parent_id=topic_in.parent_id
    )
    db.add(db_topic)
    db.commit()
    db.refresh(db_topic)
    return db_topic

def update_topic(db: Session, topic: Topic, topic_in: TopicUpdate) -> Topic:
    """
    Update a topic
    """
    update_data = topic_in.dict(exclude_unset=True)
    
    for key, value in update_data.items():
        setattr(topic, key, value)
        
    db.add(topic)
    db.commit()
    db.refresh(topic)
    return topic

def delete_topic(db: Session, topic_id: UUID) -> None:
    """
    Delete a topic
    """
    topic = db.query(Topic).filter(Topic.id == topic_id).first()
    if topic:
        db.delete(topic)
        db.commit()
    return None

