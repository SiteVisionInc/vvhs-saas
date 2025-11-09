# api/app/api/v1/reporting.py
"""
Reporting and analytics endpoints.
"""
from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_, text
from typing import List, Optional, Dict, Any
from datetime import datetime, date, timedelta
import io
import pandas as pd
from openpyxl import Workbook

from database import get_db
from models.user import User
from models.volunteer import Volunteer
from models.event import Event
from models.time_tracking import TimeEntry
from models.training import VolunteerTraining, Certification
from models.reporting import SavedReport, ReportExecution, ReportField, ReportWorkflow
from api.deps import get_current_user
from schemas.reporting import (
    SavedReportCreate,
    SavedReportUpdate,
    SavedReportResponse,
    ExecuteReportRequest,
    ReportExecutionResponse,
    ReportResultsResponse,
    WorkflowCreate,
    WorkflowResponse,
    VolunteerHoursReport,
    ImpactDataReport,
    ComplianceReport,
    UnitMetricsReport,
    ExportFormat
)

router = APIRouter()


# ============ Saved Reports ============

@router.get("/reports", response_model=List[SavedReportResponse])
def list_saved_reports(
    report_type: Optional[str] = None,
    include_shared: bool = True,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List saved reports accessible to current user."""
    query = db.query(SavedReport).filter(
        SavedReport.tenant_id == current_user.tenant_id,
        SavedReport.is_active == True
    )
    
    if report_type:
        query = query.filter(SavedReport.report_type == report_type)
    
    # Filter by access
    if include_shared:
        query = query.filter(
            or_(
                SavedReport.created_by == current_user.id,
                SavedReport.is_public == True,
                # TODO: Check shared_with_roles and shared_with_users
            )
        )
    else:
        query = query.filter(SavedReport.created_by == current_user.id)
    
    reports = query.order_by(SavedReport.created_at.desc()).offset(skip).limit(limit).all()
    return reports


@router.post("/reports", response_model=SavedReportResponse, status_code=status.HTTP_201_CREATED)
def create_saved_report(
    report_data: SavedReportCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new saved report."""
    report = SavedReport(
        tenant_id=current_user.tenant_id,
        **report_data.dict(),
        created_by=current_user.id
    )
    
    db.add(report)
    db.commit()
    db.refresh(report)
    
    return report


@router.get("/reports/{report_id}", response_model=SavedReportResponse)
def get_saved_report(
    report_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get saved report by ID."""
    report = db.query(SavedReport).filter(
        SavedReport.id == report_id,
        SavedReport.tenant_id == current_user.tenant_id
    ).first()
    
    if not report:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Report not found"
        )
    
    # TODO: Check access permissions
    
    return report


@router.patch("/reports/{report_id}", response_model=SavedReportResponse)
def update_saved_report(
    report_id: int,
    report_data: SavedReportUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update saved report."""
    report = db.query(SavedReport).filter(
        SavedReport.id == report_id,
        SavedReport.tenant_id == current_user.tenant_id
    ).first()
    
    if not report:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Report not found"
        )
    
    # Only creator can update
    if report.created_by != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only report creator can update"
        )
    
    for field, value in report_data.dict(exclude_unset=True).items():
        setattr(report, field, value)
    
    db.commit()
    db.refresh(report)
    
    return report


