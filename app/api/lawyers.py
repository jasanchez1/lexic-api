from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status, UploadFile, File
from sqlalchemy.orm import Session
from uuid import UUID

from app.db.database import get_db
from app.db.repositories import lawyers as lawyers_repository
from app.db.repositories import areas as areas_repository
from app.schemas.lawyer import Lawyer, LawyerDetail, LawyerCreate, LawyerUpdate, LawyerList
from app.api.dependencies import get_optional_current_user
from app.models.user import User
from app.models.area import lawyer_area_association
from app.db.repositories.users import get_user_by_id

# Import routers for lawyer-related endpoints
from app.api.reviews import router as reviews_router
from app.api.experience import router as experience_router
from app.api.messages import router as messages_router

router = APIRouter()

@router.get("", response_model=LawyerList)
async def search_lawyers(
    db: Session = Depends(get_db),
    area: Optional[str] = None,
    city: Optional[str] = None,
    q: Optional[str] = None,
    sort: str = "best_match",
    page: int = Query(1, ge=1),
    size: int = Query(10, ge=1, le=100),
):
    """
    Search lawyers with various filters
    """
    skip = (page - 1) * size
    
    lawyers, total = lawyers_repository.search_lawyers(
        db, 
        area_slug=area, 
        city=city, 
        query=q, 
        sort=sort, 
        skip=skip, 
        limit=size
    )
    
    # Calculate total pages
    pages = (total + size - 1) // size  # Ceiling division
    
    return LawyerList(
        lawyers=lawyers,
        total=total, 
        page=page, 
        size=size, 
        pages=pages
    )


@router.get("/{lawyer_id}", response_model=LawyerDetail)
async def get_lawyer(
    lawyer_id: UUID, 
    db: Session = Depends(get_db),
):
    """
    Get a specific lawyer by ID
    """
    db_lawyer = lawyers_repository.get_lawyer_by_id(db, lawyer_id)
    if db_lawyer is None:
        raise HTTPException(status_code=404, detail="Lawyer not found")
    
    # Process the lawyer's areas to match LawyerPracticeArea format
    area_scores = db.query(
        lawyer_area_association.c.area_id, 
        lawyer_area_association.c.experience_score
    ).filter(
        lawyer_area_association.c.lawyer_id == db_lawyer.id
    ).all()
    
    score_map = {str(area_id): score for area_id, score in area_scores}
    
    # Create a dictionary for the lawyer
    lawyer_dict = db_lawyer.__dict__.copy()
    if "_sa_instance_state" in lawyer_dict:
        del lawyer_dict["_sa_instance_state"]
    
    # Process areas
    processed_areas = []
    for area in db_lawyer.areas:
        processed_areas.append({
            "id": str(area.id),
            "name": area.name,
            "slug": area.slug,
            "experience_score": score_map.get(str(area.id), 0)
        })
    
    lawyer_dict["areas"] = processed_areas
    lawyer_dict["review_score"] = 0.0  # Default value
    lawyer_dict["review_count"] = 0    # Default value
    
    return lawyer_dict


