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

router = APIRouter()

@router.get("/", response_model=LawyerList)
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
    
    return LawyerList(lawyers=[lawyer for lawyer in lawyers],
         total=total, 
         page=page, 
         size=size, 
         pages=pages)


@router.get("/{lawyer_id}", response_model=LawyerDetail)
async def get_lawyer(
    lawyer_id: UUID, 
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_optional_current_user)
):
    """
    Get a specific lawyer by ID
    """
    db_lawyer = lawyers_repository.get_lawyer_by_id(db, lawyer_id)
    if db_lawyer is None:
        raise HTTPException(status_code=404, detail="Lawyer not found")
    return db_lawyer

@router.post("/", response_model=Lawyer, status_code=status.HTTP_201_CREATED)
async def create_lawyer(
    lawyer: LawyerCreate, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_optional_current_user)
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
    if current_user:
        lawyer.user_id = current_user.id
        
        # Check if current user already has a lawyer profile
        existing_profile = lawyers_repository.get_lawyer_by_user_id(db, current_user.id)
        if existing_profile:
            raise HTTPException(
                status_code=400,
                detail="Current user already has a lawyer profile"
            )
    
    return lawyers_repository.create_lawyer(db, lawyer)

@router.patch("/{lawyer_id}", response_model=Lawyer)
async def update_lawyer(
    lawyer_id: UUID,
    lawyer: LawyerUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_optional_current_user)
):
    """
    Update a lawyer profile
    """
    db_lawyer = lawyers_repository.get_lawyer_by_id(db, lawyer_id)
    if db_lawyer is None:
        raise HTTPException(status_code=404, detail="Lawyer not found")
    
    # Check if user is authorized to update this lawyer
    # Only the linked user or an admin can update a lawyer profile
    if current_user and (current_user.id == db_lawyer.user_id):
        # Authorized
        pass
    else:
        raise HTTPException(
            status_code=403,
            detail="Not authorized to update this lawyer profile"
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
    
    # Check email uniqueness if being updated
    if lawyer.email and lawyer.email != db_lawyer.email:
        existing_lawyer = lawyers_repository.get_lawyer_by_email(db, lawyer.email)
        if existing_lawyer:
            raise HTTPException(
                status_code=400,
                detail="Lawyer with this email already exists"
            )
    
    return lawyers_repository.update_lawyer(db, db_lawyer, lawyer)

@router.delete("/{lawyer_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_lawyer(
    lawyer_id: UUID, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_optional_current_user)
):
    """
    Delete a lawyer profile
    """
    db_lawyer = lawyers_repository.get_lawyer_by_id(db, lawyer_id)
    if db_lawyer is None:
        raise HTTPException(status_code=404, detail="Lawyer not found")
    
    # Check if user is authorized to delete this lawyer
    # Only the linked user or an admin can delete a lawyer profile
    if current_user and (current_user.id == db_lawyer.user_id):
        # Authorized
        pass
    else:
        raise HTTPException(
            status_code=403,
            detail="Not authorized to delete this lawyer profile"
        )
    
    lawyers_repository.delete_lawyer(db, lawyer_id)
    return None