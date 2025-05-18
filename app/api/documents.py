from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, status, Form
from sqlalchemy.orm import Session
from typing import List, Optional
from uuid import UUID

from app.db.database import get_db
from app.db.repositories import documents as documents_repository
from app.db.repositories import lawyers as lawyers_repository
from app.models.user import User
from app.services.storage import StorageService
from app.api.dependencies import get_current_user, get_current_admin_user
from app.schemas.document import (
    DocumentResponse, 
    DocumentVerificationUpdate, 
    LawyerDocumentsResponse,
    DocumentType
)

router = APIRouter()
storage_service = StorageService()

@router.post("/{lawyer_id}/documents", response_model=LawyerDocumentsResponse)
async def upload_documents(
    lawyer_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    supreme_court_certificate: Optional[UploadFile] = None,
    university_degree: Optional[UploadFile] = None,
    document_types: List[str] = Form(...)
):
    """
    Upload one or more documents for a lawyer
    """
    # Verify lawyer exists
    lawyer = lawyers_repository.get_lawyer_by_id(db, lawyer_id)
    if not lawyer:
        raise HTTPException(status_code=404, detail="Lawyer not found")
    
    # Verify current user is either the lawyer owner or an admin
    if lawyer.user_id != current_user.id and not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Not authorized to upload documents for this lawyer")
    
    # Validate document types
    for doc_type in document_types:
        if doc_type not in [e.value for e in DocumentType]:
            raise HTTPException(status_code=400, detail=f"Invalid document type: {doc_type}")
    
    # Process each document
    uploaded_documents = []
    
    if "supreme_court_certificate" in document_types and supreme_court_certificate:
        # Check file size (5MB limit)
        if supreme_court_certificate.size > 5 * 1024 * 1024:
            raise HTTPException(status_code=400, detail="Supreme court certificate exceeds 5MB size limit")
            
        # Check file type
        if supreme_court_certificate.content_type not in ["application/pdf", "image/jpeg", "image/png"]:
            raise HTTPException(status_code=400, detail="Supreme court certificate must be a PDF, JPG, or PNG file")
        
        # Check if document already exists
        existing_doc = documents_repository.get_document_by_type(db, lawyer_id, "supreme_court_certificate")
        if existing_doc:
            # Delete old file
            storage_service.delete_file(existing_doc.file_path)
            # Delete old document record
            documents_repository.delete_document(db, existing_doc.id)
        
        # Upload file
        file_data = await storage_service.upload_file(
            supreme_court_certificate, 
            lawyer_id, 
            "supreme_court_certificate"
        )
        
        # Create document record
        file_data["document_type"] = "supreme_court_certificate"
        doc = documents_repository.create_document(db, lawyer_id, file_data)
        
        # Add to response
        uploaded_documents.append({
            "type": "supreme_court_certificate",
            "status": doc.status,
            "filename": doc.original_filename,
            "upload_date": doc.upload_date,
            "url": file_data["url"]
        })
    
    if "university_degree" in document_types and university_degree:
        # Check file size (5MB limit)
        if university_degree.size > 5 * 1024 * 1024:
            raise HTTPException(status_code=400, detail="University degree exceeds 5MB size limit")
            
        # Check file type
        if university_degree.content_type not in ["application/pdf", "image/jpeg", "image/png"]:
            raise HTTPException(status_code=400, detail="University degree must be a PDF, JPG, or PNG file")
        
        # Check if document already exists
        existing_doc = documents_repository.get_document_by_type(db, lawyer_id, "university_degree")
        if existing_doc:
            # Delete old file
            storage_service.delete_file(existing_doc.file_path)
            # Delete old document record
            documents_repository.delete_document(db, existing_doc.id)
        
        # Upload file
        file_data = await storage_service.upload_file(
            university_degree, 
            lawyer_id, 
            "university_degree"
        )
        
        # Create document record
        file_data["document_type"] = "university_degree"
        doc = documents_repository.create_document(db, lawyer_id, file_data)
        
        # Add to response
        uploaded_documents.append({
            "type": "university_degree",
            "status": doc.status,
            "filename": doc.original_filename,
            "upload_date": doc.upload_date,
            "url": file_data["url"]
        })
    
    # Get all documents for this lawyer
    lawyer_documents = documents_repository.get_documents_by_lawyer(db, lawyer_id)
    
    return {
        "success": True,
        "data": {
            "lawyer_id": str(lawyer_id),
            "documents": uploaded_documents,
            "verification_status": lawyer.verification_status
        },
        "message": "Documents uploaded successfully. They will be reviewed by our team."
    }

