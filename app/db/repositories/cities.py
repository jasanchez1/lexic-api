from typing import List, Optional
from uuid import UUID
from sqlalchemy.orm import Session

from app.models.city import City
from app.schemas.city import CityCreate, CityUpdate

def get_city_by_id(db: Session, city_id: UUID) -> Optional[City]:
    """
    Get a city by ID
    """
    return db.query(City).filter(City.id == city_id).first()

def get_city_by_slug(db: Session, slug: str) -> Optional[City]:
    """
    Get a city by slug
    """
    return db.query(City).filter(City.slug == slug).first()

def get_cities(db: Session, skip: int = 0, limit: int = 100, active_only: bool = True) -> List[City]:
    """
    Get a list of cities with optional active filtering
    """
    query = db.query(City)
    
    if active_only:
        query = query.filter(City.is_active == True)
        
    return query.order_by(City.name).offset(skip).limit(limit).all()

def create_city(db: Session, city: CityCreate) -> City:
    """
    Create a new city
    """
    db_city = City(
        name=city.name,
        slug=city.slug,
        is_active=True
    )
    db.add(db_city)
    db.commit()
    db.refresh(db_city)
    return db_city

def update_city(db: Session, city: City, city_in: CityUpdate) -> City:
    """
    Update a city
    """
    update_data = city_in.dict(exclude_unset=True)
    
    for key, value in update_data.items():
        setattr(city, key, value)
        
    db.add(city)
    db.commit()
    db.refresh(city)
    return city

def delete_city(db: Session, city_id: UUID) -> None:
    """
    Delete a city
    """
    city = db.query(City).filter(City.id == city_id).first()
    if city:
        db.delete(city)
        db.commit()
    return None

