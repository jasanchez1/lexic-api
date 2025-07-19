import uuid
from datetime import datetime, timezone
from uuid import UUID as PyUUID

from sqlalchemy import Column, String, Text, Boolean, DateTime, ForeignKey, Integer
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.db.database import Base

class Conversation(Base):
    __tablename__ = "conversations"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    lawyer_id = Column(UUID(as_uuid=True), ForeignKey("lawyers.id", ondelete="CASCADE"), nullable=False)
    last_message = Column(Text, nullable=True)
    last_message_date = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    unread_count = Column(Integer, default=0)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    # Relationships
    user = relationship("app.models.user.User", foreign_keys=[user_id], backref="conversations")
    lawyer = relationship("app.models.lawyer.Lawyer", foreign_keys=[lawyer_id], backref="conversations")
    messages = relationship("ConversationMessage", back_populates="conversation", cascade="all, delete-orphan")

class ConversationMessage(Base):
    __tablename__ = "conversation_messages"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    conversation_id = Column(UUID(as_uuid=True), ForeignKey("conversations.id", ondelete="CASCADE"), nullable=False)
    content = Column(Text, nullable=False)
    user_id_from = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    user_id_to = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    from_lawyer = Column(Boolean, default=False)  # Keep for backward compatibility during transition
    read = Column(Boolean, default=False)
    timestamp = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    # Relationships
    conversation = relationship("Conversation", back_populates="messages")
    sender = relationship("app.models.user.User", foreign_keys=[user_id_from])
    recipient = relationship("app.models.user.User", foreign_keys=[user_id_to])
    
    def is_from_lawyer(self, lawyer_user_id: PyUUID) -> bool:
        """Check if this message is from a lawyer by comparing sender with lawyer's user_id"""
        if self.user_id_from:
            return self.user_id_from == lawyer_user_id
        # Fallback to existing from_lawyer field for backward compatibility
        return self.from_lawyer
    
    def is_to_lawyer(self, lawyer_user_id: PyUUID) -> bool:
        """Check if this message is to a lawyer by comparing recipient with lawyer's user_id"""
        if self.user_id_to:
            return self.user_id_to == lawyer_user_id
        # Fallback to inverse of from_lawyer field for backward compatibility
        return not self.from_lawyer