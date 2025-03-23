from typing import Optional
from datetime import datetime
from uuid import UUID
from pydantic import BaseModel

class FeaturedItemBase(BaseModel):
    item_id: UUID
    item_type: str
    parent_id: Optional[UUID] = None
    display_order: int = 0

class FeaturedItemCreate(FeaturedItemBase):
    pass

class FeaturedItemUpdate(BaseModel):
    item_id: Optional[UUID] = None
    item_type: Optional[str] = None
    parent_id: Optional[UUID] = None
    display_order: Optional[int] = None

class FeaturedItemInDB(FeaturedItemBase):
    id: UUID
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class FeaturedItem(FeaturedItemInDB):
    pass