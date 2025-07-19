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
    participant_1_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    participant_2_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    last_message = Column(Text, nullable=True)
    last_message_date = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    # Relationships
    participant_1 = relationship("app.models.user.User", foreign_keys=[participant_1_id])
    participant_2 = relationship("app.models.user.User", foreign_keys=[participant_2_id])
    messages = relationship("ConversationMessage", back_populates="conversation", cascade="all, delete-orphan")
    
    def get_other_participant(self, current_user_id: PyUUID):
        """Get the other participant in the conversation"""
        if self.participant_1_id == current_user_id:
            return self.participant_2
        elif self.participant_2_id == current_user_id:
            return self.participant_1
        else:
            return None
    
    def is_participant(self, user_id: PyUUID) -> bool:
        """Check if user is a participant in this conversation"""
        return user_id in [self.participant_1_id, self.participant_2_id]

class ConversationMessage(Base):
    __tablename__ = "conversation_messages"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    conversation_id = Column(UUID(as_uuid=True), ForeignKey("conversations.id", ondelete="CASCADE"), nullable=False)
    sender_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    content = Column(Text, nullable=False)
    read = Column(Boolean, default=False)
    timestamp = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    # Relationships
    conversation = relationship("Conversation", back_populates="messages")
    sender = relationship("app.models.user.User", foreign_keys=[sender_id])
    
    def is_from_me(self, current_user_id: PyUUID) -> bool:
        """Check if this message was sent by the current user"""
        return self.sender_id == current_user_id