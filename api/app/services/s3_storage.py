# api/app/services/s3_storage.py
"""
S3 document storage service with presigned URLs.
"""
import boto3
import hashlib
import mimetypes
from typing import Optional, Tuple
from botocore.exceptions import ClientError
from config import get_settings

settings = get_settings()


class S3StorageService:
    """
    Service for secure document storage in AWS S3.
    """
    
    def __init__(self):
        self.s3_client = boto3.client(
            's3',
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            region_name=settings.AWS_REGION
        )
        self.bucket_name = settings.S3_BUCKET_NAME
    
    def generate_upload_url(
        self,
        file_name: str,
        file_type: str,
        tenant_id: int,
        document_type: str,
        expires_in: int = 3600
    ) -> Tuple[str, str]:
        """
        Generate presigned URL for direct upload to S3.
        
        Returns:
            Tuple of (presigned_url, s3_key)
        """
        # Generate unique S3 key
        s3_key = self._generate_s3_key(tenant_id, document_type, file_name)
        
        # Content type
        content_type = file_type or mimetypes.guess_type(file_name)[0] or 'application/octet-stream'
        
        try:
            presigned_url = self.s3_client.generate_presigned_url(
                'put_object',
                Params={
                    'Bucket': self.bucket_name,
                    'Key': s3_key,
                    'ContentType': content_type,
                    'ServerSideEncryption': 'AES256',  # Encrypt at rest
                    'Metadata': {
                        'tenant-id': str(tenant_id),
                        'document-type': document_type
                    }
                },
                ExpiresIn=expires_in,
                HttpMethod='PUT'
            )
            
            return presigned_url, s3_key
            
        except ClientError as e:
            raise Exception(f"Failed to generate presigned URL: {str(e)}")
    
    def generate_download_url(
        self,
        s3_key: str,
        expires_in: int = 3600
    ) -> str:
        """
        Generate presigned URL for downloading a document.
        """
        try:
            presigned_url = self.s3_client.generate_presigned_url(
                'get_object',
                Params={
                    'Bucket': self.bucket_name,
                    'Key': s3_key
                },
                ExpiresIn=expires_in
            )
            return presigned_url
            
        except ClientError as e:
            raise Exception(f"Failed to generate download URL: {str(e)}")
    
    def delete_document(self, s3_key: str) -> bool:
        """
        Delete a document from S3.
        """
        try:
            self.s3_client.delete_object(
                Bucket=self.bucket_name,
                Key=s3_key
            )
            return True
        except ClientError as e:
            print(f"Error deleting document: {e}")
            return False
    
    def get_file_hash(self, s3_key: str) -> Optional[str]:
        """
        Calculate SHA-256 hash of file in S3.
        """
        try:
            response = self.s3_client.get_object(
                Bucket=self.bucket_name,
                Key=s3_key
            )
            
            hash_sha256 = hashlib.sha256()
            for chunk in response['Body'].iter_chunks(chunk_size=8192):
                hash_sha256.update(chunk)
            
            return hash_sha256.hexdigest()
            
        except ClientError as e:
            print(f"Error calculating hash: {e}")
            return None
    
    def _generate_s3_key(self, tenant_id: int, document_type: str, file_name: str) -> str:
        """
        Generate organized S3 key path.
        Format: documents/{tenant_id}/{document_type}/{timestamp}_{filename}
        """
        import uuid
        from datetime import datetime
        
        timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
        unique_id = str(uuid.uuid4())[:8]
        safe_filename = file_name.replace(' ', '_').replace('/', '_')
        
        return f"documents/{tenant_id}/{document_type}/{timestamp}_{unique_id}_{safe_filename}"


# Singleton instance
try:
    s3_storage = S3StorageService()
except Exception as e:
    print(f"[WARN] S3StorageService initialization failed: {e}")
    s3_storage = None
