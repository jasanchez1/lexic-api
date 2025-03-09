import uuid
from datetime import datetime, timezone

from sqlalchemy import Column, String, DateTime, ForeignKey, Table, Integer
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.db.database import Base

# Association table for many-to-many relationships between lawyers and practice areas
lawyer_area_association = Table(
    'lawyer_areas',
    Base.metadata,
    Column('lawyer_id', UUID(as_uuid=True), ForeignKey('lawyers.id', ondelete="CASCADE"), primary_key=True),
    Column('area_id', UUID(as_uuid=True), ForeignKey('practice_areas.id', ondelete="CASCADE"), primary_key=True),
    Column('experience_score', Integer, default=0),  # 0-100 score representing expertise level
)

class PracticeArea(Base):
    __tablename__ = "practice_areas"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False)
    slug = Column(String, nullable=False, unique=True, index=True)
    category_id = Column(UUID(as_uuid=True), ForeignKey("practice_area_categories.id", ondelete="CASCADE"), nullable=False)
    description = Column(String, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    
    # Relationship with category
    category_rel = relationship("app.models.category.PracticeAreaCategory", back_populates="areas")
    
    # Relationship with lawyers
    lawyers = relationship(
        "app.models.lawyer.Lawyer", 
        secondary=lawyer_area_association,
        back_populates="areas"
    )