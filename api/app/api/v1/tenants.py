"""
Tenant management endpoints for SaaS administration.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from database import get_db
from models.tenant import Tenant
from models.user import User, UserRole
from schemas.tenant import TenantCreate, TenantUpdate, TenantResponse, TenantListResponse
from api.deps import get_current_user, require_role
from services.audit import log_action

router = APIRouter()


@router.get("/", response_model=TenantListResponse)
def list_tenants(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role([UserRole.SYSTEM_ADMIN]))
):
    """
    List all tenants (System Admin only).
    """
    tenants = db.query(Tenant).offset(skip).limit(limit).all()
    total = db.query(Tenant).count()
    
    return TenantListResponse(total=total, items=tenants)


@router.post("/", response_model=TenantResponse, status_code=status.HTTP_201_CREATED)
def create_tenant(
    tenant_data: TenantCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role([UserRole.SYSTEM_ADMIN]))
):
    """
    Create a new tenant (System Admin only).
    """
    # Check if tenant with slug already exists
    existing = db.query(Tenant).filter(Tenant.slug == tenant_data.slug).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Tenant with this slug already exists"
        )
    
    tenant = Tenant(**tenant_data.dict())
    db.add(tenant)
    db.commit()
    db.refresh(tenant)
    
    # Log action
    log_action(
        db=db,
        user_id=current_user.id,
        tenant_id=current_user.tenant_id,
        action="tenant.created",
        resource_type="tenant",
        resource_id=tenant.id,
        description=f"Created tenant: {tenant.name}",
        new_values=tenant_data.dict()
    )
    
    return tenant


@router.get("/{tenant_id}", response_model=TenantResponse)
def get_tenant(
    tenant_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role([UserRole.SYSTEM_ADMIN]))
):
    """
    Get tenant by ID.
    """
    tenant = db.query(Tenant).filter(Tenant.id == tenant_id).first()
    if not tenant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tenant not found"
        )
    return tenant


@router.put("/{tenant_id}", response_model=TenantResponse)
def update_tenant(
    tenant_id: int,
    tenant_data: TenantUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role([UserRole.SYSTEM_ADMIN]))
):
    """
    Update tenant.
    """
    tenant = db.query(Tenant).filter(Tenant.id == tenant_id).first()
    if not tenant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tenant not found"
        )
    
    # Store old values for audit
    old_values = {
        "name": tenant.name,
        "contact_email": tenant.contact_email,
        "is_active": tenant.is_active
    }
    
    # Update fields
    for field, value in tenant_data.dict(exclude_unset=True).items():
        setattr(tenant, field, value)
    
    db.commit()
    db.refresh(tenant)
    
    # Log action
    log_action(
        db=db,
        user_id=current_user.id,
        tenant_id=current_user.tenant_id,
        action="tenant.updated",
        resource_type="tenant",
        resource_id=tenant.id,
        description=f"Updated tenant: {tenant.name}",
        old_values=old_values,
        new_values=tenant_data.dict(exclude_unset=True)
    )
    
    return tenant


@router.delete("/{tenant_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_tenant(
    tenant_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role([UserRole.SYSTEM_ADMIN]))
):
    """
    Delete tenant (soft delete by setting is_active=False).
    """
    tenant = db.query(Tenant).filter(Tenant.id == tenant_id).first()
    if not tenant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tenant not found"
        )
    
    tenant.is_active = False
    db.commit()
    
    # Log action
    log_action(
        db=db,
        user_id=current_user.id,
        tenant_id=current_user.tenant_id,
        action="tenant.deleted",
        resource_type="tenant",
        resource_id=tenant.id,
        description=f"Deleted tenant: {tenant.name}"
    )
    
    return None