@router.delete("/reports/{report_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_saved_report(
    report_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete saved report."""
    report = db.query(SavedReport).filter(
        SavedReport.id == report_id,
        SavedReport.tenant_id == current_user.tenant_id,
        SavedReport.created_by == current_user.id
    ).first()
    
    if not report:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Report not found"
        )
    
    db.delete(report)
    db.commit()


# ============ Report Execution ============

@router.post("/reports/{report_id}/execute")
def execute_report(
    report_id: int,
    request: ExecuteReportRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Execute a report and return results."""
    report = db.query(SavedReport).filter(
        SavedReport.id == report_id,
        SavedReport.tenant_id == current_user.tenant_id
    ).first()
    
    if not report:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Report not found"
        )
    
    start_time = datetime.utcnow()
    
    try:
        # Build query based on configuration
        results = build_and_execute_query(
            db=db,
            tenant_id=current_user.tenant_id,
            query_config=report.query_config
        )
        
        execution_time = int((datetime.utcnow() - start_time).total_seconds() * 1000)
        
        # Create execution record
        execution = ReportExecution(
            report_id=report_id,
            executed_by=current_user.id,
            execution_time_ms=execution_time,
            row_count=len(results.get('rows', [])),
            file_format=request.export_format,
            status='completed'
        )
        
        db.add(execution)
        
        # Update last generated time
        report.last_generated_at = datetime.utcnow()
        
        db.commit()
        db.refresh(execution)
        
        # If export requested, generate file in background
        if request.export_format != ExportFormat.JSON:
            background_tasks.add_task(
                generate_export_file,
                execution_id=execution.id,
                results=results,
                format=request.export_format,
                db=db
            )
        
        return {
            "execution_id": execution.id,
            "results": results if request.export_format == ExportFormat.JSON else None,
            "status": "completed",
            "execution_time_ms": execution_time
        }
        
    except Exception as e:
        execution = ReportExecution(
            report_id=report_id,
            executed_by=current_user.id,
            status='failed',
            error_message=str(e)
        )
        db.add(execution)
        db.commit()
        
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Report execution failed: {str(e)}"
        )


# ============ Pre-built Reports ============

