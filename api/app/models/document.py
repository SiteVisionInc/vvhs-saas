# api/app/models/document.py
"""
Document management models for policy documents, signatures, and volunteer documents.
"""
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text, Date, BigInteger
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship
from datetime import datetime, date, timedelta
from database import Base


class PolicyDocument(Base):
    """
    Organizational policy documents that require acknowledgment.
    """
    __tablename__ = "policy_documents"
    
    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, ForeignKey("tenants.id"), nullable=False)
    
    # Document info
    title = Column(String(255), nullable=False)
    description = Column(Text)
    document_type = Column(String(100), nullable=False)
    version = Column(String(50), nullable=False)
    
    # File storage
    file_url = Column(String(500), nullable=False)
    file_size_bytes = Column(Integer)
    file_hash = Column(String(255))
    
    # Status
    is_active = Column(Boolean, default=True)
    requires_signature = Column(Boolean, default=False)
    
    # Metadata
    created_by = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    effective_date = Column(Date)
    expiration_date = Column(Date)
    
    # Version control
    supersedes_document_id = Column(Integer, ForeignKey("policy_documents.id"))
    
    # Relationships
    signatures = relationship("ElectronicSignature", back_populates="policy_document")
    
    def __repr__(self):
        return f"<PolicyDocument(id={self.id}, title='{self.title}', version='{self.version}')>"
    
    @property
    def is_expired(self) -> bool:
        if not self.expiration_date:
            return False
        return self.expiration_date < date.today()


class ElectronicSignature(Base):
    """
    Electronic signatures for policy acknowledgment and document signing.
    Implements non-repudiation requirements.
    """
    __tablename__ = "electronic_signatures"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Who signed
    volunteer_id = Column(Integer, ForeignKey("volunteers.id"))
    user_id = Column(Integer, ForeignKey("users.id"))
    
    # What was signed
    policy_document_id = Column(Integer, ForeignKey("policy_documents.id"))
    custom_document_id = Column(Integer, ForeignKey("volunteer_documents.id"))
    
    # Signature data
    signature_data = Column(Text)  # Base64 encoded
    signature_method = Column(String(50), nullable=False)
    
    # Legal requirements
    ip_address = Column(String(45), nullable=False)
    user_agent = Column(Text)
    geolocation = Column(JSONB)
    timestamp = Column(DateTime, nullable=False, default=datetime.utcnow)
    
    # Consent
    consent_text = Column(Text, nullable=False)
    acknowledged_terms = Column(Boolean, default=True)
    
    # Verification
    verified = Column(Boolean, default=False)
    verification_method = Column(String(100))
    verified_at = Column(DateTime)
    verified_by = Column(Integer, ForeignKey("users.id"))
    
    # Relationships
    policy_document = relationship("PolicyDocument", back_populates="signatures")
    volunteer = relationship("Volunteer")
    
    def __repr__(self):
        signer = f"volunteer_{self.volunteer_id}" if self.volunteer_id else f"user_{self.user_id}"
        return f"<ElectronicSignature(id={self.id}, signer={signer}, timestamp={self.timestamp})>"


class VolunteerDocument(Base):
    """
    Documents uploaded by or for volunteers (IDs, licenses, certifications, etc.).
    """
    __tablename__ = "volunteer_documents"
    
    id = Column(Integer, primary_key=True, index=True)
    volunteer_id = Column(Integer, ForeignKey("volunteers.id"), nullable=False)
    tenant_id = Column(Integer, ForeignKey("tenants.id"), nullable=False)
    
    # Classification
    document_type = Column(String(100), nullable=False)
    document_category = Column(String(100))
    title = Column(String(255), nullable=False)
    description = Column(Text)
    
    # File storage
    file_url = Column(String(500), nullable=False)
    file_name = Column(String(255))
    file_size_bytes = Column(Integer)
    file_type = Column(String(50))
    file_hash = Column(String(255))
    
    # Expiration
    issue_date = Column(Date)
    expiration_date = Column(Date)
    expires = Column(Boolean, default=False)
    
    # Verification
    verification_status = Column(String(50), default='pending')
    verified_by = Column(Integer, ForeignKey("users.id"))
    verified_at = Column(DateTime)
    rejection_reason = Column(Text)
    
    # Access control
    visibility = Column(String(50), default='private')
    
    # Notifications
    expiration_notified = Column(Boolean, default=False)
    last_notification_date = Column(Date)
    
    # Metadata
    uploaded_by = Column(Integer, ForeignKey("users.id"))
    uploaded_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Audit
    download_count = Column(Integer, default=0)
    last_accessed_at = Column(DateTime)
    
    # Relationships
    volunteer = relationship("Volunteer")
    signatures = relationship("ElectronicSignature", foreign_keys="[ElectronicSignature.custom_document_id]")
    
    def __repr__(self):
        return f"<VolunteerDocument(id={self.id}, type='{self.document_type}', volunteer={self.volunteer_id})>"
    
    @property
    def is_expired(self) -> bool:
        if not self.expires or not self.expiration_date:
            return False
        return self.expiration_date < date.today()
    
    @property
    def days_until_expiration(self) -> int:
        if not self.expires or not self.expiration_date:
            return 999999
        delta = self.expiration_date - date.today()
        return delta.days


class DocumentAccessLog(Base):
    """
    Audit trail for document access (required for HIPAA compliance).
    """
    __tablename__ = "document_access_log"
    
    id = Column(BigInteger, primary_key=True, index=True)
    
    # What
    document_id = Column(Integer)
    document_type = Column(String(100))
    
    # Who
    user_id = Column(Integer, ForeignKey("users.id"))
    volunteer_id = Column(Integer, ForeignKey("volunteers.id"))
    
    # How
    action = Column(String(50), nullable=False)
    ip_address = Column(String(45))
    user_agent = Column(Text)
    
    # When
    accessed_at = Column(DateTime, default=datetime.utcnow, index=True)
    
    # Context
    meta_data = Column("metadata", JSONB)
    
    def __repr__(self):
        return f"<DocumentAccessLog(id={self.id}, action='{self.action}', at={self.accessed_at})>"
