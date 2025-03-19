import uuid
from datetime import datetime, timezone

from sqlalchemy import Column, String, DateTime, ForeignKey, Integer, Boolean
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.db.database import Base

class ProfileView(Base):
    __tablename__ = "profile_views"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    lawyer_id = Column(UUID(as_uuid=True), ForeignKey("lawyers.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    source = Column(String, nullable=True)  # Where the click came from (e.g., "name", "button", etc.)
    timestamp = Column(DateTime, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    # Relationships
    lawyer = relationship("app.models.lawyer.Lawyer", backref="profile_views")
    user = relationship("app.models.user.User", backref="profile_views")

class ProfileViewCount(Base):
    __tablename__ = "profile_view_counts"

    lawyer_id = Column(UUID(as_uuid=True), ForeignKey("lawyers.id", ondelete="CASCADE"), primary_key=True)
    count = Column(Integer, default=0)
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    # Relationships
    lawyer = relationship("app.models.lawyer.Lawyer", backref="profile_view_count")

class MessageEvent(Base):
    __tablename__ = "message_events"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    lawyer_id = Column(UUID(as_uuid=True), ForeignKey("lawyers.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    status = Column(String, nullable=False)  # "opened", "sent", etc.
    timestamp = Column(DateTime, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    # Relationships
    lawyer = relationship("app.models.lawyer.Lawyer", backref="message_events")
    user = relationship("app.models.user.User", backref="message_events")

class MessageEventCount(Base):
    __tablename__ = "message_event_counts"

    lawyer_id = Column(UUID(as_uuid=True), ForeignKey("lawyers.id", ondelete="CASCADE"), primary_key=True)
    status = Column(String, primary_key=True)  # "opened", "sent", etc.
    count = Column(Integer, default=0)
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    # Relationships
    lawyer = relationship("app.models.lawyer.Lawyer", backref="message_event_counts")

class CallEvent(Base):
    __tablename__ = "call_events"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    lawyer_id = Column(UUID(as_uuid=True), ForeignKey("lawyers.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    completed = Column(Boolean, default=False)
    timestamp = Column(DateTime, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    # Relationships
    lawyer = relationship("app.models.lawyer.Lawyer", backref="call_events")
    user = relationship("app.models.user.User", backref="call_events")

class CallEventCount(Base):
    __tablename__ = "call_event_counts"

    lawyer_id = Column(UUID(as_uuid=True), ForeignKey("lawyers.id", ondelete="CASCADE"), primary_key=True)
    count = Column(Integer, default=0)
    completed_count = Column(Integer, default=0)
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    # Relationships
    lawyer = relationship("app.models.lawyer.Lawyer", backref="call_event_count")

class ProfileImpression(Base):
    __tablename__ = "profile_impressions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    lawyer_id = Column(UUID(as_uuid=True), ForeignKey("lawyers.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    search_query = Column(String, nullable=True)
    area_slug = Column(String, nullable=True)
    city_slug = Column(String, nullable=True)
    position = Column(Integer, nullable=True)
    timestamp = Column(DateTime, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    # Relationships
    lawyer = relationship("app.models.lawyer.Lawyer", backref="profile_impressions")
    user = relationship("app.models.user.User", backref="profile_impressions")

class ProfileImpressionCount(Base):
    __tablename__ = "profile_impression_counts"

    lawyer_id = Column(UUID(as_uuid=True), ForeignKey("lawyers.id", ondelete="CASCADE"), primary_key=True)
    count = Column(Integer, default=0)
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    # Relationships
    lawyer = relationship("app.models.lawyer.Lawyer", backref="profile_impression_count")

class ListingClick(Base):
    __tablename__ = "listing_clicks"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    lawyer_id = Column(UUID(as_uuid=True), ForeignKey("lawyers.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    search_query = Column(String, nullable=True)
    area_slug = Column(String, nullable=True)
    city_slug = Column(String, nullable=True)
    position = Column(Integer, nullable=True)
    timestamp = Column(DateTime, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    # Relationships
    lawyer = relationship("app.models.lawyer.Lawyer", backref="listing_clicks")
    user = relationship("app.models.user.User", backref="listing_clicks")

class ListingClickCount(Base):
    __tablename__ = "listing_click_counts"

    lawyer_id = Column(UUID(as_uuid=True), ForeignKey("lawyers.id", ondelete="CASCADE"), primary_key=True)
    count = Column(Integer, default=0)
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    # Relationships
    lawyer = relationship("app.models.lawyer.Lawyer", backref="listing_click_count")

class GuideView(Base):
    __tablename__ = "guide_views"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    guide_id = Column(UUID(as_uuid=True), ForeignKey("guides.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    timestamp = Column(DateTime, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    # Relationships
    guide = relationship("app.models.guide.Guide", backref="analytics_guide_views")
    user = relationship("app.models.user.User", backref="guide_views")

class GuideViewCount(Base):
    __tablename__ = "guide_view_counts"

    guide_id = Column(UUID(as_uuid=True), ForeignKey("guides.id", ondelete="CASCADE"), primary_key=True)
    count = Column(Integer, default=0)
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    guide = relationship("Guide", foreign_keys=[guide_id], passive_deletes=True)


class QuestionView(Base):
    __tablename__ = "question_views"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    question_id = Column(UUID(as_uuid=True), ForeignKey("questions.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    timestamp = Column(DateTime, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    # Relationships
    question = relationship("app.models.question.Question", backref="question_views")
    user = relationship("app.models.user.User", backref="question_views")

class QuestionViewCount(Base):
    __tablename__ = "question_view_counts"

    question_id = Column(UUID(as_uuid=True), ForeignKey("questions.id", ondelete="CASCADE"), primary_key=True)
    count = Column(Integer, default=0)
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    # Relationships
    question = relationship("app.models.question.Question", backref="analytics_view_count")
