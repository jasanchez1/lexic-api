from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status, File, UploadFile, BackgroundTasks
from sqlalchemy import func
from sqlalchemy.orm import Session
from uuid import UUID
import os
import uuid
from datetime import datetime

from app.db.database import get_db
from app.db.repositories import guides as guides_repository
from app.schemas.guide import (
    GuideCategory, GuideCategoryCreate, GuideCategoryList, GuideCategoryUpdate, GuideCategoryWithGuides, GuideCreate, GuideUpdate, GuidesList, GuideDetail, 
    GuideSectionUpdate, SectionsReorder, SlugCheckResponse,
    ImageUploadResponse, SuccessResponse, ErrorResponse
)
from app.api.dependencies import get_current_active_verified_user, get_optional_current_user
from app.models.user import User
from app.utils.analytics import track_guide_view_async

router = APIRouter()

@router.get("", response_model=GuidesList)
async def get_guides(
    db: Session = Depends(get_db),
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    published_only: bool = True,
    category_slug: Optional[str] = None
):
    """
    List all guides with basic information and pagination
    """
    skip = (page - 1) * limit
    
    # Get guides with optional category filter
    guides, total = guides_repository.get_guides(
        db, 
        skip=skip, 
        limit=limit, 
        published_only=published_only,
        category_slug=category_slug
    )
    
    # Calculate total pages
    pages = (total + limit - 1) // limit
    
    return {
        "guides": guides,
        "total": total,
        "page": page,
        "pages": pages
    }

@router.get("/slug/{slug}", response_model=GuideDetail)
async def get_guide_by_slug(
    slug: str,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_optional_current_user),
    background_tasks: BackgroundTasks = BackgroundTasks()
):
    """
    Get a guide by slug with complete information including all sections
    """
    guide = guides_repository.get_guide_by_slug(db, slug)
    if not guide:
        raise HTTPException(status_code=404, detail="Guide not found")
    
    # Only return published guides unless explicitly requested
    if not guide.published:
        raise HTTPException(status_code=404, detail="Guide not found or not published")
    
    # Track guide view asynchronously
    track_guide_view_async(
        background_tasks=background_tasks,
        guide_id=guide.id,
        user_id=current_user.id if current_user else None,
        db=db
    )
    
    return guide

@router.get("/slug-check/{slug}", response_model=SlugCheckResponse)
async def check_slug_availability(
    slug: str,
    db: Session = Depends(get_db),
    exclude_id: Optional[UUID] = None
):
    """
    Check if a slug is available for use
    """
    is_available = guides_repository.check_slug_availability(db, slug, exclude_id)
    
    if is_available:
        return {"available": True}
    else:
        # Generate a suggestion
        suggestion = guides_repository.get_slug_suggestion(db, slug)
        return {"available": False, "suggestion": suggestion}

@router.post("", response_model=GuideDetail, status_code=status.HTTP_201_CREATED)
async def create_guide(
    guide: GuideCreate,
    db: Session = Depends(get_db),
):
    """
    Create a new guide
    """
    # Check if slug is provided and if it's available
    if guide.slug:
        is_available = guides_repository.check_slug_availability(db, guide.slug)
        if not is_available:
            raise HTTPException(
                status_code=400,
                detail="Slug is already in use. Please use a different slug."
            )
    
    # Create the guide
    db_guide = guides_repository.create_guide(db, guide)
    
    return db_guide

@router.put("/{guide_id}", response_model=GuideDetail)
async def update_guide(
    guide_id: UUID,
    guide: GuideUpdate,
    db: Session = Depends(get_db),
):
    """
    Update an existing guide
    """
    # Check if guide exists
    db_guide = guides_repository.get_guide_by_id(db, guide_id)
    if not db_guide:
        raise HTTPException(status_code=404, detail="Guide not found")
    
    # Check if slug is being updated and if it's available
    if guide.slug is not None and guide.slug != db_guide.slug:
        is_available = guides_repository.check_slug_availability(db, guide.slug, exclude_id=guide_id)
        if not is_available:
            raise HTTPException(
                status_code=400,
                detail="Slug is already in use. Please use a different slug."
            )
    
    # Update the guide
    updated_guide = guides_repository.update_guide(db, db_guide, guide)
    
    return updated_guide

