#!/usr/bin/env python3
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import uuid
from datetime import datetime
import sys
import os
import logging
from typing import List, Dict

# Add the parent directory to the path so we can import the app modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.models.featured_item import FeaturedItem
from app.models.guide import GuideCategory
from app.db.database import Base

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Guide slugs to categories mapping (these are your existing guides)
GUIDE_CATEGORIES = {
    "posesion-efectiva-chile": "sucesiones",
    "alzamiento-hipotecas-chile": "inmobiliario",
    "cambio-nombre-apellido-chile": "civil",
    "accidentes-trabajo-chile": "laboral"
}

# Top-level area categories to feature
FEATURED_CATEGORIES = [
    "civil",
    "family",
    "labor",
    "commercial",
    "criminal"
]

# Areas to feature within each category
FEATURED_AREAS = {
    "civil": [
        "contratos",
        "sucesiones",
        "propiedad"
    ],
    "family": [
        "divorcio",
        "pension-alimenticia", 
        "tuicion"
    ],
    "labor": [
        "derechos-laborales",
        "despido-injustificado",
        "accidentes-laborales"
    ],
    "commercial": [
        "constitucion-empresas",
        "contratos-comerciales",
        "propiedad-intelectual"
    ],
    "criminal": [
        "robos-hurtos",
        "estafas",
        "homicidios"
    ]
}

# Top-level topics to feature
FEATURED_TOPICS = [
    "divorcio",
    "derecho-laboral",
    "derecho-civil",
    "derecho-penal",
    "derecho-comercial"
]

# Subtopics to feature within each topic
FEATURED_SUBTOPICS = {
    "divorcio": [
        "divorcios-pension-alimenticia",
        "custodia-menores"
    ],
    "derecho-laboral": [
        "despido-injustificado",
        "acoso-laboral",
        "contratos-laborales"
    ],
    "derecho-civil": [
        "arrendamientos",
        "compraventa-propiedades",
        "herencias-testamentos"
    ],
    "derecho-penal": [
        "delitos-economicos",
        "defensa-criminal",
        "violencia-intrafamiliar"
    ],
    "derecho-comercial": [
        "constitucion-empresas",
        "contratos-comerciales",
        "propiedad-intelectual"
    ]
}

def create_database_session(database_url: str):
    """Create a database session"""
    engine = create_engine(database_url)
    Session = sessionmaker(bind=engine)
    return Session()

def get_guide_ids(session) -> Dict[str, uuid.UUID]:
    """Get IDs of the existing guides by slug"""
    from app.models.guide import Guide
    
    guides = session.query(Guide.id, Guide.slug).all()
    return {guide.slug: guide.id for guide in guides}

def get_category_ids(session) -> Dict[str, uuid.UUID]:
    """Get IDs of the existing categories by slug"""
    from app.models.category import PracticeAreaCategory
    
    categories = session.query(PracticeAreaCategory.id, PracticeAreaCategory.slug).all()
    return {category.slug: category.id for category in categories}

def get_area_ids(session) -> Dict[str, uuid.UUID]:
    """Get IDs of the existing areas by slug"""
    from app.models.area import PracticeArea
    
    areas = session.query(PracticeArea.id, PracticeArea.slug).all()
    return {area.slug: area.id for area in areas}

def get_topic_ids(session) -> Dict[str, uuid.UUID]:
    """Get IDs of the existing topics by slug"""
    from app.models.topic import Topic
    
    topics = session.query(Topic.id, Topic.slug).all()
    return {topic.slug: topic.id for topic in topics}

def get_guide_category_ids(session) -> Dict[str, uuid.UUID]:
    """Get IDs of the existing guide categories by slug"""
    
    categories = session.query(GuideCategory.id, GuideCategory.slug).all()
    return {category.slug: category.id for category in categories}

def ensure_guide_categories_exist(session):
    """
    Ensure guide categories exist in the database, creating them if needed
    """
    # Get existing categories
    existing_categories = get_guide_category_ids(session)
    
    # Collect unique category slugs from guide mappings
    needed_categories = set(GUIDE_CATEGORIES.values())
    
    # Create categories if they don't exist
    for slug in needed_categories:
        if slug not in existing_categories:
            # Create descriptive name from slug
            name = slug.replace("-", " ").title()
            
            # Create new category
            category = GuideCategory(
                id=uuid.uuid4(),
                name=name,
                slug=slug,
                created_at=datetime.now(),
                updated_at=datetime.now()
            )
            session.add(category)
            logger.info(f"Created guide category: {name} ({slug})")
    
    # Commit changes
    session.commit()
    
    # Return updated category mapping
    return get_guide_category_ids(session)

