import uuid
from datetime import datetime, timezone

from sqlalchemy import Column, String, DateTime, ForeignKey, Integer
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.db.database import Base

class LawyerDocument(Base):
    __tablename__ = "lawyer_documents"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    lawyer_id = Column(UUID(as_uuid=True), ForeignKey("lawyers.id", ondelete="CASCADE"), nullable=False)
    document_type = Column(String(50), nullable=False)
    filename = Column(String(255), nullable=False)  # Generated filename in storage
    original_filename = Column(String(255), nullable=False)  # Original uploaded filename
    file_path = Column(String(512), nullable=False)  # Full path in storage (S3 or local)
    file_size = Column(Integer, nullable=False)
    mime_type = Column(String(100), nullable=False)
    status = Column(String(20), nullable=False, default="pending_review")  # pending_review, approved, rejected
    upload_date = Column(DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))
    review_date = Column(DateTime, nullable=True)
    reviewed_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    rejection_reason = Column(String, nullable=True)
    
    # Relationships
    lawyer = relationship("app.models.lawyer.Lawyer", backref="documents")
    reviewer = relationship("app.models.user.User", foreign_keys=[reviewed_by])