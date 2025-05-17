from typing import List, Optional, Dict
from uuid import UUID
from sqlalchemy.orm import Session
from datetime import datetime, timezone

from app.models.document import LawyerDocument
from app.models.lawyer import Lawyer

def get_document_by_id(db: Session, document_id: UUID) -> Optional[LawyerDocument]:
    """Get a document by ID"""
    return db.query(LawyerDocument).filter(LawyerDocument.id == document_id).first()

def get_documents_by_lawyer(db: Session, lawyer_id: UUID) -> List[LawyerDocument]:
    """Get all documents for a lawyer"""
    return db.query(LawyerDocument).filter(LawyerDocument.lawyer_id == lawyer_id).all()

def get_document_by_type(db: Session, lawyer_id: UUID, document_type: str) -> Optional[LawyerDocument]:
    """Get a specific document type for a lawyer"""
    return db.query(LawyerDocument).filter(
        LawyerDocument.lawyer_id == lawyer_id,
        LawyerDocument.document_type == document_type
    ).first()

def create_document(db: Session, lawyer_id: UUID, document_data: Dict) -> LawyerDocument:
    """Create a new document"""
    db_document = LawyerDocument(
        lawyer_id=lawyer_id,
        document_type=document_data["document_type"],
        filename=document_data["filename"],
        original_filename=document_data["original_filename"],
        file_path=document_data["file_path"],
        file_size=document_data["file_size"],
        mime_type=document_data["mime_type"],
        status="pending_review"
    )
    db.add(db_document)
    db.commit()
    db.refresh(db_document)
    
    # Update lawyer verification status
    update_lawyer_verification_status(db, lawyer_id)
    
    return db_document

def update_document_status(db: Session, document_id: UUID, status: str, user_id: UUID, rejection_reason: Optional[str] = None) -> LawyerDocument:
    """Update a document status"""
    document = get_document_by_id(db, document_id)
    if not document:
        return None
        
    document.status = status
    document.review_date = datetime.now(timezone.utc)
    document.reviewed_by = user_id
    
    if status == "rejected" and rejection_reason:
        document.rejection_reason = rejection_reason
    
    db.add(document)
    db.commit()
    db.refresh(document)
    
    # Update lawyer verification status
    update_lawyer_verification_status(db, document.lawyer_id)
    
    return document

def delete_document(db: Session, document_id: UUID) -> bool:
    """Delete a document"""
    document = get_document_by_id(db, document_id)
    if not document:
        return False
        
    lawyer_id = document.lawyer_id
    
    db.delete(document)
    db.commit()
    
    # Update lawyer verification status
    update_lawyer_verification_status(db, lawyer_id)
    
    return True

def update_lawyer_verification_status(db: Session, lawyer_id: UUID) -> None:
    """Update lawyer verification status based on document statuses"""
    lawyer = db.query(Lawyer).filter(Lawyer.id == lawyer_id).first()
    if not lawyer:
        return
    
    documents = get_documents_by_lawyer(db, lawyer_id)
    
    # No documents
    if not documents:
        lawyer.verification_status = "pending"
        db.add(lawyer)
        db.commit()
        return
    
    # Check document statuses
    has_rejected = False
    has_approved = False
    all_approved = True
    
    for doc in documents:
        if doc.status == "rejected":
            has_rejected = True
            all_approved = False
        elif doc.status == "approved":
            has_approved = True
        else:  # pending_review
            all_approved = False
    
    # Determine verification status
    if has_rejected:
        lawyer.verification_status = "rejected"
    elif all_approved:
        lawyer.verification_status = "verified"
    elif has_approved:
        lawyer.verification_status = "partial"
    else:
        lawyer.verification_status = "pending"
    
    db.add(lawyer)
    db.commit()