def seed_featured_items(session):
    """Seed the featured items table"""
    
    # Get existing IDs
    guide_ids = get_guide_ids(session)
    category_ids = get_category_ids(session)
    area_ids = get_area_ids(session)
    topic_ids = get_topic_ids(session)
    
    # Ensure guide categories exist
    guide_category_ids = ensure_guide_categories_exist(session)
    
    logger.info(f"Found {len(guide_ids)} guides, {len(category_ids)} categories, {len(area_ids)} areas, "
                f"{len(topic_ids)} topics, {len(guide_category_ids)} guide categories")
    
    # Clear existing featured items (optional - remove this if you want to keep existing items)
    session.query(FeaturedItem).delete()
    logger.info("Cleared existing featured items")
    
    featured_items = []
    
    # Featured Guide Categories
    for i, category_slug in enumerate(sorted(set(GUIDE_CATEGORIES.values()))):
        if category_slug not in guide_category_ids:
            logger.warning(f"Guide category not found: {category_slug}")
            continue
            
        category_id = guide_category_ids[category_slug]
        featured_items.append(
            FeaturedItem(
                id=uuid.uuid4(),
                item_id=category_id,
                item_type="guide_category",
                display_order=i,
                created_at=datetime.now(),
                updated_at=datetime.now()
            )
        )
        logger.info(f"Added featured guide category: {category_slug}")
    
    # Featured Guides within Categories
    for guide_slug, category_slug in GUIDE_CATEGORIES.items():
        if guide_slug not in guide_ids:
            logger.warning(f"Guide not found: {guide_slug}")
            continue
            
        if category_slug not in guide_category_ids:
            logger.warning(f"Guide category not found: {category_slug}")
            continue
            
        category_id = guide_category_ids[category_slug]
        
        # Find position within category
        position = 0
        for slug, cat in GUIDE_CATEGORIES.items():
            if cat == category_slug:
                if slug == guide_slug:
                    break
                position += 1
        
        featured_items.append(
            FeaturedItem(
                id=uuid.uuid4(),
                item_id=guide_ids[guide_slug],
                item_type="guide",
                parent_id=category_id,
                display_order=position,
                created_at=datetime.now(),
                updated_at=datetime.now()
            )
        )
        logger.info(f"Added featured guide: {guide_slug} in category {category_slug}")
    
    # Featured Area Categories
    for i, slug in enumerate(FEATURED_CATEGORIES):
        if slug not in category_ids:
            logger.warning(f"Category not found: {slug}")
            continue
            
        featured_items.append(
            FeaturedItem(
                id=uuid.uuid4(),
                item_id=category_ids[slug],
                item_type="category",
                display_order=i,
                created_at=datetime.now(),
                updated_at=datetime.now()
            )
        )
        logger.info(f"Added featured category: {slug}")
    
    # Featured Areas within Categories
    for category_slug, area_slugs in FEATURED_AREAS.items():
        if category_slug not in category_ids:
            logger.warning(f"Category not found: {category_slug}")
            continue
            
        for i, area_slug in enumerate(area_slugs):
            if area_slug not in area_ids:
                logger.warning(f"Area not found: {area_slug}")
                continue
                
            featured_items.append(
                FeaturedItem(
                    id=uuid.uuid4(),
                    item_id=area_ids[area_slug],
                    item_type="area",
                    parent_id=category_ids[category_slug],
                    display_order=i,
                    created_at=datetime.now(),
                    updated_at=datetime.now()
                )
            )
            logger.info(f"Added featured area: {area_slug} in category {category_slug}")
    
    # Featured Topics
    for i, slug in enumerate(FEATURED_TOPICS):
        if slug not in topic_ids:
            logger.warning(f"Topic not found: {slug}")
            continue
            
        featured_items.append(
            FeaturedItem(
                id=uuid.uuid4(),
                item_id=topic_ids[slug],
                item_type="topic",
                display_order=i,
                created_at=datetime.now(),
                updated_at=datetime.now()
            )
        )
        logger.info(f"Added featured topic: {slug}")
    
    # Featured Subtopics
    for topic_slug, subtopic_slugs in FEATURED_SUBTOPICS.items():
        if topic_slug not in topic_ids:
            logger.warning(f"Topic not found: {topic_slug}")
            continue
            
        for i, subtopic_slug in enumerate(subtopic_slugs):
            if subtopic_slug not in topic_ids:
                logger.warning(f"Subtopic not found: {subtopic_slug}")
                continue
                
            featured_items.append(
                FeaturedItem(
                    id=uuid.uuid4(),
                    item_id=topic_ids[subtopic_slug],
                    item_type="subtopic",
                    parent_id=topic_ids[topic_slug],
                    display_order=i,
                    created_at=datetime.now(),
                    updated_at=datetime.now()
                )
            )
            logger.info(f"Added featured subtopic: {subtopic_slug} in topic {topic_slug}")
    
    # Add all the featured items to the session
    session.add_all(featured_items)
    session.commit()
    
    logger.info(f"Added {len(featured_items)} featured items successfully")

def main():
    # Use DATABASE_URL from environment or set a default
    if not os.environ.get("DATABASE_URL"):
        os.environ["DATABASE_URL"] = "postgresql://postgres:postgres@localhost:5432/lexic_db"
    
    database_url = os.environ["DATABASE_URL"]
    logger.info(f"Connecting to database: {database_url}")
    
    session = create_database_session(database_url)
    try:
        seed_featured_items(session)
        logger.info("Featured items seeded successfully!")
    except Exception as e:
        logger.error(f"Error seeding featured items: {e}")
        session.rollback()
        raise
    finally:
        session.close()

if __name__ == "__main__":
    main()