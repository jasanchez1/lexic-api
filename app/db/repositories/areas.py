from typing import List, Optional, Dict
from uuid import UUID
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func

from app.models.area import PracticeArea as PracticeAreaModel
from app.models.area import lawyer_area_association
from app.schemas.area import PracticeAreaCreate, PracticeAreaUpdate
from app.models.category import PracticeAreaCategory

def get_area_by_id(db: Session, area_id: UUID) -> Optional[PracticeAreaModel]:
    """
    Get a practice area by ID
    """
    return db.query(PracticeAreaModel).options(
        joinedload(PracticeAreaModel.category_rel)
    ).filter(PracticeAreaModel.id == area_id).first()

def get_area_by_slug(db: Session, slug: str) -> Optional[PracticeAreaModel]:
    """
    Get a practice area by slug
    """
    return db.query(PracticeAreaModel).options(
        joinedload(PracticeAreaModel.category_rel)
    ).filter(PracticeAreaModel.slug == slug).first()

def get_areas(
    db: Session, 
    skip: int = 0, 
    limit: int = 100, 
    category_id: Optional[UUID] = None,
    category_slug: Optional[str] = None
) -> List[PracticeAreaModel]:
    """
    Get a list of practice areas with optional category filtering
    """
    query = db.query(PracticeAreaModel).options(
        joinedload(PracticeAreaModel.category_rel)
    )
    
    if category_id:
        query = query.filter(PracticeAreaModel.category_id == category_id)

    if category_slug:
        query = query.join(PracticeAreaCategory).filter(PracticeAreaCategory.slug == category_slug)
        
    return query.offset(skip).limit(limit).all()

def get_areas_with_counts(db: Session) -> List[dict]:
    """
    Get all practice areas with lawyer counts
    """
    results = db.query(
        PracticeAreaModel,
        func.count(lawyer_area_association.c.lawyer_id).label('lawyer_count')
    ).options(
        joinedload(PracticeAreaModel.category_rel)
    ).outerjoin(
        lawyer_area_association,
        PracticeAreaModel.id == lawyer_area_association.c.area_id
    ).group_by(
        PracticeAreaModel.id
    ).all()
    
    return [
        {
            "area": area,
            "lawyer_count": count
        }
        for area, count in results
    ]

def get_areas_by_category(db: Session) -> Dict[str, List[PracticeAreaModel]]:
    """
    Get practice areas grouped by category
    """
    areas = db.query(PracticeAreaModel).options(
        joinedload(PracticeAreaModel.category_rel)
    ).all()
    grouped = {}
    
    for area in areas:
        category_id = str(area.category_id)
        if category_id not in grouped:
            grouped[category_id] = []
        grouped[category_id].append(area)
        
    return grouped

def create_area(db: Session, area_in: PracticeAreaCreate) -> PracticeAreaModel:
    """
    Create a new practice area
    """
    db_area = PracticeAreaModel(
        name=area_in.name,
        slug=area_in.slug,
        category_id=area_in.category_id,
        description=area_in.description,
    )
    db.add(db_area)
    db.commit()
    db.refresh(db_area)
    return db_area

def update_area(db: Session, area: PracticeAreaModel, area_in: PracticeAreaUpdate) -> PracticeAreaModel:
    """
    Update a practice area
    """
    update_data = area_in.dict(exclude_unset=True)
    
    for key, value in update_data.items():
        setattr(area, key, value)
        
    db.add(area)
    db.commit()
    db.refresh(area)
    return area

def delete_area(db: Session, area_id: UUID) -> None:
    """
    Delete a practice area
    """
    area = db.query(PracticeAreaModel).filter(PracticeAreaModel.id == area_id).first()
    if area:
        db.delete(area)
        db.commit()
    return None