import uuid
from datetime import datetime, UTC

from sqlalchemy import Column, String, Boolean, DateTime
from sqlalchemy.dialects.postgresql import UUID

from app.db.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    first_name = Column(String, nullable=True)
    last_name = Column(String, nullable=True)
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.now(tz=UTC))
    updated_at = Column(DateTime, default=datetime.now(tz=UTC), onupdate=datetime.now(tz=UTC))
    
    # In a real application you would add relationships to other models
    # For example, a relationship to a UserProfile or LawyerProfile model