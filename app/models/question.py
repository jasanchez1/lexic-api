import uuid
from datetime import datetime, timezone
from enum import Enum as PyEnum

from sqlalchemy import Column, String, Text, Integer, DateTime, ForeignKey, Enum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.db.database import Base

class PlanToHire(str, PyEnum):
    yes = "yes"
    no = "no"
    maybe = "maybe"
    
class Question(Base):
    __tablename__ = "questions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title = Column(String, nullable=False)
    content = Column(Text, nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    location = Column(String, nullable=True)
    plan_to_hire = Column(Enum(PlanToHire), default=PlanToHire.maybe)
    view_count = Column(Integer, default=0)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    # Relationships
    user = relationship("app.models.user.User", backref="questions")
    topics = relationship("app.models.topic.Topic", 
                          secondary="question_topics",
                          back_populates="questions")
    answers = relationship("Answer", back_populates="question", cascade="all, delete-orphan")

