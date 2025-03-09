from typing import List, Optional, Dict, Any, Tuple
from uuid import UUID
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func, or_, and_, desc, asc

from app.models.lawyer import Lawyer as LawyerModel
from app.models.area import PracticeArea, lawyer_area_association
from app.schemas.lawyer import LawyerCreate, LawyerUpdate, LawyerAreaAssociation

def get_lawyer_by_id(db: Session, lawyer_id: UUID) -> Optional[LawyerModel]:
    """
    Get a lawyer by ID with eager-loaded relationships
    """
    return db.query(LawyerModel).options(
        joinedload(LawyerModel.areas)
    ).filter(LawyerModel.id == lawyer_id).first()

def get_lawyer_by_email(db: Session, email: str) -> Optional[LawyerModel]:
    """
    Get a lawyer by email
    """
    return db.query(LawyerModel).filter(LawyerModel.email == email).first()

def get_lawyer_by_user_id(db: Session, user_id: UUID) -> Optional[LawyerModel]:
    """
    Get a lawyer by user_id
    """
    return db.query(LawyerModel).filter(LawyerModel.user_id == user_id).first()

def search_lawyers(
    db: Session,
    area_slug: Optional[str] = None,
    city: Optional[str] = None,
    query: Optional[str] = None,
    sort: str = "best_match",
    skip: int = 0,
    limit: int = 100
) -> Tuple[List[Dict], int]:
    """
    Search lawyers with various filters
    Returns lawyers and total count
    """
    base_query = db.query(LawyerModel).options(
        joinedload(LawyerModel.areas)
    )
    
    # Base filters
    filters = []
    
    # Filter by area
    if area_slug:
        area = db.query(PracticeArea).filter(PracticeArea.slug == area_slug).first()
        if area:
            base_query = base_query.join(
                lawyer_area_association,
                LawyerModel.id == lawyer_area_association.c.lawyer_id
            ).filter(
                lawyer_area_association.c.area_id == area.id
            )
    
    # Filter by city
    if city:
        filters.append(LawyerModel.city.ilike(f"%{city}%"))
    
    # Text search
    if query:
        text_filters = [
            LawyerModel.name.ilike(f"%{query}%"),
            LawyerModel.bio.ilike(f"%{query}%"),
            LawyerModel.title.ilike(f"%{query}%")
        ]
        filters.append(or_(*text_filters))
    
    # Apply all filters
    if filters:
        base_query = base_query.filter(and_(*filters))
    
    # Get total count
    total = base_query.count()
    
    # Apply sorting
    if sort == "highest_rating":
        # Assuming a review_score field or relationship
        # For now, just sort by name as a placeholder
        base_query = base_query.order_by(asc(LawyerModel.name))
    elif sort == "most_experience":
        # Sort by experience (professional_start_date)
        base_query = base_query.order_by(asc(LawyerModel.professional_start_date))
    else:
        # Default sorting (best_match)
        # Here you might implement a more complex sort logic
        base_query = base_query.order_by(asc(LawyerModel.name))
    
    # Apply pagination
    lawyers_db = base_query.offset(skip).limit(limit).all()
    
    # Process lawyers to create dictionaries that match the expected format
    result_lawyers = []
    
    for lawyer in lawyers_db:
        # Get experience scores for each area
        area_scores = db.query(
            lawyer_area_association.c.area_id, 
            lawyer_area_association.c.experience_score
        ).filter(
            lawyer_area_association.c.lawyer_id == lawyer.id
        ).all()
        
        # Convert to dict for easy lookup
        score_map = {str(area_id): score for area_id, score in area_scores}
        
        # Transform areas to match LawyerPracticeArea format
        processed_areas = []
        for area in lawyer.areas:
            processed_areas.append({
                "id": str(area.id),
                "name": area.name,
                "slug": area.slug,
                "experience_score": score_map.get(str(area.id), 0)
            })
        
        # Create a dictionary representation of the lawyer
        lawyer_dict = {
            "id": lawyer.id,
            "user_id": lawyer.user_id,
            "name": lawyer.name,
            "title": lawyer.title,
            "bio": lawyer.bio,
            "phone": lawyer.phone,
            "email": lawyer.email,
            "city": lawyer.city,
            "image_url": lawyer.image_url,
            "languages": lawyer.languages,
            "is_verified": lawyer.is_verified,
            "professional_start_date": lawyer.professional_start_date,
            "catchphrase": lawyer.catchphrase,
            "created_at": lawyer.created_at,
            "updated_at": lawyer.updated_at,
            "areas": processed_areas,
            "review_score": 0.0,  # Default placeholder value
            "review_count": 0     # Default placeholder value
        }
        
        result_lawyers.append(lawyer_dict)
    
    return result_lawyers, total

def create_lawyer(db: Session, lawyer_in: LawyerCreate) -> LawyerModel:
    """
    Create a new lawyer
    """
    # Create lawyer without areas first
    lawyer_data = lawyer_in.dict(exclude={"areas"})
    db_lawyer = LawyerModel(**lawyer_data)
    db.add(db_lawyer)
    db.flush()  # Flush to get the ID
    
    # Now add areas if provided
    if lawyer_in.areas:
        for area_assoc in lawyer_in.areas:
            # Query to get the area
            area = db.query(PracticeArea).filter(PracticeArea.id == area_assoc.area_id).first()
            if area:
                # Add to association table with experience score
                db.execute(
                    lawyer_area_association.insert().values(
                        lawyer_id=db_lawyer.id,
                        area_id=area.id,
                        experience_score=area_assoc.experience_score
                    )
                )
    
    db.commit()
    db.refresh(db_lawyer)
    return db_lawyer

def update_lawyer(db: Session, lawyer: LawyerModel, lawyer_in: LawyerUpdate) -> LawyerModel:
    """
    Update a lawyer
    """
    # Update basic fields
    update_data = lawyer_in.dict(exclude={"areas"}, exclude_unset=True)
    
    for key, value in update_data.items():
        setattr(lawyer, key, value)
    
    # Update areas if provided
    if lawyer_in.areas is not None:
        # First remove all existing relationships
        db.execute(
            lawyer_area_association.delete().where(
                lawyer_area_association.c.lawyer_id == lawyer.id
            )
        )
        
        # Then add the new ones
        for area_assoc in lawyer_in.areas:
            # Add to association table with experience score
            db.execute(
                lawyer_area_association.insert().values(
                    lawyer_id=lawyer.id,
                    area_id=area_assoc.area_id,
                    experience_score=area_assoc.experience_score
                )
            )
    
    db.add(lawyer)
    db.commit()
    db.refresh(lawyer)
    return lawyer

def delete_lawyer(db: Session, lawyer_id: UUID) -> None:
    """
    Delete a lawyer
    """
    lawyer = db.query(LawyerModel).filter(LawyerModel.id == lawyer_id).first()
    if lawyer:
        db.delete(lawyer)
        db.commit()
    return None