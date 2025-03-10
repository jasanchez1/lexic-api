import uuid
from datetime import datetime, timezone

from sqlalchemy import Column, String, Text, Integer, Boolean, DateTime, ForeignKey, Table
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.db.database import Base

# Association table for answer helpful votes
answer_helpful_votes = Table(
    'answer_helpful_votes',
    Base.metadata,
    Column('answer_id', UUID(as_uuid=True), ForeignKey('answers.id', ondelete="CASCADE"), primary_key=True),
    Column('user_id', UUID(as_uuid=True), ForeignKey('users.id', ondelete="CASCADE"), primary_key=True),
    Column('created_at', DateTime, default=lambda: datetime.now(timezone.utc))
)

class Answer(Base):
    __tablename__ = "answers"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    content = Column(Text, nullable=False)
    question_id = Column(UUID(as_uuid=True), ForeignKey("questions.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    lawyer_id = Column(UUID(as_uuid=True), ForeignKey("lawyers.id", ondelete="SET NULL"), nullable=True)
    is_accepted = Column(Boolean, default=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    # Relationships
    question = relationship("app.models.question.Question", back_populates="answers")
    user = relationship("app.models.user.User", foreign_keys=[user_id], backref="answers")
    lawyer = relationship("app.models.lawyer.Lawyer", foreign_keys=[lawyer_id], backref="answers")
    replies = relationship("Reply", back_populates="answer", cascade="all, delete-orphan")
    helpful_users = relationship("app.models.user.User", 
                                secondary=answer_helpful_votes,
                                backref="helpful_answers")

class Reply(Base):
    __tablename__ = "replies"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    content = Column(Text, nullable=False)
    answer_id = Column(UUID(as_uuid=True), ForeignKey("answers.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    # Relationships
    answer = relationship("Answer", back_populates="replies")
    user = relationship("app.models.user.User", backref="replies")

