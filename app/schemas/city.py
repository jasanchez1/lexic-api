from typing import Optional, List
from uuid import UUID
from pydantic import BaseModel

class CityBase(BaseModel):
    name: str
    slug: str

class CityCreate(CityBase):
    pass

class CityUpdate(BaseModel):
    name: Optional[str] = None
    slug: Optional[str] = None
    is_active: Optional[bool] = None

class CityInDB(CityBase):
    id: UUID
    is_active: bool
    
    class Config:
        from_attributes = True

class City(CityInDB):
    """City schema for API responses"""
    pass

class CitiesList(BaseModel):
    """List of cities"""
    cities: List[City]