@router.delete("/{guide_id}", response_model=SuccessResponse, status_code=status.HTTP_200_OK)
async def delete_guide(
    guide_id: UUID,
    db: Session = Depends(get_db),
):
    """
    Delete a guide
    """
    # Check if guide exists
    db_guide = guides_repository.get_guide_by_id(db, guide_id)
    if not db_guide:
        raise HTTPException(status_code=404, detail="Guide not found")
    
    # Delete the guide
    guides_repository.delete_guide(db, guide_id)
    
    return {"success": True}

@router.patch("/{guide_id}/sections/{section_id}", response_model=GuideDetail)
async def update_section(
    guide_id: UUID,
    section_id: UUID,
    section: GuideSectionUpdate,
    db: Session = Depends(get_db),
):
    """
    Update a specific section of a guide
    """
    # Check if guide exists
    db_guide = guides_repository.get_guide_by_id(db, guide_id)
    if not db_guide:
        raise HTTPException(status_code=404, detail="Guide not found")
    
    # Check if section exists and belongs to the guide
    db_section = guides_repository.get_section_by_id(db, section_id)
    if not db_section or db_section.guide_id != guide_id:
        raise HTTPException(status_code=404, detail="Section not found")
    
    # Update the section
    guides_repository.update_section(db, db_section, section)
    
    # Return the updated guide
    updated_guide = guides_repository.get_guide_by_id(db, guide_id)
    return updated_guide

@router.post("/{guide_id}/sections/reorder", response_model=GuideDetail)
async def reorder_sections(
    guide_id: UUID,
    order_data: SectionsReorder,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_verified_user)
):
    """
    Reorder the sections of a guide
    """
    # Check if guide exists
    db_guide = guides_repository.get_guide_by_id(db, guide_id)
    if not db_guide:
        raise HTTPException(status_code=404, detail="Guide not found")
    
    # Reorder the sections
    guides_repository.reorder_sections(db, guide_id, order_data)
    
    # Return the updated guide
    updated_guide = guides_repository.get_guide_by_id(db, guide_id)
    return updated_guide

@router.post("/images", response_model=ImageUploadResponse)
async def upload_image(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_verified_user)
):
    """
    Upload an image for use in guide content
    """
    # Create the uploads directory if it doesn't exist
    upload_dir = "uploads/guide_images"
    os.makedirs(upload_dir, exist_ok=True)
    
    # Generate a unique filename
    file_extension = os.path.splitext(file.filename)[1]
    unique_filename = f"{uuid.uuid4()}{file_extension}"
    file_path = os.path.join(upload_dir, unique_filename)
    
    # Write the file
    contents = await file.read()
    with open(file_path, "wb") as f:
        f.write(contents)
    
    # Get the file size
    file_size = os.path.getsize(file_path)
    
    # Generate URL for the uploaded file
    file_url = f"/api/uploads/guide_images/{unique_filename}"
    
    return {
        "url": file_url,
        "name": unique_filename,
        "size": file_size
    }



@router.get("/categories", response_model=GuideCategoryList)
async def get_guide_categories(
    db: Session = Depends(get_db),
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
):
    """
    List all guide categories with pagination
    """
    skip = (page - 1) * limit
    
    # Get categories with guide counts
    categories, total = guides_repository.get_categories(
        db, 
        skip=skip, 
        limit=limit, 
        with_counts=True
    )
    
    # Calculate total pages
    pages = (total + limit - 1) // limit
    
    return {
        "categories": categories,
        "total": total,
        "page": page,
        "pages": pages
    }