@router.get("/reports/volunteer-hours", response_model=List[VolunteerHoursReport])
def get_volunteer_hours_report(
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    volunteer_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Volunteer hours report.
    Shows individual and collective hours with filtering.
    """
    query = db.query(
        Volunteer.id,
        Volunteer.first_name,
        Volunteer.last_name,
        func.coalesce(func.sum(TimeEntry.hours_decimal), 0).label('total_hours'),
        func.coalesce(
            func.sum(func.case((TimeEntry.status == 'approved', TimeEntry.hours_decimal), else_=0)), 
            0
        ).label('approved_hours'),
        func.coalesce(
            func.sum(func.case((TimeEntry.status == 'pending', TimeEntry.hours_decimal), else_=0)), 
            0
        ).label('pending_hours'),
        func.count(func.distinct(TimeEntry.event_id)).label('events_attended')
    ).outerjoin(
        TimeEntry, Volunteer.id == TimeEntry.volunteer_id
    ).filter(
        Volunteer.tenant_id == current_user.tenant_id
    )
    
    if volunteer_id:
        query = query.filter(Volunteer.id == volunteer_id)
    
    if start_date:
        query = query.filter(TimeEntry.check_in_time >= start_date)
    if end_date:
        query = query.filter(TimeEntry.check_in_time <= end_date)
    
    query = query.group_by(Volunteer.id, Volunteer.first_name, Volunteer.last_name)
    
    results = query.all()
    
    return [
        VolunteerHoursReport(
            volunteer_id=r.id,
            volunteer_name=f"{r.first_name} {r.last_name}",
            total_hours=float(r.total_hours or 0),
            approved_hours=float(r.approved_hours or 0),
            pending_hours=float(r.pending_hours or 0),
            events_attended=r.events_attended,
            date_range_start=start_date,
            date_range_end=end_date
        )
        for r in results
    ]


@router.get("/reports/compliance", response_model=List[ComplianceReport])
def get_compliance_report(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Compliance report showing training completion and certification status.
    """
    # Get all volunteers with their training status
    volunteers = db.query(Volunteer).filter(
        Volunteer.tenant_id == current_user.tenant_id,
        Volunteer.application_status == 'approved'
    ).all()
    
    # Get required trainings (would come from configuration)
    required_trainings = ['ICS 100', 'CPR', 'HIPAA Training']
    
    results = []
    for volunteer in volunteers:
        # Get completed trainings
        completed = db.query(VolunteerTraining).join(
            VolunteerTraining.course
        ).filter(
            VolunteerTraining.volunteer_id == volunteer.id,
            VolunteerTraining.status == 'active'
        ).all()
        
        completed_names = [t.course.name for t in completed if t.course]
        missing = [t for t in required_trainings if t not in completed_names]
        
        # Get expired certifications
        expired_certs = db.query(Certification).filter(
            Certification.volunteer_id == volunteer.id,
            Certification.expiration_date < date.today()
        ).all()
        
        compliance_pct = ((len(completed_names) / len(required_trainings)) * 100) if required_trainings else 100
        
        results.append(ComplianceReport(
            volunteer_id=volunteer.id,
            volunteer_name=volunteer.full_name,
            required_trainings=required_trainings,
            completed_trainings=completed_names,
            missing_trainings=missing,
            expired_certifications=[c.certification_type for c in expired_certs],
            compliance_percentage=round(compliance_pct, 2)
        ))
    
    return results


@router.get("/reports/unit-metrics", response_model=UnitMetricsReport)
def get_unit_metrics_report(
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Unit-level metrics report.
    """
    if not start_date:
        start_date = date.today() - timedelta(days=30)
    if not end_date:
        end_date = date.today()
    
    # Total volunteers
    total_volunteers = db.query(func.count(Volunteer.id)).filter(
        Volunteer.tenant_id == current_user.tenant_id
    ).scalar()
    
    # Active volunteers (volunteered in period)
    active_volunteers = db.query(func.count(func.distinct(TimeEntry.volunteer_id))).filter(
        TimeEntry.tenant_id == current_user.tenant_id,
        TimeEntry.check_in_time >= start_date,
        TimeEntry.check_in_time <= end_date
    ).scalar()
    
    # Total events in period
    total_events = db.query(func.count(Event.id)).filter(
        Event.tenant_id == current_user.tenant_id,
        Event.start_date >= start_date,
        Event.start_date <= end_date
    ).scalar()
    
    # Total hours
    total_hours = db.query(func.sum(TimeEntry.hours_decimal)).filter(
        TimeEntry.tenant_id == current_user.tenant_id,
        TimeEntry.status == 'approved',
        TimeEntry.check_in_time >= start_date,
        TimeEntry.check_in_time <= end_date
    ).scalar() or 0
    
    # Average hours per volunteer
    avg_hours = total_hours / total_volunteers if total_volunteers > 0 else 0
    
    # Retention rate (volunteers who volunteered in both periods)
    # Simplified calculation
    retention_rate = (active_volunteers / total_volunteers * 100) if total_volunteers > 0 else 0
    
    return UnitMetricsReport(
        unit_name="Main Unit",  # Would come from tenant/user
        total_volunteers=total_volunteers,
        active_volunteers=active_volunteers,
        total_events=total_events,
        total_hours_served=float(total_hours),
        average_hours_per_volunteer=round(avg_hours, 2),
        retention_rate=round(retention_rate, 2),
        period_start=datetime.combine(start_date, datetime.min.time()),
        period_end=datetime.combine(end_date, datetime.max.time())
    )


# ============ Export Functions ============

def generate_export_file(
    execution_id: int,
    results: Dict[str, Any],
    format: ExportFormat,
    db: Session
):
    """Generate export file in background."""
    try:
        if format == ExportFormat.EXCEL:
            file_content = generate_excel(results)
            file_ext = 'xlsx'
        elif format == ExportFormat.CSV:
            file_content = generate_csv(results)
            file_ext = 'csv'
        elif format == ExportFormat.PDF:
            file_content = generate_pdf(results)
            file_ext = 'pdf'
        else:
            raise ValueError(f"Unsupported format: {format}")
        
        # Upload to S3 (implement S3 upload)
        # file_url = upload_to_s3(file_content, f"reports/{execution_id}.{file_ext}")
        file_url = f"/exports/report_{execution_id}.{file_ext}"  # Placeholder
        
        # Update execution record
        execution = db.query(ReportExecution).filter(
            ReportExecution.id == execution_id
        ).first()
        
        if execution:
            execution.file_url = file_url
            execution.file_size_bytes = len(file_content)
            execution.status = 'completed'
            db.commit()
            
    except Exception as e:
        execution = db.query(ReportExecution).filter(
            ReportExecution.id == execution_id
        ).first()
        if execution:
            execution.status = 'failed'
            execution.error_message = str(e)
            db.commit()


def generate_excel(results: Dict[str, Any]) -> bytes:
    """Generate Excel file from results."""
    df = pd.DataFrame(results['rows'])
    
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, sheet_name='Report', index=False)
    
    return output.getvalue()


def generate_csv(results: Dict[str, Any]) -> bytes:
    """Generate CSV file from results."""
    df = pd.DataFrame(results['rows'])
    return df.to_csv(index=False).encode('utf-8')


def generate_pdf(results: Dict[str, Any]) -> bytes:
    """Generate PDF file from results."""
    # Implement PDF generation using reportlab or similar
    # For now, return placeholder
    return b"PDF generation not yet implemented"


def build_and_execute_query(
    db: Session,
    tenant_id: int,
    query_config: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Build and execute a query based on configuration.
    This is a simplified implementation - production would be more robust.
    """
    entity_type = query_config.get('entity_type')
    fields = query_config.get('fields', [])
    filters = query_config.get('filters', [])
    
    # Map entity types to models
    entity_map = {
        'volunteer': Volunteer,
        'event': Event,
        'time_entry': TimeEntry,
        'training': VolunteerTraining
    }
    
    model = entity_map.get(entity_type)
    if not model:
        raise ValueError(f"Unknown entity type: {entity_type}")
    
    # Build query
    query = db.query(model).filter(model.tenant_id == tenant_id)
    
    # Apply filters (simplified)
    for f in filters:
        field_name = f.get('field')
        operator = f.get('operator')
        value = f.get('value')
        
        if hasattr(model, field_name):
            field = getattr(model, field_name)
            
            if operator == 'eq':
                query = query.filter(field == value)
            elif operator == 'ne':
                query = query.filter(field != value)
            elif operator == 'gt':
                query = query.filter(field > value)
            elif operator == 'lt':
                query = query.filter(field < value)
            # Add more operators as needed
    
    # Execute and format results
    results = query.all()
    
    rows = []
    for result in results:
        row = {}
        for field in fields:
            if hasattr(result, field):
                value = getattr(result, field)
                # Convert datetime to string
                if isinstance(value, datetime):
                    value = value.isoformat()
                row[field] = value
        rows.append(row)
    
    return {
        'columns': fields,
        'rows': rows,
        'total_count': len(rows)
    }


# ============ Workflow Automation ============

@router.post("/workflows", response_model=WorkflowResponse, status_code=status.HTTP_201_CREATED)
def create_workflow(
    workflow_data: WorkflowCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create workflow automation."""
    workflow = ReportWorkflow(
        tenant_id=current_user.tenant_id,
        **workflow_data.dict(),
        created_by=current_user.id
    )
    
    db.add(workflow)
    db.commit()
    db.refresh(workflow)
    
    return workflow


@router.get("/workflows", response_model=List[WorkflowResponse])
def list_workflows(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List workflows."""
    workflows = db.query(ReportWorkflow).filter(
        ReportWorkflow.tenant_id == current_user.tenant_id,
        ReportWorkflow.is_active == True
    ).all()
    
    return workflows


# ============ Report Fields (for Ad Hoc Builder) ============

@router.get("/fields")
def get_available_fields(
    entity_type: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get available fields for report builder."""
    query = db.query(ReportField)
    
    if entity_type:
        query = query.filter(ReportField.entity_type == entity_type)
    
    fields = query.all()
    return fields
