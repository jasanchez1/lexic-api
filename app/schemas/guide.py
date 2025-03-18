from typing import List, Optional
from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, Field

# Guide Section schemas
class GuideSectionBase(BaseModel):
    section_id: str  # e.g., "que-es", "procedimiento"
    title: str
    content: str  # HTML content
    display_order: int = 0
    always_open: bool = False

class GuideSectionCreate(GuideSectionBase):
    pass

class GuideSectionUpdate(BaseModel):
    section_id: Optional[str] = None
    title: Optional[str] = None
    content: Optional[str] = None
    display_order: Optional[int] = None
    always_open: Optional[bool] = None

class GuideSectionInDB(GuideSectionBase):
    id: UUID
    guide_id: UUID
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class GuideSection(GuideSectionInDB):
    pass

# Guide Section Reorder schema
class SectionOrderItem(BaseModel):
    id: UUID
    display_order: int

class SectionsReorder(BaseModel):
    section_order: List[SectionOrderItem]

# Related Guide schema for responses
class RelatedGuideBase(BaseModel):
    id: UUID
    title: str
    slug: str
    description: Optional[str] = None

# Guide schemas
class GuideBase(BaseModel):
    title: str
    slug: Optional[str] = None
    description: Optional[str] = None
    published: bool = False

class GuideCreate(GuideBase):
    sections: List[GuideSectionCreate] = []
    related_guide_ids: List[UUID] = []

class GuideUpdate(BaseModel):
    title: Optional[str] = None
    slug: Optional[str] = None
    description: Optional[str] = None
    published: Optional[bool] = None
    sections: Optional[List[GuideSectionCreate]] = None
    related_guide_ids: Optional[List[UUID]] = None

class GuideInDB(GuideBase):
    id: UUID
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class GuideListItem(GuideInDB):
    pass

class GuideDetail(GuideInDB):
    sections: List[GuideSection] = []
    related_guides: List[RelatedGuideBase] = []

# List response with pagination
class GuidesList(BaseModel):
    guides: List[GuideListItem]
    total: int
    page: int
    pages: int

# Slug check response
class SlugCheckResponse(BaseModel):
    available: bool
    suggestion: Optional[str] = None

# Image upload response
class ImageUploadResponse(BaseModel):
    url: str
    name: str
    size: int

# Generic success/error responses
class SuccessResponse(BaseModel):
    success: bool = True
    data: Optional[dict] = None

class ErrorResponse(BaseModel):
    success: bool = False
    error: str
    errors: Optional[List[str]] = None