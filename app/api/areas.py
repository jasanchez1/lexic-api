from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from uuid import UUID

from app.db.database import get_db
from app.db.repositories import areas as areas_repository
from app.db.repositories import categories as categories_repository
from app.schemas.area import PracticeArea, PracticeAreaCreate, PracticeAreaUpdate, PracticeAreaWithCount
from app.schemas.category import PracticeAreaCategoryWithAreas

router = APIRouter()

@router.get("", response_model=List[PracticeArea])
async def get_practice_areas(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    category_id: Optional[UUID] = None,
    category_slug: Optional[str] = None
):
    """
    Retrieve all practice areas with optional filtering by category
    """
    return areas_repository.get_areas(db, skip, limit, category_id, category_slug)

@router.get("/with-counts", response_model=List[PracticeAreaWithCount])
async def get_practice_areas_with_counts(db: Session = Depends(get_db)):
    """
    Retrieve all practice areas with lawyer counts
    """
    return areas_repository.get_areas_with_counts(db)

@router.get("/by-category", response_model=List[PracticeAreaCategoryWithAreas])
async def get_practice_areas_by_category(db: Session = Depends(get_db)):
    """
    Retrieve practice areas grouped by category
    """
    # Get all categories
    categories = categories_repository.get_categories(db)
    result = []
    
    # For each category, get its areas
    for category in categories:
        areas = areas_repository.get_areas(db, category_id=category.id)
        
        category_with_areas = PracticeAreaCategoryWithAreas(
            id=category.id,
            name=category.name,
            slug=category.slug,
            areas=[
                PracticeArea(
                id=area.id,
                name=area.name,
                slug=area.slug,
                category_id=area.category_id,
                description=area.description
            ) for area in areas]
        )
        
        result.append(category_with_areas)
    return result

@router.get("/{area_id}", response_model=PracticeArea)
async def get_practice_area(area_id: UUID, db: Session = Depends(get_db)):
    """
    Retrieve a specific practice area by ID
    """
    db_area = areas_repository.get_area_by_id(db, area_id)
    if db_area is None:
        raise HTTPException(status_code=404, detail="Practice area not found")
    return db_area

@router.get("/slug/{slug}", response_model=PracticeArea)
async def get_practice_area_by_slug(slug: str, db: Session = Depends(get_db)):
    """
    Retrieve a specific practice area by slug
    """
    db_area = areas_repository.get_area_by_slug(db, slug)
    if db_area is None:
        raise HTTPException(status_code=404, detail="Practice area not found")
    return db_area

@router.post("", response_model=PracticeArea, status_code=status.HTTP_201_CREATED)
async def create_practice_area(
    area: PracticeAreaCreate, 
    db: Session = Depends(get_db)
):
    """
    Create a new practice area
    """
    # Check if an area with the same slug already exists
    db_area = areas_repository.get_area_by_slug(db, area.slug)
    if db_area:
        raise HTTPException(
            status_code=400,
            detail="Practice area with this slug already exists"
        )
    
    # Check if the category exists
    db_category = categories_repository.get_category_by_id(db, area.category_id)
    if not db_category:
        raise HTTPException(
            status_code=404,
            detail="Category not found"
        )
        
    return areas_repository.create_area(db, area)

@router.patch("/{area_id}", response_model=PracticeArea)
async def update_practice_area(
    area_id: UUID,
    area: PracticeAreaUpdate,
    db: Session = Depends(get_db)
):
    """
    Update a practice area
    """
    db_area = areas_repository.get_area_by_id(db, area_id)
    if db_area is None:
        raise HTTPException(status_code=404, detail="Practice area not found")
        
    # Check if slug is being updated and is unique
    if area.slug is not None and area.slug != db_area.slug:
        existing_area = areas_repository.get_area_by_slug(db, area.slug)
        if existing_area and existing_area.id != area_id:
            raise HTTPException(
                status_code=400,
                detail="Practice area with this slug already exists"
            )
    
    # Check if category exists if it's being updated
    if area.category_id is not None and area.category_id != db_area.category_id:
        db_category = categories_repository.get_category_by_id(db, area.category_id)
        if not db_category:
            raise HTTPException(
                status_code=404,
                detail="Category not found"
            )
            
    return areas_repository.update_area(db, db_area, area)

@router.delete("/{area_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_practice_area(area_id: UUID, db: Session = Depends(get_db)):
    """
    Delete a practice area
    """
    db_area = areas_repository.get_area_by_id(db, area_id)
    if db_area is None:
        raise HTTPException(status_code=404, detail="Practice area not found")
        
    areas_repository.delete_area(db, area_id)
    return None