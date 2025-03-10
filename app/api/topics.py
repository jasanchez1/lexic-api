from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from uuid import UUID

from app.db.database import get_db
from app.db.repositories import topics as topics_repository
from app.schemas.topic import TopicResponse, TopicCreate, TopicUpdate, TopicsList

router = APIRouter()

@router.get("", response_model=List[TopicResponse])
async def get_topics(
    db: Session = Depends(get_db),
):
    """
    Retrieve all topics with their subtopics
    """
    topics_with_counts = topics_repository.get_topics_with_counts(db)
    return topics_with_counts

@router.get("/{topic_id}", response_model=TopicResponse)
async def get_topic(
    topic_id: UUID,
    db: Session = Depends(get_db)
):
    """
    Retrieve a specific topic by ID
    """
    topic_with_counts = topics_repository.get_topic_with_counts(db, topic_id)
    if topic_with_counts is None:
        raise HTTPException(status_code=404, detail="Topic not found")
    
    return topic_with_counts

@router.get("/slug/{slug}", response_model=TopicResponse)
async def get_topic_by_slug(
    slug: str,
    db: Session = Depends(get_db)
):
    """
    Retrieve a specific topic by slug
    """
    db_topic = topics_repository.get_topic_by_slug(db, slug)
    if db_topic is None:
        raise HTTPException(status_code=404, detail="Topic not found")
    
    topic_with_counts = topics_repository.get_topic_with_counts(db, db_topic.id)
    if topic_with_counts is None:
        raise HTTPException(status_code=404, detail="Topic not found")
    
    return topic_with_counts

@router.post("", response_model=TopicResponse, status_code=status.HTTP_201_CREATED)
async def create_topic(
    topic: TopicCreate,
    db: Session = Depends(get_db)
):
    """
    Create a new topic
    """
    # Check if a topic with the same slug already exists
    db_topic = topics_repository.get_topic_by_slug(db, topic.slug)
    if db_topic:
        raise HTTPException(
            status_code=400,
            detail="Topic with this slug already exists"
        )
    
    # Check if parent exists if specified
    if topic.parent_id:
        parent_topic = topics_repository.get_topic_by_id(db, topic.parent_id)
        if not parent_topic:
            raise HTTPException(
                status_code=404,
                detail="Parent topic not found"
            )
    
    created_topic = topics_repository.create_topic(db, topic)
    return {
        "id": created_topic.id,
        "name": created_topic.name,
        "slug": created_topic.slug,
        "description": created_topic.description,
        "parent_id": created_topic.parent_id,
        "questions_count": 0,
        "subtopics": []
    }

@router.patch("/{topic_id}", response_model=TopicResponse)
async def update_topic(
    topic_id: UUID,
    topic: TopicUpdate,
    db: Session = Depends(get_db)
):
    """
    Update a topic
    """
    db_topic = topics_repository.get_topic_by_id(db, topic_id)
    if db_topic is None:
        raise HTTPException(status_code=404, detail="Topic not found")
    
    # Check if slug is being updated and is unique
    if topic.slug is not None and topic.slug != db_topic.slug:
        existing_topic = topics_repository.get_topic_by_slug(db, topic.slug)
        if existing_topic and existing_topic.id != topic_id:
            raise HTTPException(
                status_code=400,
                detail="Topic with this slug already exists"
            )
    
    # Check if parent exists if being updated
    if topic.parent_id is not None and topic.parent_id != db_topic.parent_id:
        # Can't make a topic its own parent
        if topic.parent_id == topic_id:
            raise HTTPException(
                status_code=400,
                detail="A topic cannot be its own parent"
            )
        
        # Check if parent exists
        parent_topic = topics_repository.get_topic_by_id(db, topic.parent_id)
        if not parent_topic:
            raise HTTPException(
                status_code=404,
                detail="Parent topic not found"
            )
    
    updated_topic = topics_repository.update_topic(db, db_topic, topic)
    
    # Get the updated topic with counts
    return topics_repository.get_topic_with_counts(db, db_topic.id)

@router.delete("/{topic_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_topic(
    topic_id: UUID,
    db: Session = Depends(get_db)
):
    """
    Delete a topic
    """
    db_topic = topics_repository.get_topic_by_id(db, topic_id)
    if db_topic is None:
        raise HTTPException(status_code=404, detail="Topic not found")
    
    topics_repository.delete_topic(db, topic_id)
    return None

