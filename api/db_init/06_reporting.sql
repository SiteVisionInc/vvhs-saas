-- api/db_init/06_reporting.sql
-- Reporting & Analytics Schema
-- Implements section 1.7 from roadmap

-- Saved Reports Library
CREATE TABLE saved_reports (
    id SERIAL PRIMARY KEY,
    tenant_id INTEGER NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    
    -- Report metadata
    name VARCHAR(255) NOT NULL,
    description TEXT,
    report_type VARCHAR(100) NOT NULL, -- volunteer_hours, impact_data, compliance, etc.
    
    -- Report configuration
    query_config JSONB NOT NULL, -- Field selections, filters, groupings
    visualization_config JSONB, -- Chart type, colors, etc.
    
    -- Scheduling
    schedule_config JSONB, -- {frequency: 'daily', time: '08:00', recipients: ['email@example.com']}
    last_generated_at TIMESTAMP,
    next_scheduled_at TIMESTAMP,
    
    -- Sharing
    is_public BOOLEAN DEFAULT FALSE,
    shared_with_roles TEXT, -- JSON array of roles
    shared_with_users TEXT, -- JSON array of user IDs
    
    -- Ownership
    created_by INTEGER REFERENCES users(id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Status
    is_active BOOLEAN DEFAULT TRUE
);

-- Report Executions History
CREATE TABLE report_executions (
    id SERIAL PRIMARY KEY,
    report_id INTEGER REFERENCES saved_reports(id) ON DELETE CASCADE,
    
    -- Execution details
    executed_by INTEGER REFERENCES users(id),
    executed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    execution_time_ms INTEGER,
    row_count INTEGER,
    
    -- Output
    file_url VARCHAR(500), -- S3 URL for generated file
    file_format VARCHAR(20), -- excel, pdf, csv
    file_size_bytes INTEGER,
    
    -- Status
    status VARCHAR(50) DEFAULT 'pending', -- pending, completed, failed
    error_message TEXT
);

-- Report Builder Field Definitions
CREATE TABLE report_fields (
    id SERIAL PRIMARY KEY,
    entity_type VARCHAR(100) NOT NULL, -- volunteer, event, training, time_entry
    field_name VARCHAR(100) NOT NULL,
    field_label VARCHAR(255) NOT NULL,
    field_type VARCHAR(50) NOT NULL, -- string, number, date, boolean
    is_filterable BOOLEAN DEFAULT TRUE,
    is_groupable BOOLEAN DEFAULT TRUE,
    is_aggregatable BOOLEAN DEFAULT FALSE,
    aggregation_functions TEXT, -- JSON array: ['sum', 'avg', 'count']
    UNIQUE(entity_type, field_name)
);

-- Workflow Automation Rules
CREATE TABLE report_workflows (
    id SERIAL PRIMARY KEY,
    tenant_id INTEGER NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    
    -- Workflow details
    name VARCHAR(255) NOT NULL,
    description TEXT,
    
    -- Trigger configuration
    trigger_report_id INTEGER REFERENCES saved_reports(id),
    trigger_conditions JSONB, -- Filter conditions that must be met
    
    -- Actions to perform
    actions JSONB NOT NULL, -- [{type: 'add_to_group', group_id: 123}, {type: 'send_email', template_id: 456}]
    
    -- Status
    is_active BOOLEAN DEFAULT TRUE,
    last_executed_at TIMESTAMP,
    execution_count INTEGER DEFAULT 0,
    
    -- Metadata
    created_by INTEGER REFERENCES users(id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Workflow Execution Log
CREATE TABLE workflow_executions (
    id SERIAL PRIMARY KEY,
    workflow_id INTEGER REFERENCES report_workflows(id) ON DELETE CASCADE,
    
    -- Execution details
    executed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    records_processed INTEGER,
    records_affected INTEGER,
    
    -- Status
    status VARCHAR(50) DEFAULT 'pending',
    error_message TEXT,
    execution_log JSONB -- Detailed log of actions performed
);

-- Indexes for performance
CREATE INDEX idx_saved_reports_tenant ON saved_reports(tenant_id, is_active);
CREATE INDEX idx_saved_reports_type ON saved_reports(report_type);
CREATE INDEX idx_report_executions_report ON report_executions(report_id, executed_at);
CREATE INDEX idx_report_workflows_tenant ON report_workflows(tenant_id, is_active);
CREATE INDEX idx_workflow_executions_workflow ON workflow_executions(workflow_id, executed_at);

-- Permissions
GRANT ALL PRIVILEGES ON saved_reports TO vvhs;
GRANT ALL PRIVILEGES ON report_executions TO vvhs;
GRANT ALL PRIVILEGES ON report_fields TO vvhs;
GRANT ALL PRIVILEGES ON report_workflows TO vvhs;
GRANT ALL PRIVILEGES ON workflow_executions TO vvhs;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO vvhs;

-- Insert report field definitions
INSERT INTO report_fields (entity_type, field_name, field_label, field_type, is_filterable, is_groupable, is_aggregatable, aggregation_functions) VALUES
-- Volunteer fields
('volunteer', 'id', 'Volunteer ID', 'number', TRUE, TRUE, TRUE, '["count"]'),
('volunteer', 'full_name', 'Full Name', 'string', TRUE, TRUE, FALSE, NULL),
('volunteer', 'email', 'Email', 'string', TRUE, FALSE, FALSE, NULL),
('volunteer', 'application_status', 'Application Status', 'string', TRUE, TRUE, TRUE, '["count"]'),
('volunteer', 'account_status', 'Account Status', 'string', TRUE, TRUE, TRUE, '["count"]'),
('volunteer', 'total_hours', 'Total Hours', 'number', TRUE, FALSE, TRUE, '["sum", "avg", "min", "max"]'),
('volunteer', 'created_at', 'Registration Date', 'date', TRUE, TRUE, TRUE, '["count"]'),
('volunteer', 'city', 'City', 'string', TRUE, TRUE, TRUE, '["count"]'),
('volunteer', 'state', 'State', 'string', TRUE, TRUE, TRUE, '["count"]'),

-- Training fields
('training', 'course_name', 'Course Name', 'string', TRUE, TRUE, TRUE, '["count"]'),
('training', 'completion_date', 'Completion Date', 'date', TRUE, TRUE, TRUE, '["count"]'),
('training', 'expiration_date', 'Expiration Date', 'date', TRUE, TRUE, TRUE, '["count"]'),
('training', 'status', 'Training Status', 'string', TRUE, TRUE, TRUE, '["count"]'),

-- Event fields
('event', 'name', 'Event Name', 'string', TRUE, TRUE, TRUE, '["count"]'),
('event', 'activity_type', 'Activity Type', 'string', TRUE, TRUE, TRUE, '["count"]'),
('event', 'start_date', 'Event Date', 'date', TRUE, TRUE, TRUE, '["count"]'),
('event', 'location', 'Location', 'string', TRUE, TRUE, TRUE, '["count"]'),
('event', 'registered_volunteers', 'Registered Volunteers', 'number', TRUE, FALSE, TRUE, '["sum", "avg", "min", "max"]'),

-- Time Entry fields
('time_entry', 'check_in_time', 'Check In Time', 'date', TRUE, TRUE, TRUE, '["count"]'),
('time_entry', 'hours_decimal', 'Hours', 'number', TRUE, FALSE, TRUE, '["sum", "avg", "min", "max"]'),
('time_entry', 'status', 'Approval Status', 'string', TRUE, TRUE, TRUE, '["count"]'),
('time_entry', 'entry_method', 'Entry Method', 'string', TRUE, TRUE, TRUE, '["count"]');

COMMENT ON TABLE saved_reports IS 'User-defined and system reports';
COMMENT ON TABLE report_executions IS 'History of report generations';
COMMENT ON TABLE report_fields IS 'Available fields for report builder';
COMMENT ON TABLE report_workflows IS 'Automated workflows triggered by report results';