@router.get("/categories/{category_id}", response_model=GuideCategoryWithGuides)
async def get_guide_category(
    category_id: UUID,
    db: Session = Depends(get_db),
):
    """
    Get a specific guide category by ID
    """
    category = guides_repository.get_category_by_id(db, category_id)
    if not category:
        raise HTTPException(status_code=404, detail="Guide category not found")
    
    # Count guides in this category
    guide_count = db.query(func.count("*")).filter_by(category_id=category_id).scalar() or 0
    
    return {
        "id": category.id,
        "name": category.name,
        "slug": category.slug,
        "description": category.description,
        "created_at": category.created_at,
        "updated_at": category.updated_at,
        "guide_count": guide_count
    }


@router.get("/categories/slug/{slug}", response_model=GuideCategoryWithGuides)
async def get_guide_category_by_slug(
    slug: str,
    db: Session = Depends(get_db),
):
    """
    Get a specific guide category by slug
    """
    category = guides_repository.get_category_by_slug(db, slug)
    if not category:
        raise HTTPException(status_code=404, detail="Guide category not found")
    
    # Count guides in this category
    guide_count = db.query(func.count("*")).filter_by(category_id=category.id).scalar() or 0
    
    return {
        "id": category.id,
        "name": category.name,
        "slug": category.slug,
        "description": category.description,
        "created_at": category.created_at,
        "updated_at": category.updated_at,
        "guide_count": guide_count
    }


@router.get("/categories/slug-check/{slug}", response_model=SlugCheckResponse)
async def check_category_slug_availability(
    slug: str,
    db: Session = Depends(get_db),
    exclude_id: Optional[UUID] = None
):
    """
    Check if a category slug is available for use
    """
    is_available = guides_repository.check_slug_availability(db, slug, exclude_id)
    
    if is_available:
        return {"available": True}
    else:
        # Generate a suggestion
        suggestion = guides_repository.get_slug_suggestion(db, slug)
        return {"available": False, "suggestion": suggestion}


@router.post("/categories", response_model=GuideCategory, status_code=status.HTTP_201_CREATED)
async def create_guide_category(
    category: GuideCategoryCreate,
    db: Session = Depends(get_db),
):
    """
    Create a new guide category
    """
    # Check if slug is available
    if not guides_repository.check_slug_availability(db, category.slug):
        raise HTTPException(
            status_code=400,
            detail="Slug is already in use. Please use a different slug."
        )
    
    # Create the category
    db_category = guides_repository.create_category(db, category)
    
    return db_category


@router.patch("/categories/{category_id}", response_model=GuideCategory)
async def update_guide_category(
    category_id: UUID,
    category: GuideCategoryUpdate,
    db: Session = Depends(get_db),
):
    """
    Update an existing guide category
    """
    # Check if category exists
    db_category = guides_repository.get_category_by_id(db, category_id)
    if not db_category:
        raise HTTPException(status_code=404, detail="Guide category not found")
    
    # Check if slug is being updated and if it's available
    if category.slug is not None and category.slug != db_category.slug:
        is_available = guides_repository.check_slug_availability(db, category.slug, exclude_id=category_id)
        if not is_available:
            raise HTTPException(
                status_code=400,
                detail="Slug is already in use. Please use a different slug."
            )
    
    # Update the category
    updated_category = guides_repository.update_category(db, db_category, category)
    
    return updated_category


@router.delete("/categories/{category_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_guide_category(
    category_id: UUID,
    db: Session = Depends(get_db),
):
    """
    Delete a guide category
    """
    # Check if category exists
    db_category = guides_repository.get_category_by_id(db, category_id)
    if not db_category:
        raise HTTPException(status_code=404, detail="Guide category not found")
    
    # Check if any guides are using this category
    from app.models.guide import Guide
    guide_count = db.query(func.count(Guide.id)).filter(Guide.category_id == category_id).scalar()
    if guide_count > 0:
        raise HTTPException(
            status_code=400,
            detail=f"Cannot delete this category as it is being used by {guide_count} guides. Update or delete those guides first."
        )
    
    # Delete the category
    guides_repository.delete_category(db, category_id)
    
    return None