"""
Tenant model for multi-tenant SaaS architecture.
Each tenant represents a health district or organization.
"""
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text
from sqlalchemy.orm import relationship
from datetime import datetime
from database import Base


class Tenant(Base):
    """
    Tenant/Organization model.
    Represents a health district or MRC unit using the system.
    """
    __tablename__ = "tenants"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False, unique=True, index=True)
    slug = Column(String(100), nullable=False, unique=True, index=True)
    contact_email = Column(String(255), nullable=False)
    contact_phone = Column(String(20))
    
    # Address information
    address_line1 = Column(String(255))
    address_line2 = Column(String(255))
    city = Column(String(100))
    state = Column(String(2), default="VA")
    zip_code = Column(String(10))
    
    # Status and settings
    is_active = Column(Boolean, default=True, nullable=False)
    settings = Column(Text)  # JSON field for tenant-specific settings
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    users = relationship("User", back_populates="tenant", cascade="all, delete-orphan")
    volunteers = relationship("Volunteer", back_populates="tenant", cascade="all, delete-orphan")
    events = relationship("Event", back_populates="tenant", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Tenant(id={self.id}, name='{self.name}', slug='{self.slug}')>"
