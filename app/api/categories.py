from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from uuid import UUID

from app.db.database import get_db
from app.db.repositories import categories as categories_repository
from app.db.repositories import areas as areas_repository
from app.schemas.category import PracticeAreaCategory, PracticeAreaCategoryCreate, PracticeAreaCategoryUpdate, PracticeAreaCategoryWithAreas
from app.schemas.area import PracticeArea

router = APIRouter()

@router.get("/{category_id}", response_model=PracticeAreaCategory)
async def get_practice_area_category(category_id: UUID, db: Session = Depends(get_db)):
    """
    Retrieve a specific practice area category by ID
    """
    db_category = categories_repository.get_category_by_id(db, category_id)
    if db_category is None:
        raise HTTPException(status_code=404, detail="Practice area category not found")
    return db_category

@router.get("/{category_id}/areas", response_model=List[PracticeArea])
async def get_areas_by_category(category_id: UUID, db: Session = Depends(get_db)):
    """
    Retrieve all practice areas in a specific category
    """
    db_category = categories_repository.get_category_by_id(db, category_id)
    if db_category is None:
        raise HTTPException(status_code=404, detail="Practice area category not found")
        
    return areas_repository.get_areas(db, category_id=category_id, limit=1000)

@router.get("/slug/{slug}", response_model=PracticeAreaCategory)
async def get_practice_area_category_by_slug(slug: str, db: Session = Depends(get_db)):
    """
    Retrieve a specific practice area category by slug
    """
    db_category = categories_repository.get_category_by_slug(db, slug)
    if db_category is None:
        raise HTTPException(status_code=404, detail="Practice area category not found")
    return db_category

@router.get("/slug/{slug}/areas", response_model=List[PracticeArea])
async def get_areas_by_category_slug(slug: str, db: Session = Depends(get_db)):
    """
    Retrieve all practice areas in a specific category by slug
    """
    db_category = categories_repository.get_category_by_slug(db, slug)
    if db_category is None:
        raise HTTPException(status_code=404, detail="Practice area category not found")
        
    return areas_repository.get_areas(db, category_id=db_category.id, limit=1000)

@router.post("/", response_model=PracticeAreaCategory, status_code=status.HTTP_201_CREATED)
async def create_practice_area_category(
    category: PracticeAreaCategoryCreate, 
    db: Session = Depends(get_db)
):
    """
    Create a new practice area category
    """
    # Check if a category with the same slug already exists
    db_category = categories_repository.get_category_by_slug(db, category.slug)
    if db_category:
        raise HTTPException(
            status_code=400,
            detail="Practice area category with this slug already exists"
        )
        
    return categories_repository.create_category(db, category)

@router.patch("/{category_id}", response_model=PracticeAreaCategory)
async def update_practice_area_category(
    category_id: UUID,
    category: PracticeAreaCategoryUpdate,
    db: Session = Depends(get_db)
):
    """
    Update a practice area category
    """
    db_category = categories_repository.get_category_by_id(db, category_id)
    if db_category is None:
        raise HTTPException(status_code=404, detail="Practice area category not found")
        
    # Check if slug is being updated and is unique
    if category.slug is not None and category.slug != db_category.slug:
        existing_category = categories_repository.get_category_by_slug(db, category.slug)
        if existing_category:
            raise HTTPException(
                status_code=400,
                detail="Practice area category with this slug already exists"
            )
            
    return categories_repository.update_category(db, db_category, category)

@router.delete("/{category_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_practice_area_category(category_id: UUID, db: Session = Depends(get_db)):
    """
    Delete a practice area category
    """
    db_category = categories_repository.get_category_by_id(db, category_id)
    if db_category is None:
        raise HTTPException(status_code=404, detail="Practice area category not found")
        
    categories_repository.delete_category(db, category_id)
    return None