from typing import List, Optional
from uuid import UUID
from sqlalchemy.orm import Session

from app.models.category import PracticeAreaCategory as CategoryModel
from app.schemas.category import PracticeAreaCategoryCreate, PracticeAreaCategoryUpdate

def get_category_by_id(db: Session, category_id: UUID) -> Optional[CategoryModel]:
    """
    Get a practice area category by ID
    """
    return db.query(CategoryModel).filter(CategoryModel.id == category_id).first()

def get_category_by_slug(db: Session, slug: str) -> Optional[CategoryModel]:
    """
    Get a practice area category by slug
    """
    return db.query(CategoryModel).filter(CategoryModel.slug == slug).first()

def get_categories(
    db: Session, 
    skip: int = 0, 
    limit: int = 100
) -> List[CategoryModel]:
    """
    Get a list of practice area categories
    """
    return db.query(CategoryModel).offset(skip).limit(limit).all()

def create_category(db: Session, category_in: PracticeAreaCategoryCreate) -> CategoryModel:
    """
    Create a new practice area category
    """
    db_category = CategoryModel(
        name=category_in.name,
        slug=category_in.slug,
    )
    db.add(db_category)
    db.commit()
    db.refresh(db_category)
    return db_category

def update_category(db: Session, category: CategoryModel, category_in: PracticeAreaCategoryUpdate) -> CategoryModel:
    """
    Update a practice area category
    """
    update_data = category_in.dict(exclude_unset=True)
    
    for key, value in update_data.items():
        setattr(category, key, value)
        
    db.add(category)
    db.commit()
    db.refresh(category)
    return category

def delete_category(db: Session, category_id: UUID) -> None:
    """
    Delete a practice area category
    """
    category = db.query(CategoryModel).filter(CategoryModel.id == category_id).first()
    if category:
        db.delete(category)
        db.commit()
    return None