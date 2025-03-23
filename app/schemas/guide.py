from typing import List, Optional
from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, Field


# Guide Section schemas
from typing import List, Optional
from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, Field


# Guide Section schemas
class GuideSectionBase(BaseModel):
    section_id: str
    title: str
    content: str
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


# Guide Category reference
class GuideCategoryReference(BaseModel):
    id: UUID
    name: str
    slug: str


# Guide schemas
class GuideBase(BaseModel):
    title: str
    slug: Optional[str] = None
    description: Optional[str] = None
    published: bool = False
    category_id: Optional[UUID] = None
    
    # Legacy fields (to be removed after transition)
    category_name: Optional[str] = None
    category_slug: Optional[str] = None


class GuideCreate(GuideBase):
    sections: List[GuideSectionCreate] = []
    related_guide_ids: List[UUID] = []


class GuideUpdate(BaseModel):
    title: Optional[str] = None
    slug: Optional[str] = None
    description: Optional[str] = None
    published: Optional[bool] = None
    category_id: Optional[UUID] = None
    sections: Optional[List[GuideSectionCreate]] = None
    related_guide_ids: Optional[List[UUID]] = None
    
    # Legacy fields (to be removed after transition)
    category_name: Optional[str] = None
    category_slug: Optional[str] = None


class GuideInDB(GuideBase):
    id: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class GuideListItem(GuideInDB):
    category: Optional[GuideCategoryReference] = None


class GuideDetail(GuideInDB):
    sections: List[GuideSection] = []
    related_guides: List[RelatedGuideBase] = []
    category: Optional[GuideCategoryReference] = None


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


class GuideCategoryBase(BaseModel):
    name: str
    slug: str
    description: Optional[str] = None


class GuideCategoryCreate(GuideCategoryBase):
    pass


class GuideCategoryUpdate(BaseModel):
    name: Optional[str] = None
    slug: Optional[str] = None
    description: Optional[str] = None


class GuideCategoryInDB(GuideCategoryBase):
    id: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class GuideCategory(GuideCategoryInDB):
    """Guide category schema for API responses"""
    pass


class GuideCategoryWithGuides(GuideCategory):
    """Guide category with guides count"""
    guide_count: int = 0


class GuideCategoryList(BaseModel):
    """List of categories with pagination"""
    categories: List[GuideCategoryWithGuides]
    total: int
    page: Optional[int] = 1
    pages: Optional[int] = 1