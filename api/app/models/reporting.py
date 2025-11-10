# api/app/models/reporting.py
"""
Reporting models.
"""
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship
from datetime import datetime
from database import Base


class SavedReport(Base):
    """Saved report configuration."""
    __tablename__ = "saved_reports"
    
    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, ForeignKey("tenants.id"), nullable=False, index=True)
    
    # Report metadata
    name = Column(String(255), nullable=False)
    description = Column(Text)
    report_type = Column(String(100), nullable=False, index=True)
    
    # Configuration
    query_config = Column(JSONB, nullable=False)
    visualization_config = Column(JSONB)
    
    # Scheduling
    schedule_config = Column(JSONB)
    last_generated_at = Column(DateTime)
    next_scheduled_at = Column(DateTime)
    
    # Sharing
    is_public = Column(Boolean, default=False)
    shared_with_roles = Column(Text)
    shared_with_users = Column(Text)
    
    # Ownership
    created_by = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Status
    is_active = Column(Boolean, default=True)
    
    # Relationships
    executions = relationship("ReportExecution", back_populates="report", cascade="all, delete-orphan")


class ReportExecution(Base):
    """Report execution history."""
    __tablename__ = "report_executions"
    
    id = Column(Integer, primary_key=True, index=True)
    report_id = Column(Integer, ForeignKey("saved_reports.id"), nullable=False)
    
    # Execution details
    executed_by = Column(Integer, ForeignKey("users.id"))
    executed_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    execution_time_ms = Column(Integer)
    row_count = Column(Integer)
    
    # Output
    file_url = Column(String(500))
    file_format = Column(String(20))
    file_size_bytes = Column(Integer)
    
    # Status
    status = Column(String(50), default='pending')
    error_message = Column(Text)
    
    # Relationships
    report = relationship("SavedReport", back_populates="executions")


class ReportField(Base):
    """Report builder field definitions."""
    __tablename__ = "report_fields"
    
    id = Column(Integer, primary_key=True, index=True)
    entity_type = Column(String(100), nullable=False)
    field_name = Column(String(100), nullable=False)
    field_label = Column(String(255), nullable=False)
    field_type = Column(String(50), nullable=False)
    is_filterable = Column(Boolean, default=True)
    is_groupable = Column(Boolean, default=True)
    is_aggregatable = Column(Boolean, default=False)
    aggregation_functions = Column(Text)


class ReportWorkflow(Base):
    """Workflow automation rules."""
    __tablename__ = "report_workflows"
    
    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, ForeignKey("tenants.id"), nullable=False)
    
    # Workflow details
    name = Column(String(255), nullable=False)
    description = Column(Text)
    
    # Trigger
    trigger_report_id = Column(Integer, ForeignKey("saved_reports.id"))
    trigger_conditions = Column(JSONB)
    
    # Actions
    actions = Column(JSONB, nullable=False)
    
    # Status
    is_active = Column(Boolean, default=True)
    last_executed_at = Column(DateTime)
    execution_count = Column(Integer, default=0)
    
    # Metadata
    created_by = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    executions = relationship("WorkflowExecution", back_populates="workflow", cascade="all, delete-orphan")


class WorkflowExecution(Base):
    """Workflow execution log."""
    __tablename__ = "workflow_executions"
    
    id = Column(Integer, primary_key=True, index=True)
    workflow_id = Column(Integer, ForeignKey("report_workflows.id"), nullable=False)
    
    # Execution details
    executed_at = Column(DateTime, default=datetime.utcnow)
    records_processed = Column(Integer)
    records_affected = Column(Integer)
    
    # Status
    status = Column(String(50), default='pending')
    error_message = Column(Text)
    execution_log = Column(JSONB)
    
    # Relationships
    workflow = relationship("ReportWorkflow", back_populates="executions")
