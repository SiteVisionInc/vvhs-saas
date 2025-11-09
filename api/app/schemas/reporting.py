# api/app/schemas/reporting.py
"""
Reporting and analytics schemas.
"""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


class ReportType(str, Enum):
    """Report types."""
    VOLUNTEER_HOURS = "volunteer_hours"
    IMPACT_DATA = "impact_data"
    COMPLIANCE = "compliance"
    UNIT_METRICS = "unit_metrics"
    CUSTOM = "custom"


class AggregationFunction(str, Enum):
    """Aggregation functions."""
    COUNT = "count"
    SUM = "sum"
    AVG = "avg"
    MIN = "min"
    MAX = "max"


class ExportFormat(str, Enum):
    """Export formats."""
    EXCEL = "excel"
    PDF = "pdf"
    CSV = "csv"
    JSON = "json"


# ============ Report Configuration ============

class FilterCondition(BaseModel):
    """Filter condition for report."""
    field: str
    operator: str  # eq, ne, gt, lt, gte, lte, in, contains
    value: Any


class GroupByConfig(BaseModel):
    """Grouping configuration."""
    field: str
    aggregation: Optional[AggregationFunction] = None


class QueryConfig(BaseModel):
    """Report query configuration."""
    entity_type: str
    fields: List[str]
    filters: Optional[List[FilterCondition]] = []
    group_by: Optional[List[GroupByConfig]] = []
    order_by: Optional[List[Dict[str, str]]] = []
    limit: Optional[int] = None


class VisualizationConfig(BaseModel):
    """Chart/visualization configuration."""
    chart_type: str  # bar, line, pie, table
    x_axis: Optional[str] = None
    y_axis: Optional[str] = None
    colors: Optional[List[str]] = None


class ScheduleConfig(BaseModel):
    """Report scheduling configuration."""
    frequency: str  # daily, weekly, monthly
    time: str  # HH:MM
    timezone: str = "America/New_York"
    recipients: List[str]  # Email addresses
    format: ExportFormat = ExportFormat.EXCEL


# ============ Saved Reports ============

class SavedReportCreate(BaseModel):
    """Create saved report."""
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    report_type: ReportType
    query_config: QueryConfig
    visualization_config: Optional[VisualizationConfig] = None
    schedule_config: Optional[ScheduleConfig] = None
    is_public: bool = False
    shared_with_roles: Optional[List[str]] = []
    shared_with_users: Optional[List[int]] = []


class SavedReportUpdate(BaseModel):
    """Update saved report."""
    name: Optional[str] = None
    description: Optional[str] = None
    query_config: Optional[QueryConfig] = None
    visualization_config: Optional[VisualizationConfig] = None
    schedule_config: Optional[ScheduleConfig] = None
    is_public: Optional[bool] = None
    is_active: Optional[bool] = None


class SavedReportResponse(BaseModel):
    """Saved report response."""
    id: int
    tenant_id: int
    name: str
    description: Optional[str]
    report_type: str
    query_config: Dict[str, Any]
    visualization_config: Optional[Dict[str, Any]]
    schedule_config: Optional[Dict[str, Any]]
    is_public: bool
    created_by: int
    created_at: datetime
    updated_at: datetime
    is_active: bool
    last_generated_at: Optional[datetime]
    
    class Config:
        from_attributes = True


# ============ Report Execution ============

class ExecuteReportRequest(BaseModel):
    """Execute report request."""
    export_format: ExportFormat = ExportFormat.EXCEL
    email_to: Optional[List[str]] = None


class ReportExecutionResponse(BaseModel):
    """Report execution response."""
    id: int
    report_id: int
    executed_by: int
    executed_at: datetime
    execution_time_ms: int
    row_count: int
    file_url: Optional[str]
    file_format: str
    status: str
    
    class Config:
        from_attributes = True


# ============ Report Results ============

class ReportResultsResponse(BaseModel):
    """Report results response."""
    columns: List[str]
    rows: List[Dict[str, Any]]
    total_count: int
    execution_time_ms: int
    aggregations: Optional[Dict[str, Any]] = None


# ============ Workflow Automation ============

class WorkflowAction(BaseModel):
    """Workflow action configuration."""
    type: str  # add_to_group, send_email, award_badge, etc.
    config: Dict[str, Any]


class WorkflowCreate(BaseModel):
    """Create workflow."""
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    trigger_report_id: int
    trigger_conditions: Optional[List[FilterCondition]] = []
    actions: List[WorkflowAction]


class WorkflowResponse(BaseModel):
    """Workflow response."""
    id: int
    tenant_id: int
    name: str
    description: Optional[str]
    trigger_report_id: int
    trigger_conditions: Optional[List[Dict[str, Any]]]
    actions: List[Dict[str, Any]]
    is_active: bool
    last_executed_at: Optional[datetime]
    execution_count: int
    created_at: datetime
    
    class Config:
        from_attributes = True


# ============ Pre-built Reports ============

class VolunteerHoursReport(BaseModel):
    """Volunteer hours report results."""
    volunteer_id: int
    volunteer_name: str
    total_hours: float
    approved_hours: float
    pending_hours: float
    events_attended: int
    date_range_start: Optional[datetime]
    date_range_end: Optional[datetime]


class ImpactDataReport(BaseModel):
    """Impact data report results."""
    event_id: int
    event_name: str
    event_date: datetime
    volunteers_assigned: int
    total_hours: float
    impact_metrics: Dict[str, Any]  # vaccines_administered, meals_distributed, etc.


class ComplianceReport(BaseModel):
    """Compliance report results."""
    volunteer_id: int
    volunteer_name: str
    required_trainings: List[str]
    completed_trainings: List[str]
    missing_trainings: List[str]
    expired_certifications: List[str]
    compliance_percentage: float


class UnitMetricsReport(BaseModel):
    """Unit-level metrics report."""
    unit_name: str
    total_volunteers: int
    active_volunteers: int
    total_events: int
    total_hours_served: float
    average_hours_per_volunteer: float
    retention_rate: float
    period_start: datetime
    period_end: datetime
