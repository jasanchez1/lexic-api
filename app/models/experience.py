import uuid
from datetime import datetime, timezone

from sqlalchemy import Column, String, Text, Integer, DateTime, ForeignKey, JSON
from sqlalchemy.dialects.postgresql import UUID, ARRAY
from sqlalchemy.orm import relationship

from app.db.database import Base

class Education(Base):
    __tablename__ = "education"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    lawyer_id = Column(UUID(as_uuid=True), ForeignKey("lawyers.id", ondelete="CASCADE"), nullable=False)
    institution = Column(String, nullable=False)
    degree = Column(String, nullable=False)
    year = Column(Integer, nullable=True)
    honors = Column(String, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    # Relationship
    lawyer = relationship("app.models.lawyer.Lawyer", back_populates="education")

class WorkExperience(Base):
    __tablename__ = "work_experience"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    lawyer_id = Column(UUID(as_uuid=True), ForeignKey("lawyers.id", ondelete="CASCADE"), nullable=False)
    role = Column(String, nullable=False)
    company = Column(String, nullable=False)
    start_date = Column(String, nullable=True)  # Format: YYYY-MM
    end_date = Column(String, nullable=True)    # Format: YYYY-MM or "Present"
    description = Column(Text, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    # Relationship
    lawyer = relationship("app.models.lawyer.Lawyer", back_populates="work_experience")

class Achievement(Base):
    __tablename__ = "achievements"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    lawyer_id = Column(UUID(as_uuid=True), ForeignKey("lawyers.id", ondelete="CASCADE"), nullable=False)
    title = Column(String, nullable=False)
    year = Column(Integer, nullable=True)
    issuer = Column(String, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    # Relationship
    lawyer = relationship("app.models.lawyer.Lawyer", back_populates="achievements")
