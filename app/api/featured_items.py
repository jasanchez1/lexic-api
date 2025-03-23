from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from uuid import UUID

from app.db.database import get_db
from app.db.repositories import featured_items as featured_repository
from app.db.repositories import areas as areas_repository
from app.db.repositories import categories as categories_repository
from app.db.repositories import topics as topics_repository
from app.db.repositories import guides as guides_repository
from app.schemas.featured_item import FeaturedItem, FeaturedItemCreate, FeaturedItemUpdate

router = APIRouter()

@router.get("", response_model=List[FeaturedItem])
async def get_featured_items(
    db: Session = Depends(get_db),
    item_type: Optional[str] = None,
    parent_id: Optional[UUID] = None
):
    """
    Get all featured items, optionally filtered by type and parent ID
    """
    if item_type:
        return featured_repository.get_featured_items_by_type(db, item_type, parent_id)
    
    return featured_repository.get_all_featured_items(db)

@router.post("", response_model=FeaturedItem, status_code=status.HTTP_201_CREATED)
async def create_featured_item(
    item: FeaturedItemCreate,
    db: Session = Depends(get_db)
):
    """
    Create a new featured item
    """
    # Verify the item exists based on its type
    if item.item_type == "area":
        existing_item = areas_repository.get_area_by_id(db, item.item_id)
        if not existing_item:
            raise HTTPException(status_code=404, detail="Area not found")
    elif item.item_type == "category":
        existing_item = categories_repository.get_category_by_id(db, item.item_id)
        if not existing_item:
            raise HTTPException(status_code=404, detail="Category not found")
    elif item.item_type == "topic" or item.item_type == "subtopic":
        existing_item = topics_repository.get_topic_by_id(db, item.item_id)
        if not existing_item:
            raise HTTPException(status_code=404, detail="Topic not found")
    elif item.item_type == "guide":
        existing_item = guides_repository.get_guide_by_id(db, item.item_id)
        if not existing_item:
            raise HTTPException(status_code=404, detail="Guide not found")
    elif item.item_type == "guide_category":
        # For guide_category, we check if any guides exist with this category slug
        exists = featured_repository.check_guide_category_exists(db, item.item_id)
        if not exists:
            raise HTTPException(status_code=404, detail="Guide category not found")
    else:
        raise HTTPException(status_code=400, detail="Invalid item type")
    
    return featured_repository.create_featured_item(db, item)

@router.patch("/{item_id}", response_model=FeaturedItem)
async def update_featured_item(
    item_id: UUID,
    item: FeaturedItemUpdate,
    db: Session = Depends(get_db)
):
    """
    Update a featured item
    """
    db_item = featured_repository.get_featured_item_by_id(db, item_id)
    if not db_item:
        raise HTTPException(status_code=404, detail="Featured item not found")
    
    return featured_repository.update_featured_item(db, db_item, item)

@router.delete("/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_featured_item(
    item_id: UUID,
    db: Session = Depends(get_db)
):
    """
    Delete a featured item
    """
    db_item = featured_repository.get_featured_item_by_id(db, item_id)
    if not db_item:
        raise HTTPException(status_code=404, detail="Featured item not found")
    
    featured_repository.delete_featured_item(db, item_id)
    return None

@router.post("/reorder", response_model=List[FeaturedItem])
async def reorder_featured_items(
    item_ids: List[UUID],
    db: Session = Depends(get_db)
):
    """
    Reorder featured items
    """
    return featured_repository.reorder_featured_items(db, item_ids)