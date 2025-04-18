from typing import List, Optional, Tuple, Dict
from uuid import UUID
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import desc, func

from app.models.analytics import GuideView, GuideViewCount
from app.models.guide import Guide, GuideCategory, GuideSection, guide_related_guides
from app.schemas.guide import (
    GuideCategoryCreate,
    GuideCategoryUpdate,
    GuideCreate,
    GuideUpdate,
    GuideSectionUpdate,
    SectionsReorder,
)


def get_guide_by_id(db: Session, guide_id: UUID) -> Optional[Guide]:
    """
    Get a guide by ID with eager-loaded relationships
    """
    return (
        db.query(Guide)
        .options(
            joinedload(Guide.sections),
            joinedload(Guide.related_guides),
            joinedload(Guide.category),
        )
        .filter(Guide.id == guide_id)
        .first()
    )


def get_guide_by_slug(db: Session, slug: str) -> Optional[Guide]:
    """
    Get a guide by slug with eager-loaded relationships
    """
    return (
        db.query(Guide)
        .options(
            joinedload(Guide.sections),
            joinedload(Guide.related_guides),
            joinedload(Guide.category),
        )
        .filter(Guide.slug == slug)
        .first()
    )


def get_guides(
    db: Session,
    skip: int = 0,
    limit: int = 20,
    published_only: bool = False,
    category_slug: Optional[str] = None,
    category_id: Optional[UUID] = None,
) -> Tuple[List[Guide], int]:
    """
    Get a list of guides with pagination and optional filtering
    Returns guides and total count
    """
    query = db.query(Guide).options(joinedload(Guide.category))

    if published_only:
        query = query.filter(Guide.published == True)

    # Handle category filtering
    if category_id:
        # If category_id is provided, use it directly
        query = query.filter(Guide.category_id == category_id)
    elif category_slug:
        # If only category_slug is provided, join with guide_categories table
        query = query.join(GuideCategory, Guide.category_id == GuideCategory.id).filter(
            GuideCategory.slug == category_slug
        )

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

    # Create guide with only valid fields
    if "category_name" in guide_data:
        del guide_data["category_name"]
    if "category_slug" in guide_data:
        del guide_data["category_slug"]

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
            always_open=section.always_open,
        )
        db.add(db_section)

    # Add related guides
    if guide_in.related_guide_ids:
        related_guides = (
            db.query(Guide).filter(Guide.id.in_(guide_in.related_guide_ids)).all()
        )
        db_guide.related_guides = related_guides

    db.commit()
    db.refresh(db_guide)
    return db_guide


def update_guide(db: Session, guide: Guide, guide_in: GuideUpdate) -> Guide:
    """
    Update a guide with sections and related guides
    """
    # Update basic guide fields
    update_data = guide_in.dict(
        exclude={"sections", "related_guide_ids"}, exclude_unset=True
    )

    # Handle category update logic
    if "category_id" in update_data and update_data["category_id"] is not None:
        # If category_id is updated, update legacy fields too
        category = (
            db.query(GuideCategory)
            .filter(GuideCategory.id == update_data["category_id"])
            .first()
        )
        if category:
            update_data["category_name"] = category.name
            update_data["category_slug"] = category.slug
    elif "category_slug" in update_data and update_data["category_slug"] is not None:
        # If only category_slug is updated, look up the category_id
        category = (
            db.query(GuideCategory)
            .filter(GuideCategory.slug == update_data["category_slug"])
            .first()
        )
        if category:
            update_data["category_id"] = category.id
            update_data["category_name"] = category.name

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
                always_open=section.always_open,
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
            related_guides = (
                db.query(Guide).filter(Guide.id.in_(guide_in.related_guide_ids)).all()
            )
            guide.related_guides = related_guides

    db.commit()
    db.refresh(guide)
    return guide


def delete_guide(db: Session, guide_id: UUID) -> None:
    """
    Delete a guide
    """
    try:
        # Fetch the guide from the database
        guide = db.query(Guide).filter(Guide.id == guide_id).first()

        if not guide:
            return None  # Nothing to delete, guide not found

        # Load related views and view counts
        guide_views = db.query(GuideView).filter(GuideView.guide_id == guide_id).all()
        view_count = (
            db.query(GuideViewCount).filter(GuideViewCount.guide_id == guide_id).first()
        )

        # Delete the related records from the session
        for view in guide_views:
            db.delete(view)

        if view_count:
            db.delete(view_count)

        # Clear related_guides relationship (removes rows from `guide_related_guides` table)
        guide.related_guides = []

        # Delete the guide itself
        db.delete(guide)

        # Commit transaction
        db.commit()

    except Exception as e:
        db.rollback()
        print(f"Error deleting guide: {e}")
        raise e

    return None


