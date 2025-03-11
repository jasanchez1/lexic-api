import uuid
from datetime import datetime, timezone
from typing import List

from sqlalchemy import Column, String, Boolean, DateTime, ForeignKey, Text, ARRAY
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.db.database import Base
from app.models.area import lawyer_area_association

class Lawyer(Base):
    __tablename__ = "lawyers"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    name = Column(String, nullable=False)
    title = Column(String, nullable=True)
    bio = Column(Text, nullable=True)
    phone = Column(String, nullable=True)
    email = Column(String, nullable=False, unique=True, index=True)
    city = Column(String, nullable=True)
    image_url = Column(String, nullable=True)
    languages = Column(ARRAY(String), nullable=True)
    is_verified = Column(Boolean, default=False)
    professional_start_date = Column(DateTime, nullable=True)
    catchphrase = Column(String, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    
    # Relationship with user - using string to avoid circular import
    user = relationship("app.models.user.User", backref="lawyer_profile")
    
    # Relationship with practice areas
    areas = relationship(
        "app.models.area.PracticeArea", 
        secondary=lawyer_area_association,
        back_populates="lawyers"
    )
    # Additional relationships
    reviews = relationship("app.models.review.Review", back_populates="lawyer", cascade="all, delete-orphan")
    education = relationship("app.models.experience.Education", back_populates="lawyer", cascade="all, delete-orphan") 
    work_experience = relationship("app.models.experience.WorkExperience", back_populates="lawyer", cascade="all, delete-orphan")
    achievements = relationship("app.models.experience.Achievement", back_populates="lawyer", cascade="all, delete-orphan")
    messages = relationship("app.models.message.Message", back_populates="lawyer", cascade="all, delete-orphan")
    calls = relationship("app.models.message.Call", back_populates="lawyer", cascade="all, delete-orphan")
