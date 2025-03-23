from typing import List, Optional
from uuid import UUID
from sqlalchemy.orm import Session

from app.models.featured_item import FeaturedItem
from app.schemas.featured_item import FeaturedItemCreate, FeaturedItemUpdate

def get_featured_item_by_id(db: Session, item_id: UUID) -> Optional[FeaturedItem]:
    """
    Get a featured item by ID
    """
    return db.query(FeaturedItem).filter(FeaturedItem.id == item_id).first()

def get_featured_items_by_type(
    db: Session, 
    item_type: str,
    parent_id: Optional[UUID] = None
) -> List[FeaturedItem]:
    """
    Get featured items by type and optional parent ID
    """
    query = db.query(FeaturedItem).filter(FeaturedItem.item_type == item_type)
    
    if parent_id is not None:
        query = query.filter(FeaturedItem.parent_id == parent_id)
    
    return query.order_by(FeaturedItem.display_order).all()

def get_all_featured_items(db: Session) -> List[FeaturedItem]:
    """
    Get all featured items
    """
    return db.query(FeaturedItem).order_by(
        FeaturedItem.item_type,
        FeaturedItem.display_order
    ).all()

def create_featured_item(db: Session, item: FeaturedItemCreate) -> FeaturedItem:
    """
    Create a new featured item
    """
    db_item = FeaturedItem(
        item_id=item.item_id,
        item_type=item.item_type,
        parent_id=item.parent_id,
        display_order=item.display_order
    )
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item

def update_featured_item(db: Session, item: FeaturedItem, item_in: FeaturedItemUpdate) -> FeaturedItem:
    """
    Update a featured item
    """
    update_data = item_in.dict(exclude_unset=True)
    
    for key, value in update_data.items():
        setattr(item, key, value)
        
    db.add(item)
    db.commit()
    db.refresh(item)
    return item

def delete_featured_item(db: Session, item_id: UUID) -> None:
    """
    Delete a featured item
    """
    item = db.query(FeaturedItem).filter(FeaturedItem.id == item_id).first()
    if item:
        db.delete(item)
        db.commit()
    return None

def reorder_featured_items(db: Session, item_ids: List[UUID]) -> List[FeaturedItem]:
    """
    Reorder featured items
    """
    for i, item_id in enumerate(item_ids):
        db.query(FeaturedItem).filter(FeaturedItem.id == item_id).update(
            {"display_order": i}
        )
    
    db.commit()
    return db.query(FeaturedItem).filter(FeaturedItem.id.in_(item_ids)).order_by(FeaturedItem.display_order).all()

def check_guide_category_exists(db: Session, category_slug: str) -> bool:
    """
    Check if a guide category exists by checking if any guides have this category
    """
    from app.models.guide import Guide
    return db.query(Guide).filter(
        Guide.category_slug == category_slug
    ).first() is not None