def check_slug_availability(
    db: Session, slug: str, exclude_id: Optional[UUID] = None
) -> bool:
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


def update_section(
    db: Session, section: GuideSection, section_in: GuideSectionUpdate
) -> GuideSection:
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


def reorder_sections(
    db: Session, guide_id: UUID, order_data: SectionsReorder
) -> List[GuideSection]:
    """
    Reorder guide sections
    """
    # Update each section's display_order
    for item in order_data.section_order:
        db.query(GuideSection).filter(
            GuideSection.id == item.id, GuideSection.guide_id == guide_id
        ).update({"display_order": item.display_order})

    db.commit()

    # Return the updated sections
    return (
        db.query(GuideSection)
        .filter(GuideSection.guide_id == guide_id)
        .order_by(GuideSection.display_order)
        .all()
    )


def get_guide_categories(db: Session) -> List[dict]:
    """
    Get all unique guide categories with counts
    """
    # Query for categories with counts using the new guide_categories table
    results = (
        db.query(
            GuideCategory.id,
            GuideCategory.name,
            GuideCategory.slug,
            func.count(Guide.id).label("guide_count"),
        )
        .outerjoin(Guide, GuideCategory.id == Guide.category_id)
        .filter(Guide.published == True)
        .group_by(GuideCategory.id, GuideCategory.name, GuideCategory.slug)
        .order_by(GuideCategory.name)
        .all()
    )

    return [
        {"id": str(id), "name": name, "slug": slug, "guide_count": guide_count}
        for id, name, slug, guide_count in results
    ]


def get_guide_category_info(db: Session, category_slug: str) -> Optional[Dict]:
    """
    Get guide category info directly from the guide_categories table
    """
    category = (
        db.query(GuideCategory).filter(GuideCategory.slug == category_slug).first()
    )

    if not category:
        return None

    return {
        "id": str(category.id),
        "name": category.name,
        "slug": category.slug,
    }


def get_category_by_id(db: Session, category_id: UUID) -> Optional[GuideCategory]:
    """
    Get a guide category by ID
    """
    return db.query(GuideCategory).filter(GuideCategory.id == category_id).first()


def get_category_by_slug(db: Session, slug: str) -> Optional[GuideCategory]:
    """
    Get a guide category by slug
    """
    return db.query(GuideCategory).filter(GuideCategory.slug == slug).first()


def get_categories(
    db: Session, skip: int = 0, limit: int = 20, with_counts: bool = False
) -> Tuple[List[GuideCategory], int]:
    """
    Get a list of guide categories with pagination
    Returns categories and total count
    """
    query = db.query(GuideCategory)

    # Get total count before pagination
    total = query.count()

    # Apply pagination
    categories = query.order_by(GuideCategory.name).offset(skip).limit(limit).all()

    # Add guide counts if requested
    if with_counts:
        result = []
        for category in categories:
            # Count guides in this category
            guide_count = (
                db.query(func.count(Guide.id))
                .filter(Guide.category_id == category.id)
                .scalar()
                or 0
            )

            # Create a dict with category attributes and guide count
            category_dict = {
                "id": category.id,
                "name": category.name,
                "slug": category.slug,
                "description": category.description,
                "created_at": category.created_at,
                "updated_at": category.updated_at,
                "guide_count": guide_count,
            }
            result.append(category_dict)
        return result, total

    return categories, total


def create_category(db: Session, category: GuideCategoryCreate) -> GuideCategory:
    """
    Create a new guide category
    """
    db_category = GuideCategory(
        name=category.name, slug=category.slug, description=category.description
    )
    db.add(db_category)
    db.commit()
    db.refresh(db_category)
    return db_category


def update_category(
    db: Session, db_category: GuideCategory, category: GuideCategoryUpdate
) -> GuideCategory:
    """
    Update a guide category
    """
    update_data = category.dict(exclude_unset=True)

    for key, value in update_data.items():
        setattr(db_category, key, value)

    db.add(db_category)
    db.commit()
    db.refresh(db_category)
    return db_category


def delete_category(db: Session, category_id: UUID) -> None:
    """
    Delete a guide category
    """
    db_category = (
        db.query(GuideCategory).filter(GuideCategory.id == category_id).first()
    )
    if db_category:
        db.delete(db_category)
        db.commit()
    return None


def check_slug_availability(
    db: Session, slug: str, exclude_id: Optional[UUID] = None
) -> bool:
    """
    Check if a category slug is available for use
    """
    query = db.query(GuideCategory).filter(GuideCategory.slug == slug)

    if exclude_id:
        query = query.filter(GuideCategory.id != exclude_id)

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
