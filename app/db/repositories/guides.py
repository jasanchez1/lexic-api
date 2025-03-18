from typing import List, Optional, Tuple
from uuid import UUID
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func, desc, asc

from app.models.guide import Guide, GuideSection, guide_related_guides
from app.schemas.guide import GuideCreate, GuideUpdate, GuideSectionCreate, GuideSectionUpdate, SectionsReorder

def get_guide_by_id(db: Session, guide_id: UUID) -> Optional[Guide]:
    """
    Get a guide by ID with eager-loaded relationships
    """
    return db.query(Guide).options(
        joinedload(Guide.sections),
        joinedload(Guide.related_guides)
    ).filter(Guide.id == guide_id).first()

def get_guide_by_slug(db: Session, slug: str) -> Optional[Guide]:
    """
    Get a guide by slug with eager-loaded relationships
    """
    return db.query(Guide).options(
        joinedload(Guide.sections),
        joinedload(Guide.related_guides)
    ).filter(Guide.slug == slug).first()

def get_guides(
    db: Session, 
    skip: int = 0, 
    limit: int = 20,
    published_only: bool = False
) -> Tuple[List[Guide], int]:
    """
    Get a list of guides with pagination
    Returns guides and total count
    """
    query = db.query(Guide)
    
    if published_only:
        query = query.filter(Guide.published == True)
    
    # Get total count before pagination
    total = query.count()
    
    # Apply pagination and return results
    guides = query.order_by(desc(Guide.created_at)).offset(skip).limit(limit).all()
    
    return guides, total

def create_guide(db: Session, guide_in: GuideCreate) -> Guide:
    """
    Create a new guide with sections and related guides
    """
    # Create guide
    guide_data = guide_in.dict(exclude={"sections", "related_guide_ids"})
    
    # If slug is not provided, generate from title
    if not guide_data.get("slug"):
        from slugify import slugify
        guide_data["slug"] = slugify(guide_data["title"])
    
    db_guide = Guide(**guide_data)
    db.add(db_guide)
    db.flush()  # Flush to get the ID
    
    # Create sections
    for section in guide_in.sections:
        db_section = GuideSection(
            guide_id=db_guide.id,
            section_id=section.section_id,
            title=section.title,
            content=section.content,
            display_order=section.display_order,
            always_open=section.always_open
        )
        db.add(db_section)
    
    # Add related guides
    if guide_in.related_guide_ids:
        related_guides = db.query(Guide).filter(Guide.id.in_(guide_in.related_guide_ids)).all()
        db_guide.related_guides = related_guides
    
    db.commit()
    db.refresh(db_guide)
    return db_guide

def update_guide(db: Session, guide: Guide, guide_in: GuideUpdate) -> Guide:
    """
    Update a guide with sections and related guides
    """
    # Update basic guide fields
    update_data = guide_in.dict(exclude={"sections", "related_guide_ids"}, exclude_unset=True)
    
    for key, value in update_data.items():
        setattr(guide, key, value)
    
    # Update sections if provided
    if guide_in.sections is not None:
        # Delete existing sections
        db.query(GuideSection).filter(GuideSection.guide_id == guide.id).delete()
        
        # Create new sections
        for section in guide_in.sections:
            db_section = GuideSection(
                guide_id=guide.id,
                section_id=section.section_id,
                title=section.title,
                content=section.content,
                display_order=section.display_order,
                always_open=section.always_open
            )
            db.add(db_section)
    
    # Update related guides if provided
    if guide_in.related_guide_ids is not None:
        # Clear existing relationships
        db.execute(
            guide_related_guides.delete().where(
                guide_related_guides.c.guide_id == guide.id
            )
        )
        
        if guide_in.related_guide_ids:
            # Add new relationships
            related_guides = db.query(Guide).filter(Guide.id.in_(guide_in.related_guide_ids)).all()
            guide.related_guides = related_guides
    
    db.commit()
    db.refresh(guide)
    return guide

def delete_guide(db: Session, guide_id: UUID) -> None:
    """
    Delete a guide
    """
    guide = db.query(Guide).filter(Guide.id == guide_id).first()
    if guide:
        db.delete(guide)
        db.commit()
    return None

def check_slug_availability(db: Session, slug: str, exclude_id: Optional[UUID] = None) -> bool:
    """
    Check if a slug is available for use
    """
    query = db.query(Guide).filter(Guide.slug == slug)
    
    if exclude_id:
        query = query.filter(Guide.id != exclude_id)
    
    return query.first() is None

def get_slug_suggestion(db: Session, base_slug: str) -> str:
    """
    Generate a unique slug suggestion based on a base slug
    """
    from slugify import slugify
    
    # Make sure base_slug is slugified
    slug = slugify(base_slug)
    
    # Check if the base slug is available
    if check_slug_availability(db, slug):
        return slug
    
    # If not, try appending numbers
    counter = 1
    while True:
        new_slug = f"{slug}-{counter}"
        if check_slug_availability(db, new_slug):
            return new_slug
        counter += 1

# Guide section repository functions
def get_section_by_id(db: Session, section_id: UUID) -> Optional[GuideSection]:
    """
    Get a guide section by ID
    """
    return db.query(GuideSection).filter(GuideSection.id == section_id).first()

def update_section(db: Session, section: GuideSection, section_in: GuideSectionUpdate) -> GuideSection:
    """
    Update a guide section
    """
    update_data = section_in.dict(exclude_unset=True)
    
    for key, value in update_data.items():
        setattr(section, key, value)
    
    db.add(section)
    db.commit()
    db.refresh(section)
    return section

def reorder_sections(db: Session, guide_id: UUID, order_data: SectionsReorder) -> List[GuideSection]:
    """
    Reorder guide sections
    """
    # Update each section's display_order
    for item in order_data.section_order:
        db.query(GuideSection).filter(
            GuideSection.id == item.id,
            GuideSection.guide_id == guide_id
        ).update({"display_order": item.display_order})
    
    db.commit()
    
    # Return the updated sections
    return db.query(GuideSection).filter(
        GuideSection.guide_id == guide_id
    ).order_by(GuideSection.display_order).all()