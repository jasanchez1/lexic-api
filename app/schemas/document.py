from typing import List, Optional
from datetime import datetime
from uuid import UUID
from pydantic import BaseModel
from fastapi import UploadFile, File
from enum import Enum

# Document type enum for validation
class DocumentType(str, Enum):
    SUPREME_COURT_CERTIFICATE = "supreme_court_certificate"
    UNIVERSITY_DEGREE = "university_degree"

# Status enum for validation
class DocumentStatus(str, Enum):
    PENDING_REVIEW = "pending_review"
    APPROVED = "approved"
    REJECTED = "rejected"

# Lawyer verification status enum
class VerificationStatus(str, Enum):
    PENDING = "pending"
    PARTIAL = "partial"
    VERIFIED = "verified"
    REJECTED = "rejected"

# Document response schema
class DocumentResponse(BaseModel):
    type: str
    status: DocumentStatus
    filename: str
    upload_date: datetime
    review_date: Optional[datetime] = None
    url: str
    rejection_reason: Optional[str] = None

    class Config:
        from_attributes = True

# Request to update document verification status (for admins)
class DocumentVerificationUpdate(BaseModel):
    status: DocumentStatus
    rejection_reason: Optional[str] = None

# Full response with all lawyer documents
class LawyerDocumentsResponse(BaseModel):
    success: bool
    data: dict
    message: Optional[str] = None