@router.post("", response_model=Lawyer, status_code=status.HTTP_201_CREATED)
async def create_lawyer(
    lawyer: LawyerCreate, 
    db: Session = Depends(get_db),
):
    """
    Create a new lawyer profile
    """
    # Check if lawyer with this email already exists
    db_lawyer = lawyers_repository.get_lawyer_by_email(db, lawyer.email)
    if db_lawyer:
        raise HTTPException(
            status_code=400,
            detail="Lawyer with this email already exists"
        )
    
    # Check if areas exist if provided
    if lawyer.areas:
        for area_assoc in lawyer.areas:
            db_area = areas_repository.get_area_by_id(db, area_assoc.area_id)
            if not db_area:
                raise HTTPException(
                    status_code=400,
                    detail=f"Practice area with ID {area_assoc.area_id} not found"
                )
    
    # Associate with current user if authenticated
    user = get_user_by_id(db, lawyer.user_id) if lawyer.user_id else None
    
    if lawyer.user_id and not user:
        raise HTTPException(
            status_code=400,
            detail="User with this ID not found"
        )
    
    # Check if current user already has a lawyer profile
    if lawyer.user_id and lawyers_repository.get_lawyer_by_user_id(db, lawyer.user_id):
        raise HTTPException(
            status_code=400,
            detail="User already has a lawyer profile"
        )
        
    db_lawyer = lawyers_repository.create_lawyer(db, lawyer)
    
    # Process the lawyer's areas to match LawyerPracticeArea format
    area_scores = db.query(
        lawyer_area_association.c.area_id, 
        lawyer_area_association.c.experience_score
    ).filter(
        lawyer_area_association.c.lawyer_id == db_lawyer.id
    ).all()
    
    score_map = {str(area_id): score for area_id, score in area_scores}
    
    # Create a dictionary for the lawyer
    lawyer_dict = db_lawyer.__dict__.copy()
    if "_sa_instance_state" in lawyer_dict:
        del lawyer_dict["_sa_instance_state"]
    
    # Process areas
    processed_areas = []
    for area in db_lawyer.areas:
        processed_areas.append({
            "id": str(area.id),
            "name": area.name,
            "slug": area.slug,
            "experience_score": score_map.get(str(area.id), 0)
        })
    
    lawyer_dict["areas"] = processed_areas
    lawyer_dict["review_score"] = 0.0  # Default value
    lawyer_dict["review_count"] = 0    # Default value
    
    return lawyer_dict

@router.patch("/{lawyer_id}", response_model=Lawyer)
async def update_lawyer(
    lawyer_id: UUID,
    lawyer: LawyerUpdate,
    db: Session = Depends(get_db),
):
    """
    Update a lawyer profile
    """
    db_lawyer = lawyers_repository.get_lawyer_by_id(db, lawyer_id)
    if db_lawyer is None:
        raise HTTPException(status_code=404, detail="Lawyer not found")
    
    # Check if areas exist if provided
    if lawyer.areas:
        for area_assoc in lawyer.areas:
            db_area = areas_repository.get_area_by_id(db, area_assoc.area_id)
            if not db_area:
                raise HTTPException(
                    status_code=400,
                    detail=f"Practice area with ID {area_assoc.area_id} not found"
                )
    
    # Check email uniqueness if being updated
    if lawyer.email and lawyer.email != db_lawyer.email:
        existing_lawyer = lawyers_repository.get_lawyer_by_email(db, lawyer.email)
        if existing_lawyer:
            raise HTTPException(
                status_code=400,
                detail="Lawyer with this email already exists"
            )
    
    updated_lawyer = lawyers_repository.update_lawyer(db, db_lawyer, lawyer)
    
    # Process the lawyer's areas to match LawyerPracticeArea format
    area_scores = db.query(
        lawyer_area_association.c.area_id, 
        lawyer_area_association.c.experience_score
    ).filter(
        lawyer_area_association.c.lawyer_id == updated_lawyer.id
    ).all()
    
    score_map = {str(area_id): score for area_id, score in area_scores}
    
    # Create a dictionary for the lawyer
    lawyer_dict = updated_lawyer.__dict__.copy()
    if "_sa_instance_state" in lawyer_dict:
        del lawyer_dict["_sa_instance_state"]
    
    # Process areas
    processed_areas = []
    for area in updated_lawyer.areas:
        processed_areas.append({
            "id": str(area.id),
            "name": area.name,
            "slug": area.slug,
            "experience_score": score_map.get(str(area.id), 0)
        })
    
    lawyer_dict["areas"] = processed_areas
    lawyer_dict["review_score"] = 0.0  # Default value
    lawyer_dict["review_count"] = 0    # Default value
    
    return lawyer_dict

@router.delete("/{lawyer_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_lawyer(
    lawyer_id: UUID, 
    db: Session = Depends(get_db),
):
    """
    Delete a lawyer profile
    """
    db_lawyer = lawyers_repository.get_lawyer_by_id(db, lawyer_id)
    if db_lawyer is None:
        raise HTTPException(status_code=404, detail="Lawyer not found")
    
    lawyers_repository.delete_lawyer(db, lawyer_id)
    return None

# Include subrouters for lawyer-related endpoints
router.include_router(reviews_router, prefix="")
router.include_router(experience_router, prefix="")
router.include_router(messages_router, prefix="")
