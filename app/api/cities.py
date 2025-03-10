from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from uuid import UUID

from app.db.database import get_db
from app.db.repositories import cities as cities_repository
from app.schemas.city import City, CityCreate, CityUpdate, CitiesList

router = APIRouter()

@router.get("", response_model=List[City])
async def get_cities(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100
):
    """
    Retrieve all cities
    """
    return cities_repository.get_cities(db, skip, limit)

@router.get("/{city_id}", response_model=City)
async def get_city(
    city_id: UUID,
    db: Session = Depends(get_db)
):
    """
    Retrieve a specific city by ID
    """
    db_city = cities_repository.get_city_by_id(db, city_id)
    if db_city is None:
        raise HTTPException(status_code=404, detail="City not found")
    return db_city

@router.get("/slug/{slug}", response_model=City)
async def get_city_by_slug(
    slug: str,
    db: Session = Depends(get_db)
):
    """
    Retrieve a specific city by slug
    """
    db_city = cities_repository.get_city_by_slug(db, slug)
    if db_city is None:
        raise HTTPException(status_code=404, detail="City not found")
    return db_city

@router.post("", response_model=City, status_code=status.HTTP_201_CREATED)
async def create_city(
    city: CityCreate,
    db: Session = Depends(get_db)
):
    """
    Create a new city
    """
    # Check if a city with the same slug already exists
    db_city = cities_repository.get_city_by_slug(db, city.slug)
    if db_city:
        raise HTTPException(
            status_code=400,
            detail="City with this slug already exists"
        )
        
    return cities_repository.create_city(db, city)

@router.patch("/{city_id}", response_model=City)
async def update_city(
    city_id: UUID,
    city: CityUpdate,
    db: Session = Depends(get_db)
):
    """
    Update a city
    """
    db_city = cities_repository.get_city_by_id(db, city_id)
    if db_city is None:
        raise HTTPException(status_code=404, detail="City not found")
        
    # Check if slug is being updated and is unique
    if city.slug is not None and city.slug != db_city.slug:
        existing_city = cities_repository.get_city_by_slug(db, city.slug)
        if existing_city:
            raise HTTPException(
                status_code=400,
                detail="City with this slug already exists"
            )
            
    return cities_repository.update_city(db, db_city, city)

@router.delete("/{city_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_city(
    city_id: UUID,
    db: Session = Depends(get_db)
):
    """
    Delete a city
    """
    db_city = cities_repository.get_city_by_id(db, city_id)
    if db_city is None:
        raise HTTPException(status_code=404, detail="City not found")
        
    cities_repository.delete_city(db, city_id)
    return None

