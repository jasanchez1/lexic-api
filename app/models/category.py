import uuid
from datetime import datetime, timezone

from sqlalchemy import Column, String, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.db.database import Base

class PracticeAreaCategory(Base):
    __tablename__ = "practice_area_categories"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False)  # Display name (e.g., "Derecho Civil")
    slug = Column(String, nullable=False, unique=True, index=True)  # URL-friendly name (e.g., "civil")
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    
    # Relationship with practice areas
    areas = relationship("app.models.area.PracticeArea", back_populates="category_rel")