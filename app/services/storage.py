import os
import boto3
from botocore.exceptions import ClientError
from fastapi import UploadFile
import uuid
from app.core.config import settings

class StorageService:
    """Service for handling file storage (S3 or local filesystem)"""
    
    def __init__(self):
        self.use_s3 = settings.USE_S3_STORAGE
        
        if self.use_s3:
            self.s3_client = boto3.client(
                's3',
                aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
                region_name=settings.AWS_REGION
            )
            self.bucket_name = settings.S3_BUCKET_NAME
        else:
            # Ensure local storage directory exists
            self.storage_path = settings.LOCAL_STORAGE_PATH
            os.makedirs(self.storage_path, exist_ok=True)
    
    async def upload_file(self, file: UploadFile, lawyer_id: uuid.UUID, document_type: str) -> dict:
        """
        Upload a file to storage (S3 or local filesystem)
        Returns file metadata
        """
        # Read file content
        file_content = await file.read()
        
        # Generate unique filename
        file_extension = os.path.splitext(file.filename)[1]
        environment = settings.ENVIRONMENT

        filename = f"{uuid.uuid4()}{file_extension}"
        
        # Create storage path
        relative_path = f"{environment}/lawyers/{lawyer_id}/documents/{document_type}/{filename}"
        
        if self.use_s3:
            # Upload to S3
            try:
                self.s3_client.put_object(
                    Body=file_content,
                    Bucket=self.bucket_name,
                    Key=relative_path,
                    ContentType=file.content_type
                )
                file_url = f"https://{self.bucket_name}.s3.amazonaws.com/{relative_path}"
            except ClientError as e:
                raise Exception(f"S3 upload error: {str(e)}")
        else:
            # Save to local filesystem
            full_path = os.path.join(self.storage_path, relative_path)
            os.makedirs(os.path.dirname(full_path), exist_ok=True)
            
            with open(full_path, "wb") as f:
                f.write(file_content)
            
            file_url = f"/api/lawyers/{lawyer_id}/documents/{document_type}"
        
        # Return file metadata
        return {
            "filename": filename,
            "original_filename": file.filename,
            "file_path": relative_path,
            "file_size": len(file_content),
            "mime_type": file.content_type,
            "url": file_url
        }
    
    def get_file_url(self, file_path: str) -> str:
        """Get the URL for a file in storage"""
        if self.use_s3:
            return f"https://{self.bucket_name}.s3.amazonaws.com/{file_path}"
        else:
            return f"/api/storage/{file_path}"
    
    def get_file(self, file_path: str):
        """Get a file from storage"""
        if self.use_s3:
            try:
                response = self.s3_client.get_object(
                    Bucket=self.bucket_name,
                    Key=file_path
                )
                return response['Body'].read(), response['ContentType']
            except ClientError as e:
                raise Exception(f"S3 download error: {str(e)}")
        else:
            full_path = os.path.join(self.storage_path, file_path)
            if not os.path.exists(full_path):
                return None, None
                
            with open(full_path, "rb") as f:
                content = f.read()
            
            # Determine content type based on file extension
            import mimetypes
            content_type, _ = mimetypes.guess_type(file_path)
            
            return content, content_type or "application/octet-stream"
    
    def delete_file(self, file_path: str) -> bool:
        """Delete a file from storage"""
        if self.use_s3:
            try:
                self.s3_client.delete_object(
                    Bucket=self.bucket_name,
                    Key=file_path
                )
                return True
            except ClientError as e:
                raise Exception(f"S3 delete error: {str(e)}")
        else:
            full_path = os.path.join(self.storage_path, file_path)
            if os.path.exists(full_path):
                os.remove(full_path)
                return True
            return False