@router.get("/{lawyer_id}/documents", response_model=LawyerDocumentsResponse)
async def get_lawyer_documents(
    lawyer_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get all documents for a lawyer
    """
    # Verify lawyer exists
    lawyer = lawyers_repository.get_lawyer_by_id(db, lawyer_id)
    if not lawyer:
        raise HTTPException(status_code=404, detail="Lawyer not found")
    
    # Verify current user is either the lawyer owner or an admin
    if lawyer.user_id != current_user.id and not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Not authorized to access documents for this lawyer")
    
    # Get all documents
    documents = documents_repository.get_documents_by_lawyer(db, lawyer_id)
    
    # Format response
    document_responses = []
    for doc in documents:
        document_responses.append({
            "type": doc.document_type,
            "status": doc.status,
            "filename": doc.original_filename,
            "upload_date": doc.upload_date,
            "review_date": doc.review_date,
            "url": f"/api/lawyers/{lawyer_id}/documents/{doc.document_type}",
            "rejection_reason": doc.rejection_reason
        })
    
    return {
        "success": True,
        "data": {
            "lawyer_id": str(lawyer_id),
            "documents": document_responses,
        }
    }

@router.get("/{lawyer_id}/documents/{document_type}")
async def download_document(
    lawyer_id: UUID,
    document_type: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Download a document
    """
    # Verify lawyer exists
    lawyer = lawyers_repository.get_lawyer_by_id(db, lawyer_id)
    if not lawyer:
        raise HTTPException(status_code=404, detail="Lawyer not found")
    
    # Verify current user is either the lawyer owner or an admin
    if lawyer.user_id != current_user.id and not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Not authorized to access this document")
    
    # Verify document type
    if document_type not in [e.value for e in DocumentType]:
        raise HTTPException(status_code=400, detail=f"Invalid document type: {document_type}")
    
    # Get document
    document = documents_repository.get_document_by_type(db, lawyer_id, document_type)
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    
    # Get file content
    file_content, content_type = storage_service.get_file(document.file_path)
    if not file_content:
        raise HTTPException(status_code=404, detail="File not found in storage")
    
    # Return file
    from fastapi.responses import Response
    return Response(
        content=file_content,
        media_type=content_type,
        headers={
            "Content-Disposition": f"attachment; filename={document.original_filename}"
        }
    )

@router.delete("/{lawyer_id}/documents/{document_type}", status_code=status.HTTP_200_OK)
async def delete_lawyer_document(
    lawyer_id: UUID,
    document_type: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Delete a document
    """
    # Verify lawyer exists
    lawyer = lawyers_repository.get_lawyer_by_id(db, lawyer_id)
    if not lawyer:
        raise HTTPException(status_code=404, detail="Lawyer not found")
    
    # Verify current user is either the lawyer owner or an admin
    if lawyer.user_id != current_user.id and not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Not authorized to delete this document")
    
    # Verify document type
    if document_type not in [e.value for e in DocumentType]:
        raise HTTPException(status_code=400, detail=f"Invalid document type: {document_type}")
    
    # Get document
    document = documents_repository.get_document_by_type(db, lawyer_id, document_type)
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    
    # Delete file
    storage_service.delete_file(document.file_path)
    
    # Delete document record
    documents_repository.delete_document(db, document.id)
    
    return {
        "success": True,
        "message": "Document deleted successfully"
    }

@router.put("/admin/lawyers/{lawyer_id}/documents/{document_type}/verify", response_model=LawyerDocumentsResponse)
async def verify_document(
    lawyer_id: UUID,
    document_type: str,
    verification: DocumentVerificationUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """
    Admin endpoint to verify a document
    """
    # Verify lawyer exists
    lawyer = lawyers_repository.get_lawyer_by_id(db, lawyer_id)
    if not lawyer:
        raise HTTPException(status_code=404, detail="Lawyer not found")
    
    # Verify document type
    if document_type not in [e.value for e in DocumentType]:
        raise HTTPException(status_code=400, detail=f"Invalid document type: {document_type}")
    
    # Get document
    document = documents_repository.get_document_by_type(db, lawyer_id, document_type)
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    
    # Validate rejection reason
    if verification.status == "rejected" and not verification.rejection_reason:
        raise HTTPException(status_code=400, detail="Rejection reason is required when rejecting a document")
    
    # Update document status
    updated_document = documents_repository.update_document_status(
        db, 
        document.id, 
        verification.status, 
        current_user.id, 
        verification.rejection_reason
    )
    
    # Get the updated lawyer to get the new verification status
    updated_lawyer = lawyers_repository.get_lawyer_by_id(db, lawyer_id)
    
    return {
        "success": True,
        "data": {
            "document": {
                "type": updated_document.document_type,
                "status": updated_document.status,
                "filename": updated_document.original_filename,
                "upload_date": updated_document.upload_date,
                "review_date": updated_document.review_date
            },
            "lawyer_verification_status": updated_lawyer.verification_status
        },
        "message": "Document verification status updated successfully"
    }
