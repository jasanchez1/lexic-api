import uuid
from datetime import datetime, timezone

from sqlalchemy import (
    Column,
    String,
    Text,
    Integer,
    Boolean,
    DateTime,
    ForeignKey,
    Table,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.db.database import Base

# Association table for many-to-many relationships between guides and related guides
guide_related_guides = Table(
    "guide_related_guides",
    Base.metadata,
    Column(
        "guide_id",
        UUID(as_uuid=True),
        ForeignKey("guides.id", ondelete="CASCADE"),
        primary_key=True,
    ),
    Column(
        "related_guide_id",
        UUID(as_uuid=True),
        ForeignKey("guides.id", ondelete="CASCADE"),
        primary_key=True,
    ),
)


class Guide(Base):
    __tablename__ = "guides"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title = Column(String, nullable=False)
    slug = Column(String, nullable=False, unique=True, index=True)
    description = Column(Text, nullable=True)
    published = Column(Boolean, default=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )
    
    category_id = Column(UUID(as_uuid=True), ForeignKey("guide_categories.id", ondelete="SET NULL"), nullable=True)
    category = relationship("GuideCategory", back_populates="guides")

    sections = relationship(
        "GuideSection", back_populates="guide", cascade="all, delete-orphan"
    )
    guide_views = relationship(
        "GuideView", back_populates="guide", passive_deletes=True
    )
    related_guides = relationship(
        "Guide",
        secondary=guide_related_guides,
        primaryjoin=(id == guide_related_guides.c.guide_id),
        secondaryjoin=(id == guide_related_guides.c.related_guide_id),
        backref="related_to",
    )
    view_count = relationship(
        "GuideViewCount", cascade="all, delete-orphan", passive_deletes=True
    )

class GuideSection(Base):
    __tablename__ = "guide_sections"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    guide_id = Column(
        UUID(as_uuid=True), ForeignKey("guides.id", ondelete="CASCADE"), nullable=False
    )
    section_id = Column(String, nullable=False)  # e.g., "que-es", "procedimiento"
    title = Column(String, nullable=False)
    content = Column(Text, nullable=False)  # HTML content
    display_order = Column(Integer, default=0)
    always_open = Column(Boolean, default=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    # Relationship with guide
    guide = relationship("Guide", back_populates="sections")

    class Config:
        orm_mode = True


class GuideCategory(Base):
    __tablename__ = "guide_categories"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False)
    slug = Column(String, nullable=False, unique=True, index=True)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    # Relationship with guides
    guides = relationship("Guide", back_populates="category")
