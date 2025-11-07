-- VVHS Database Enhanced Schema
-- Comprehensive volunteer management system with all necessary fields

-- Drop all existing tables to start fresh
DROP TABLE IF EXISTS audit_logs CASCADE;
DROP TABLE IF EXISTS event_assignments CASCADE;
DROP TABLE IF EXISTS shifts CASCADE;
DROP TABLE IF EXISTS events CASCADE;
DROP TABLE IF EXISTS training_records CASCADE;
DROP TABLE IF EXISTS volunteers CASCADE;
DROP TABLE IF EXISTS users CASCADE;
DROP TABLE IF EXISTS tenants CASCADE;

-- Create tenants table (organizations/health districts)
CREATE TABLE tenants (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL UNIQUE,
    slug VARCHAR(100) NOT NULL UNIQUE,
    contact_email VARCHAR(255) NOT NULL,
    contact_phone VARCHAR(20),
    address_line1 VARCHAR(255),
    address_line2 VARCHAR(255),
    city VARCHAR(100),
    state VARCHAR(2) DEFAULT 'VA',
    zip_code VARCHAR(10),
    is_active BOOLEAN DEFAULT TRUE NOT NULL,
    settings TEXT,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create users table (staff and administrators)
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    tenant_id INTEGER NOT NULL REFERENCES tenants(id),
    
    -- Authentication
    username VARCHAR(100) NOT NULL UNIQUE,
    email VARCHAR(255) NOT NULL UNIQUE,
    hashed_password VARCHAR(255) NOT NULL,
    
    -- Profile
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    phone VARCHAR(20),
    
    -- Role and permissions
    role VARCHAR(50) NOT NULL DEFAULT 'sub_unit_staff',
    status VARCHAR(20) NOT NULL DEFAULT 'pending',
    
    -- Sub-unit staff permissions
    can_view_data BOOLEAN DEFAULT TRUE,
    can_edit_data BOOLEAN DEFAULT FALSE,
    can_send_password_reminder BOOLEAN DEFAULT FALSE,
    can_initiate_transfers BOOLEAN DEFAULT FALSE,
    can_approve_transfers BOOLEAN DEFAULT FALSE,
    can_view_alerts BOOLEAN DEFAULT TRUE,
    can_edit_alerts BOOLEAN DEFAULT FALSE,
    can_export_data BOOLEAN DEFAULT FALSE,
    
    -- Multi-factor authentication
    mfa_enabled BOOLEAN DEFAULT FALSE,
    mfa_secret VARCHAR(255),
    
    -- Timestamps
    last_login TIMESTAMP,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create enhanced volunteers table with all necessary fields
CREATE TABLE volunteers (
    id SERIAL PRIMARY KEY,
    tenant_id INTEGER NOT NULL REFERENCES tenants(id),
    
    -- Authentication (for volunteer portal)
    username VARCHAR(100) NOT NULL UNIQUE,
    email VARCHAR(255) NOT NULL,
    hashed_password VARCHAR(255),
    
    -- Personal Information
    first_name VARCHAR(100) NOT NULL,
    middle_name VARCHAR(100),
    last_name VARCHAR(100) NOT NULL,
    date_of_birth DATE,
    
    -- Contact Information
    phone_primary VARCHAR(20),
    phone_secondary VARCHAR(20),
    address_line1 VARCHAR(255),
    address_line2 VARCHAR(255),
    city VARCHAR(100),
    state VARCHAR(2) DEFAULT 'VA',
    zip_code VARCHAR(10),
    
    -- Emergency Contact
    emergency_contact_name VARCHAR(255),
    emergency_contact_phone VARCHAR(20),
    emergency_contact_relationship VARCHAR(100),
    
    -- Application Status
    application_status VARCHAR(20) DEFAULT 'pending',
    account_status VARCHAR(20) DEFAULT 'active',
    mrc_level VARCHAR(20),
    
    -- Professional Information
    occupation VARCHAR(100),
    employer VARCHAR(255),
    professional_skills TEXT,  -- Enhanced from just 'skills'
    license_number VARCHAR(100),
    license_type VARCHAR(100),
    license_state VARCHAR(2),
    license_expiration DATE,
    
    -- Skills and Languages
    skills TEXT,  -- General skills
    languages VARCHAR(255),
    
    -- Training and Credentials
    certifications TEXT,
    certification_info TEXT,  -- Additional certification details
    train_id VARCHAR(100),
    train_data TEXT,
    
    -- Availability and Preferences
    availability TEXT,
    availability_info TEXT,  -- Additional availability details
    travel_distance INTEGER DEFAULT 25,
    preferred_roles TEXT,
    assigned_groups TEXT,
    assigned_roles TEXT,
    
    -- Metrics and Performance
    total_hours DECIMAL(10,2) DEFAULT 0,
    alert_response_rate DECIMAL(5,2) DEFAULT 0,
    badges_earned TEXT,
    
    -- Background Check
    background_check_date DATE,
    background_check_status VARCHAR(20),
    
    -- Important Dates
    application_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    approval_date TIMESTAMP,
    last_activity_date TIMESTAMP,
    
    -- System Timestamps
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_activity TIMESTAMP,  -- Keeping for backward compatibility
    approved_at TIMESTAMP,     -- Keeping for backward compatibility
    approved_by INTEGER REFERENCES users(id)
);

-- Create events table
CREATE TABLE events (
    id SERIAL PRIMARY KEY,
    tenant_id INTEGER NOT NULL REFERENCES tenants(id),
    
    -- Basic Information
    name VARCHAR(255) NOT NULL,
    title VARCHAR(255),  -- Adding title for display
    staff_description TEXT,
    volunteer_description TEXT,
    location VARCHAR(255),
    locality VARCHAR(100),
    
    -- Dates and Times
    event_date TIMESTAMP,  -- Primary event date
    start_date TIMESTAMP NOT NULL,
    end_date TIMESTAMP,
    
    -- Event Classification
    activity_type VARCHAR(50) NOT NULL,
    response_name VARCHAR(255),
    mission_types TEXT,
    requestor_type VARCHAR(100),
    
    -- Volunteer Requirements
    max_volunteers INTEGER DEFAULT 100,
    min_volunteers INTEGER DEFAULT 1,
    registered_volunteers INTEGER DEFAULT 0,
    
    -- Visibility and Configuration
    visible_to_volunteers BOOLEAN DEFAULT TRUE,
    allow_self_signup BOOLEAN DEFAULT FALSE,
    enable_waitlist BOOLEAN DEFAULT FALSE,
    districts TEXT,
    
    -- Status
    status VARCHAR(20) NOT NULL DEFAULT 'draft',
    
    -- Impact Tracking
    impact_data TEXT,
    
    -- Timestamps
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by INTEGER REFERENCES users(id)
);

-- Create shifts table
CREATE TABLE shifts (
    id SERIAL PRIMARY KEY,
    event_id INTEGER NOT NULL REFERENCES events(id) ON DELETE CASCADE,
    
    name VARCHAR(255) NOT NULL,
    start_time TIMESTAMP NOT NULL,
    end_time TIMESTAMP NOT NULL,
    max_volunteers INTEGER,
    min_volunteers INTEGER DEFAULT 1,
    
    required_skills TEXT,
    description TEXT,
    location VARCHAR(255),
    
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create enhanced event_assignments table
CREATE TABLE event_assignments (
    id SERIAL PRIMARY KEY,
    event_id INTEGER NOT NULL REFERENCES events(id) ON DELETE CASCADE,
    volunteer_id INTEGER NOT NULL REFERENCES volunteers(id),
    shift_id INTEGER REFERENCES shifts(id),
    
    -- Status and Tracking
    status VARCHAR(20) NOT NULL DEFAULT 'pending',
    hours_completed DECIMAL(5,2),
    hours_served DECIMAL(5,2),  -- Additional field
    
    -- Check-in/Check-out
    check_in_time TIMESTAMP,
    check_out_time TIMESTAMP,
    
    -- Notes
    notes TEXT,
    coordinator_notes TEXT,
    volunteer_notes TEXT,
    
    -- Timestamps
    assigned_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    assigned_by INTEGER REFERENCES users(id),
    confirmed_at TIMESTAMP,
    completed_at TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    UNIQUE(event_id, volunteer_id, shift_id)
);

-- Create training_records table
CREATE TABLE training_records (
    id SERIAL PRIMARY KEY,
    volunteer_id INTEGER NOT NULL REFERENCES volunteers(id),
    course_name VARCHAR(255) NOT NULL,
    course_type VARCHAR(100),
    provider VARCHAR(255),
    completion_date DATE NOT NULL,
    expiration_date DATE,
    certificate_number VARCHAR(100),
    credits_earned DECIMAL(5,2),
    notes TEXT,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create audit_logs table
CREATE TABLE audit_logs (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id),
    tenant_id INTEGER NOT NULL,
    action VARCHAR(100) NOT NULL,
    resource_type VARCHAR(50) NOT NULL,
    resource_id INTEGER,
    ip_address VARCHAR(45),
    user_agent VARCHAR(255),
    endpoint VARCHAR(255),
    http_method VARCHAR(10),
    old_values JSON,
    new_values JSON,
    description TEXT,
    status VARCHAR(20),
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for better performance
CREATE INDEX idx_users_tenant_id ON users(tenant_id);
CREATE INDEX idx_users_username ON users(username);
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_volunteers_tenant_id ON volunteers(tenant_id);
CREATE INDEX idx_volunteers_email ON volunteers(email);
CREATE INDEX idx_volunteers_application_status ON volunteers(application_status);
CREATE INDEX idx_events_tenant_id ON events(tenant_id);
CREATE INDEX idx_events_start_date ON events(start_date);
CREATE INDEX idx_event_assignments_volunteer_id ON event_assignments(volunteer_id);
CREATE INDEX idx_event_assignments_event_id ON event_assignments(event_id);
CREATE INDEX idx_training_records_volunteer_id ON training_records(volunteer_id);
CREATE INDEX idx_audit_logs_user_id ON audit_logs(user_id);
CREATE INDEX idx_audit_logs_tenant_id ON audit_logs(tenant_id);
CREATE INDEX idx_audit_logs_created_at ON audit_logs(created_at);

-- =====================================
-- INSERT ENHANCED DUMMY DATA
-- =====================================

-- Insert tenants (health districts/organizations)
INSERT INTO tenants (id, name, slug, contact_email, contact_phone, address_line1, city, state, zip_code, is_active) VALUES
(1, 'Virginia Department of Health', 'vdh', 'admin@vdh.virginia.gov', '804-864-7001', '109 Governor Street', 'Richmond', 'VA', '23219', true),
(2, 'Richmond MRC', 'richmond-mrc', 'coordinator@richmond-mrc.org', '804-205-3501', '400 E Cary St', 'Richmond', 'VA', '23219', true),
(3, 'Fairfax County MRC', 'fairfax-mrc', 'info@fairfax-mrc.org', '703-246-2411', '10777 Main St', 'Fairfax', 'VA', '22030', true),
(4, 'Norfolk Health District', 'norfolk-hd', 'contact@norfolk-hd.org', '757-683-2745', '830 Southampton Ave', 'Norfolk', 'VA', '23510', true);

-- Insert users (password for all: 't3st45#!$6!')
INSERT INTO users (
    tenant_id, username, email, hashed_password,
    first_name, last_name, phone, role, status,
    can_view_data, can_edit_data, can_export_data, can_send_password_reminder
) VALUES
-- System Admins
(1, 'admin@vdh.virginia.gov', 'admin@vdh.virginia.gov', 
 '$2b$12$EImfq5A648cjQzk5djSQxeYO5a/Tic/KWOyVnJdXKkpuCBK/kTGFq',
 'Sarah', 'Johnson', '804-864-7001', 'system_admin', 'active',
 true, true, true, true),

-- Organization Admins
(2, 'coordinator@richmond-mrc.org', 'coordinator@richmond-mrc.org',
 '$2b$12$EImfq5A648cjQzk5djSQxeYO5a/Tic/KWOyVnJdXKkpuCBK/kTGFq',
 'Emily', 'Rodriguez', '804-205-3502', 'org_admin', 'active',
 true, true, true, false);

-- Insert comprehensive volunteer data
INSERT INTO volunteers (
    tenant_id, username, email, hashed_password,
    first_name, middle_name, last_name, date_of_birth,
    phone_primary, phone_secondary, address_line1, city, state, zip_code,
    emergency_contact_name, emergency_contact_phone, emergency_contact_relationship,
    application_status, account_status, mrc_level,
    occupation, employer, professional_skills, skills, languages,
    license_number, license_type, license_state, license_expiration,
    certifications, train_id, availability, travel_distance,
    total_hours, alert_response_rate, badges_earned,
    background_check_date, background_check_status,
    application_date, approval_date, last_activity_date
) VALUES
-- VDH Volunteers (tenant_id = 1)
(1, 'alice.anderson@vdh.gov', 'alice.anderson@vdh.gov',
 '$2b$12$EImfq5A648cjQzk5djSQxeYO5a/Tic/KWOyVnJdXKkpuCBK/kTGFq',
 'Alice', 'Marie', 'Anderson', '1985-03-15',
 '804-555-0001', '804-555-0002', '123 Main St', 'Richmond', 'VA', '23220',
 'Bob Anderson', '804-555-0003', 'Spouse',
 'approved', 'active', 'level_2',
 'Registered Nurse', 'VCU Health', 'Emergency Medicine, Critical Care, Pediatrics',
 'Medical Care, CPR, First Aid, Triage, IV Therapy', 'English, Spanish',
 'RN123456', 'RN', 'VA', '2026-12-31',
 'RN License, CPR, BLS, ACLS, PALS', 'TRAIN100001', 'Weekends, Evenings, On-call', 50,
 245.5, 92.5, 'Leadership, 100 Hours, First Responder',
 '2024-01-15', 'cleared',
 '2024-01-01 09:00:00', '2024-01-20 14:30:00', '2025-11-06 10:00:00'),

(1, 'bob.brown@vdh.gov', 'bob.brown@vdh.gov',
 '$2b$12$EImfq5A648cjQzk5djSQxeYO5a/Tic/KWOyVnJdXKkpuCBK/kTGFq',
 'Bob', NULL, 'Brown', '1990-07-22',
 '804-555-0004', NULL, '456 Oak Ave', 'Norfolk', 'VA', '23510',
 'Jane Brown', '804-555-0005', 'Wife',
 'pending', 'active', NULL,
 'EMT', 'Norfolk Fire Department', 'Emergency Response, Firefighting',
 'Emergency Medical Services, Hazmat Response', 'English',
 'EMT789012', 'EMT-B', 'VA', '2025-06-30',
 'EMT-B, CPR, Hazmat Operations', 'TRAIN100002', 'Flexible', 75,
 0, 0, NULL,
 '2024-11-01', 'pending',
 '2024-11-01 10:00:00', NULL, NULL),

(1, 'carol.clark@vdh.gov', 'carol.clark@vdh.gov',
 '$2b$12$EImfq5A648cjQzk5djSQxeYO5a/Tic/KWOyVnJdXKkpuCBK/kTGFq',
 'Carol', 'Anne', 'Clark', '1988-11-08',
 '703-555-0006', '703-555-0007', '789 Pine Rd', 'Fairfax', 'VA', '22030',
 'David Clark', '703-555-0008', 'Brother',
 'approved', 'active', 'level_3',
 'Physician', 'Inova Health', 'Internal Medicine, Infectious Disease',
 'Medical Care, Vaccination, Disease Surveillance', 'English, French, Arabic',
 'MD456789', 'MD', 'VA', '2027-12-31',
 'MD License, Board Certified IM, CPR, ACLS', 'TRAIN100003', 'Weekdays after 5pm, Weekends', 30,
 189.0, 88.0, 'Medical Expert, COVID Response Hero',
 '2024-02-10', 'cleared',
 '2024-02-01 11:00:00', '2024-02-15 09:00:00', '2025-11-05 15:30:00'),

-- Richmond MRC Volunteers (tenant_id = 2)
(2, 'jane.doe@email.com', 'jane.doe@email.com',
 '$2b$12$EImfq5A648cjQzk5djSQxeYO5a/Tic/KWOyVnJdXKkpuCBK/kTGFq',
 'Jane', 'Marie', 'Doe', '1985-03-15',
 '804-555-1111', '804-555-1112', '123 Main St', 'Richmond', 'VA', '23220',
 'John Doe', '804-555-1110', 'Spouse',
 'approved', 'active', 'level_2',
 'Registered Nurse', 'VCU Health', 'Critical Care, Emergency Medicine',
 'Medical Care, CPR, First Aid, Triage', 'English, Spanish',
 'RN654321', 'RN', 'VA', '2025-12-31',
 'RN License, CPR, BLS', 'TRAIN123456', 'Weekends, Evenings', 25,
 156.5, 95.0, 'Dedicated Volunteer, Team Leader',
 '2024-06-01', 'cleared',
 '2024-05-15 08:00:00', '2024-06-05 10:00:00', '2025-11-04 12:00:00'),

(2, 'john.smith@email.com', 'john.smith@email.com',
 '$2b$12$EImfq5A648cjQzk5djSQxeYO5a/Tic/KWOyVnJdXKkpuCBK/kTGFq',
 'John', 'Robert', 'Smith', '1978-07-22',
 '804-555-2222', NULL, '456 Oak Ave', 'Richmond', 'VA', '23221',
 'Sarah Smith', '804-555-2223', 'Wife',
 'approved', 'active', 'level_3',
 'Paramedic', 'Richmond Ambulance Authority', 'Advanced Life Support, Trauma Care',
 'Emergency Medical Services, Leadership, Logistics', 'English',
 'PM987654', 'Paramedic', 'VA', '2026-06-30',
 'Paramedic, ACLS, PALS', 'TRAIN789012', 'Flexible', 50,
 312.0, 91.5, 'Excellence Award, 300 Hour Club',
 '2024-05-15', 'cleared',
 '2024-05-01 09:30:00', '2024-05-20 14:00:00', '2025-11-06 08:00:00');

-- Insert training records
INSERT INTO training_records (
    volunteer_id, course_name, course_type, provider,
    completion_date, expiration_date, certificate_number, credits_earned
) VALUES
(1, 'Advanced Cardiac Life Support', 'Certification', 'American Heart Association', 
 '2024-03-15', '2026-03-15', 'ACLS-2024-001', 8.0),
(1, 'Pediatric Advanced Life Support', 'Certification', 'American Heart Association',
 '2024-04-20', '2026-04-20', 'PALS-2024-001', 8.0),
(3, 'Incident Command System 100', 'Training', 'FEMA',
 '2024-05-10', NULL, 'ICS100-2024-003', 4.0),
(4, 'Basic Life Support Provider', 'Certification', 'American Red Cross',
 '2024-06-01', '2026-06-01', 'BLS-2024-004', 4.0);

-- Insert events with enhanced data
INSERT INTO events (
    tenant_id, name, title, staff_description, volunteer_description,
    location, locality, event_date, start_date, end_date,
    activity_type, response_name, mission_types,
    max_volunteers, registered_volunteers,
    visible_to_volunteers, allow_self_signup, status, created_by
) VALUES
(1, 'COVID-19 Vaccination Clinic - Richmond', 'Mass Vaccination Event',
 'Large-scale vaccination event requiring medical and support volunteers',
 'Help provide COVID-19 vaccinations to the community. Various roles available.',
 'Richmond Convention Center', 'Richmond',
 '2025-11-20 08:00:00', '2025-11-20 08:00:00', '2025-11-20 17:00:00',
 'vaccination', 'COVID-19 Response', '["Medical Care", "Logistics", "Public Health"]',
 50, 12, true, true, 'published', 1),

(1, 'Emergency Preparedness Training', 'Quarterly MRC Training',
 'Essential training for all MRC volunteers',
 'Learn emergency response protocols and procedures.',
 'VDH Training Center', 'Richmond',
 '2025-12-05 09:00:00', '2025-12-05 09:00:00', '2025-12-05 16:00:00',
 'training', 'Training Event', '["Training", "Emergency Response"]',
 30, 8, true, false, 'published', 1);

-- Insert event assignments with more detailed data
INSERT INTO event_assignments (
    event_id, volunteer_id, shift_id, status,
    hours_completed, hours_served,
    coordinator_notes, assigned_by, assigned_at
) VALUES
(1, 1, NULL, 'confirmed', 8.0, 8.0, 'Team leader for vaccination station', 1, '2025-11-01 10:00:00'),
(1, 3, NULL, 'confirmed', 8.0, 8.0, 'Medical screening and vaccination', 1, '2025-11-01 10:30:00'),
(2, 1, NULL, 'pending', NULL, NULL, 'Requested instructor role', 1, '2025-11-15 14:00:00');

-- Reset sequences
SELECT setval('tenants_id_seq', (SELECT MAX(id) FROM tenants));
SELECT setval('users_id_seq', (SELECT MAX(id) FROM users));
SELECT setval('volunteers_id_seq', (SELECT MAX(id) FROM volunteers));
SELECT setval('events_id_seq', (SELECT MAX(id) FROM events));
SELECT setval('event_assignments_id_seq', (SELECT MAX(id) FROM event_assignments));
SELECT setval('training_records_id_seq', (SELECT MAX(id) FROM training_records));
SELECT setval('audit_logs_id_seq', (SELECT MAX(id) FROM audit_logs));

-- Grant permissions
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO vvhs;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO vvhs;

-- Display summary
DO $$
BEGIN
    RAISE NOTICE '';
    RAISE NOTICE '=== VVHS Enhanced Database Initialized Successfully ===';
    RAISE NOTICE '';
    RAISE NOTICE 'Created:';
    RAISE NOTICE '  - 4 Tenants';
    RAISE NOTICE '  - 2 Staff Users';
    RAISE NOTICE '  - 5 Volunteers with comprehensive profiles';
    RAISE NOTICE '  - 2 Events';
    RAISE NOTICE '  - 4 Training Records';
    RAISE NOTICE '  - 3 Event Assignments';
    RAISE NOTICE '';
    RAISE NOTICE 'Login Credentials (password: t3st45#!$6!):';
    RAISE NOTICE '  System Admin: admin@vdh.virginia.gov';
    RAISE NOTICE '  Org Admin: coordinator@richmond-mrc.org';
    RAISE NOTICE '';
    RAISE NOTICE '========================================================';
END $$;