from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.db.repositories import featured_items as featured_repository
from app.db.repositories import areas as areas_repository
from app.db.repositories import categories as categories_repository
from app.db.repositories import topics as topics_repository
from app.db.repositories import guides as guides_repository

router = APIRouter()

@router.get("/menu")
async def get_navigation_menu(db: Session = Depends(get_db)):
    """
    Get combined navigation menu data with manually curated featured items
    """
    # Get featured categories with their featured areas
    featured_categories = featured_repository.get_featured_items_by_type(db, "category")
    areas_result = []
    
    for featured_category in featured_categories:
        category = categories_repository.get_category_by_id(db, featured_category.item_id)
        if not category:
            continue
            
        # Get featured areas for this category
        featured_areas = featured_repository.get_featured_items_by_type(db, "area", category.id)
        areas_data = []
        
        for featured_area in featured_areas:
            area = areas_repository.get_area_by_id(db, featured_area.item_id)
            if not area:
                continue
                
            areas_data.append({
                "id": str(area.id),
                "name": area.name,
                "slug": area.slug
            })
            
        areas_result.append({
            "id": str(category.id),
            "name": category.name,
            "slug": category.slug,
            "featured_areas": areas_data
        })
    
    # Get featured topics with their featured subtopics
    featured_topics = featured_repository.get_featured_items_by_type(db, "topic")
    topics_result = []
    
    for featured_topic in featured_topics:
        topic = topics_repository.get_topic_by_id(db, featured_topic.item_id)
        if not topic:
            continue
            
        # Get featured subtopics for this topic
        featured_subtopics = featured_repository.get_featured_items_by_type(db, "subtopic", topic.id)
        subtopics_data = []
        
        for featured_subtopic in featured_subtopics:
            subtopic = topics_repository.get_topic_by_id(db, featured_subtopic.item_id)
            if not subtopic:
                continue
                
            subtopics_data.append({
                "id": str(subtopic.id),
                "name": subtopic.name,
                "slug": subtopic.slug
            })
            
        topics_result.append({
            "id": str(topic.id),
            "name": topic.name,
            "slug": topic.slug,
            "featured_subtopics": subtopics_data
        })
    
    # Get featured guide categories with their featured guides
    featured_guide_categories = featured_repository.get_featured_items_by_type(db, "guide_category")
    guides_result = []
    
    for featured_category in featured_guide_categories:
        # The item_id for guide_category is the category slug
        category_slug = featured_category.item_id
        category_info = guides_repository.get_guide_category_info(db, category_slug)
        
        if not category_info:
            continue
            
        # Get featured guides for this category
        featured_guides = featured_repository.get_featured_items_by_type(db, "guide", category_slug)
        guides_data = []
        
        for featured_guide in featured_guides:
            guide = guides_repository.get_guide_by_id(db, featured_guide.item_id)
            if not guide or not guide.published:
                continue
                
            guides_data.append({
                "id": str(guide.id),
                "title": guide.title,
                "slug": guide.slug,
                "description": guide.description
            })
            
        guides_result.append({
            "id": category_info["id"],
            "name": category_info["name"],
            "slug": category_info["slug"],
            "featured_guides": guides_data
        })
    
    return {
        "areas": areas_result,
        "topics": topics_result,
        "guides": guides_result
    }