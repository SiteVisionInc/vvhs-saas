-- VVHS Database Complete Initialization Script
-- This script drops and recreates all tables with proper schema and dummy data

-- Drop all existing tables to start fresh
DROP TABLE IF EXISTS audit_logs CASCADE;
DROP TABLE IF EXISTS event_assignments CASCADE;
DROP TABLE IF EXISTS shifts CASCADE;
DROP TABLE IF EXISTS events CASCADE;
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

-- Create volunteers table (separate from users)
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
    
    -- Profile Details
    occupation VARCHAR(100),
    employer VARCHAR(255),
    skills TEXT,
    languages VARCHAR(255),
    
    -- Training and Credentials
    certifications TEXT,
    train_id VARCHAR(100),
    train_data TEXT,
    
    -- Availability
    availability TEXT,
    travel_distance INTEGER DEFAULT 25,
    
    -- Background Check
    background_check_date DATE,
    background_check_status VARCHAR(20),
    
    -- Timestamps
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_activity TIMESTAMP,
    approved_at TIMESTAMP,
    approved_by INTEGER REFERENCES users(id)
);

-- Create events table
CREATE TABLE events (
    id SERIAL PRIMARY KEY,
    tenant_id INTEGER NOT NULL REFERENCES tenants(id),
    
    -- Basic Information
    name VARCHAR(255) NOT NULL,
    staff_description TEXT,
    volunteer_description TEXT,
    location VARCHAR(255),
    locality VARCHAR(100),
    
    -- Dates
    start_date TIMESTAMP NOT NULL,
    end_date TIMESTAMP,
    
    -- Event Classification
    activity_type VARCHAR(50) NOT NULL,
    response_name VARCHAR(255),
    mission_types TEXT,
    requestor_type VARCHAR(100),
    
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

-- Create event_assignments table
CREATE TABLE event_assignments (
    id SERIAL PRIMARY KEY,
    event_id INTEGER NOT NULL REFERENCES events(id) ON DELETE CASCADE,
    volunteer_id INTEGER NOT NULL REFERENCES volunteers(id),
    shift_id INTEGER REFERENCES shifts(id),
    
    status VARCHAR(20) NOT NULL DEFAULT 'pending',
    notes TEXT,
    hours_completed DECIMAL(5,2),
    
    assigned_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    assigned_by INTEGER REFERENCES users(id),
    confirmed_at TIMESTAMP,
    completed_at TIMESTAMP,
    
    UNIQUE(event_id, volunteer_id, shift_id)
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
CREATE INDEX idx_events_tenant_id ON events(tenant_id);
CREATE INDEX idx_events_start_date ON events(start_date);
CREATE INDEX idx_audit_logs_user_id ON audit_logs(user_id);
CREATE INDEX idx_audit_logs_tenant_id ON audit_logs(tenant_id);
CREATE INDEX idx_audit_logs_created_at ON audit_logs(created_at);

-- =====================================
-- INSERT DUMMY DATA
-- =====================================

-- Insert tenants (health districts/organizations)
INSERT INTO tenants (id, name, slug, contact_email, contact_phone, address_line1, city, state, zip_code, is_active) VALUES
(1, 'Virginia Department of Health', 'vdh', 'admin@vdh.virginia.gov', '804-864-7001', '109 Governor Street', 'Richmond', 'VA', '23219', true),
(2, 'Richmond MRC', 'richmond-mrc', 'coordinator@richmond-mrc.org', '804-205-3501', '400 E Cary St', 'Richmond', 'VA', '23219', true),
(3, 'Fairfax County MRC', 'fairfax-mrc', 'info@fairfax-mrc.org', '703-246-2411', '10777 Main St', 'Fairfax', 'VA', '22030', true),
(4, 'Norfolk Health District', 'norfolk-hd', 'contact@norfolk-hd.org', '757-683-2745', '830 Southampton Ave', 'Norfolk', 'VA', '23510', true);

-- Insert users (staff and administrators)
-- Password for all users: 'admin123' (bcrypt hash)
INSERT INTO users (
    tenant_id, username, email, hashed_password,
    first_name, last_name, phone, role, status,
    can_view_data, can_edit_data, can_export_data, can_send_password_reminder
) VALUES
-- System Admins (state-level)
(1, 'admin@vdh.virginia.gov', 'admin@vdh.virginia.gov', 
 '$2b$12$EImfq5A648cjQzk5djSQxeYO5a/Tic/KWOyVnJdXKkpuCBK/kTGFq',
 'Sarah', 'Johnson', '804-864-7001', 'system_admin', 'active',
 true, true, true, true),

(1, 'tech.admin@vdh.virginia.gov', 'tech.admin@vdh.virginia.gov',
 '$2b$12$EImfq5A648cjQzk5djSQxeYO5a/Tic/KWOyVnJdXKkpuCBK/kTGFq',
 'Michael', 'Chen', '804-864-7002', 'system_admin', 'active',
 true, true, true, true),

-- Organization Admins (Unit Coordinators)
(2, 'coordinator@richmond-mrc.org', 'coordinator@richmond-mrc.org',
 '$2b$12$EImfq5A648cjQzk5djSQxeYO5a/Tic/KWOyVnJdXKkpuCBK/kTGFq',
 'Emily', 'Rodriguez', '804-205-3502', 'org_admin', 'active',
 true, true, true, false),

(3, 'admin@fairfax-mrc.org', 'admin@fairfax-mrc.org',
 '$2b$12$EImfq5A648cjQzk5djSQxeYO5a/Tic/KWOyVnJdXKkpuCBK/kTGFq',
 'David', 'Thompson', '703-246-2412', 'org_admin', 'active',
 true, true, true, false),

-- Coordinators
(2, 'events@richmond-mrc.org', 'events@richmond-mrc.org',
 '$2b$12$EImfq5A648cjQzk5djSQxeYO5a/Tic/KWOyVnJdXKkpuCBK/kTGFq',
 'Jessica', 'Lee', '804-205-3503', 'coordinator', 'active',
 true, true, false, true),

(3, 'training@fairfax-mrc.org', 'training@fairfax-mrc.org',
 '$2b$12$EImfq5A648cjQzk5djSQxeYO5a/Tic/KWOyVnJdXKkpuCBK/kTGFq',
 'Robert', 'Wilson', '703-246-2413', 'coordinator', 'active',
 true, true, false, false),

-- Sub-unit Staff
(2, 'staff1@richmond-mrc.org', 'staff1@richmond-mrc.org',
 '$2b$12$EImfq5A648cjQzk5djSQxeYO5a/Tic/KWOyVnJdXKkpuCBK/kTGFq',
 'Amanda', 'Brown', '804-205-3504', 'sub_unit_staff', 'active',
 true, false, false, false),

(3, 'staff2@fairfax-mrc.org', 'staff2@fairfax-mrc.org',
 '$2b$12$EImfq5A648cjQzk5djSQxeYO5a/Tic/KWOyVnJdXKkpuCBK/kTGFq',
 'James', 'Davis', '703-246-2414', 'sub_unit_staff', 'active',
 true, false, false, false);

-- Insert volunteers
INSERT INTO volunteers (
    tenant_id, username, email, hashed_password,
    first_name, middle_name, last_name, date_of_birth,
    phone_primary, phone_secondary, address_line1, city, state, zip_code,
    emergency_contact_name, emergency_contact_phone, emergency_contact_relationship,
    application_status, account_status, mrc_level,
    occupation, employer, skills, languages,
    certifications, train_id, availability, travel_distance,
    background_check_date, background_check_status
) VALUES
-- Richmond MRC Volunteers
(2, 'jane.doe@email.com', 'jane.doe@email.com',
 '$2b$12$EImfq5A648cjQzk5djSQxeYO5a/Tic/KWOyVnJdXKkpuCBK/kTGFq',
 'Jane', 'Marie', 'Doe', '1985-03-15',
 '804-555-1111', '804-555-1112', '123 Main St', 'Richmond', 'VA', '23220',
 'John Doe', '804-555-1110', 'Spouse',
 'approved', 'active', 'level_2',
 'Registered Nurse', 'VCU Health', 'Medical Care, CPR, First Aid, Triage', 'English, Spanish',
 'RN License, CPR, BLS', 'TRAIN123456', 'Weekends, Evenings', 25,
 '2024-06-01', 'cleared'),

(2, 'john.smith@email.com', 'john.smith@email.com',
 '$2b$12$EImfq5A648cjQzk5djSQxeYO5a/Tic/KWOyVnJdXKkpuCBK/kTGFq',
 'John', 'Robert', 'Smith', '1978-07-22',
 '804-555-2222', NULL, '456 Oak Ave', 'Richmond', 'VA', '23221',
 'Sarah Smith', '804-555-2223', 'Wife',
 'approved', 'active', 'level_3',
 'Paramedic', 'Richmond Ambulance Authority', 'Emergency Medical Services, Leadership, Logistics', 'English',
 'Paramedic, ACLS, PALS', 'TRAIN789012', 'Flexible', 50,
 '2024-05-15', 'cleared'),

-- Fairfax MRC Volunteers
(3, 'maria.garcia@email.com', 'maria.garcia@email.com',
 '$2b$12$EImfq5A648cjQzk5djSQxeYO5a/Tic/KWOyVnJdXKkpuCBK/kTGFq',
 'Maria', 'Elena', 'Garcia', '1990-11-08',
 '703-555-3333', '703-555-3334', '789 Pine Rd', 'Fairfax', 'VA', '22030',
 'Carlos Garcia', '703-555-3335', 'Brother',
 'approved', 'active', 'level_1',
 'Public Health Specialist', 'Fairfax County Health Dept', 'Public Health, Education, Translation', 'English, Spanish, Portuguese',
 'MPH, CPR', 'TRAIN345678', 'Weekdays after 5pm', 20,
 '2024-07-10', 'cleared'),

(3, 'robert.jones@email.com', 'robert.jones@email.com',
 '$2b$12$EImfq5A648cjQzk5djSQxeYO5a/Tic/KWOyVnJdXKkpuCBK/kTGFq',
 'Robert', 'Alan', 'Jones', '1982-04-30',
 '703-555-4444', NULL, '321 Elm St', 'Falls Church', 'VA', '22046',
 'Linda Jones', '703-555-4445', 'Mother',
 'pending', 'active', NULL,
 'IT Specialist', 'Tech Solutions Inc', 'IT Support, Communications, Data Management', 'English',
 'CompTIA A+, Network+', 'TRAIN901234', 'Weekends', 30,
 '2024-08-20', 'pending'),

-- Norfolk Volunteers
(4, 'susan.williams@email.com', 'susan.williams@email.com',
 '$2b$12$EImfq5A648cjQzk5djSQxeYO5a/Tic/KWOyVnJdXKkpuCBK/kTGFq',
 'Susan', 'Beth', 'Williams', '1975-09-12',
 '757-555-5555', '757-555-5556', '654 Beach Blvd', 'Norfolk', 'VA', '23510',
 'Tom Williams', '757-555-5557', 'Husband',
 'approved', 'active', 'level_2',
 'Physician Assistant', 'Sentara Healthcare', 'Medical Care, Vaccination, Patient Assessment', 'English, French',
 'PA-C, BLS, ACLS', 'TRAIN567890', 'Flexible', 40,
 '2024-06-30', 'cleared');
 
 
 
 INSERT INTO volunteers (
    tenant_id, username, email, hashed_password,
    first_name, last_name,
    phone_primary, application_status, account_status,
    city, state, created_at
) VALUES 
(1, 'test.volunteer1@vdh.gov', 'test.volunteer1@vdh.gov', 
 '\$2b\$12\$EImfq5A648cjQzk5djSQxeYO5a/Tic/KWOyVnJdXKkpuCBK/kTGFq',
 'Alice', 'Anderson', '555-0001', 'approved', 'active',
 'Richmond', 'VA', NOW()),
(1, 'test.volunteer2@vdh.gov', 'test.volunteer2@vdh.gov',
 '\$2b\$12\$EImfq5A648cjQzk5djSQxeYO5a/Tic/KWOyVnJdXKkpuCBK/kTGFq',
 'Bob', 'Brown', '555-0002', 'pending', 'active', 
 'Norfolk', 'VA', NOW()),
(1, 'test.volunteer3@vdh.gov', 'test.volunteer3@vdh.gov',
 '\$2b\$12\$EImfq5A648cjQzk5djSQxeYO5a/Tic/KWOyVnJdXKkpuCBK/kTGFq',
 'Carol', 'Clark', '555-0003', 'approved', 'active',
 'Fairfax', 'VA', NOW());

-- Insert events
INSERT INTO events (
    tenant_id, name, staff_description, volunteer_description,
    location, locality, start_date, end_date,
    activity_type, response_name, mission_types,
    visible_to_volunteers, allow_self_signup, status, created_by
) VALUES
-- Richmond MRC Events
(2, 'COVID-19 Vaccination Clinic', 
 'Large-scale vaccination event requiring 25 volunteers',
 'Help provide COVID-19 vaccinations to the community. Various roles available including registration, traffic control, and post-vaccination monitoring.',
 'Richmond Convention Center, 403 N 3rd St, Richmond, VA 23219', 'Richmond',
 '2025-11-20 08:00:00', '2025-11-20 17:00:00',
 'vaccination', 'COVID-19 Response', '["Medical Care", "Logistics", "Public Health"]',
 true, true, 'published', 3),

(2, 'Emergency Preparedness Training',
 'Quarterly training for MRC volunteers on emergency response protocols',
 'Join us for essential emergency preparedness training. Topics include triage, mass casualty response, and incident command structure.',
 'Richmond Fire Training Center, 3301 E Richmond Rd', 'Richmond',
 '2025-12-05 09:00:00', '2025-12-05 16:00:00',
 'training', 'Training Event', '["Training", "Emergency Response"]',
 true, false, 'published', 3),

-- Fairfax MRC Events
(3, 'Community Health Fair',
 'Annual health fair providing free screenings and health education',
 'Volunteer at our annual health fair! Help with blood pressure screenings, diabetes testing, and health education booths.',
 'Fairfax County Government Center, 12000 Government Center Pkwy', 'Fairfax',
 '2025-11-15 10:00:00', '2025-11-15 16:00:00',
 'health_screening', 'Community Outreach', '["Public Health", "Education", "Screening"]',
 true, true, 'published', 4),

(3, 'Winter Storm Response Planning',
 'Preparation session for winter storm response protocols',
 'Prepare for winter emergency response. Review shelter operations, emergency communications, and resource distribution.',
 'Fairfax Fire Station 40, 4621 Legato Rd', 'Fairfax',
 '2025-11-25 18:00:00', '2025-11-25 21:00:00',
 'planning', 'Emergency Preparedness', '["Planning", "Emergency Response"]',
 true, false, 'draft', 4),

-- Norfolk Events
(4, 'Hurricane Season Preparedness Drill',
 'Full-scale hurricane response exercise',
 'Participate in our hurricane response drill. Practice evacuation procedures, shelter setup, and emergency medical response.',
 'Norfolk Emergency Operations Center, 2501 City Hall Ave', 'Norfolk',
 '2025-12-10 07:00:00', '2025-12-10 15:00:00',
 'exercise', 'Hurricane Preparedness', '["Emergency Response", "Shelter Operations", "Medical Care"]',
 true, false, 'published', 1);

-- Insert shifts for events
INSERT INTO shifts (
    event_id, name, start_time, end_time,
    max_volunteers, min_volunteers, required_skills, description
) VALUES
-- Vaccination Clinic Shifts (Event 1)
(1, 'Morning Registration', '2025-11-20 08:00:00', '2025-11-20 12:00:00',
 5, 2, 'Customer Service', 'Check-in patients and verify appointments'),
(1, 'Afternoon Registration', '2025-11-20 12:00:00', '2025-11-20 17:00:00',
 5, 2, 'Customer Service', 'Check-in patients and verify appointments'),
(1, 'Medical Support - Morning', '2025-11-20 08:00:00', '2025-11-20 12:00:00',
 10, 5, 'Medical License', 'Administer vaccines and monitor patients'),
(1, 'Medical Support - Afternoon', '2025-11-20 12:00:00', '2025-11-20 17:00:00',
 10, 5, 'Medical License', 'Administer vaccines and monitor patients'),

-- Health Fair Shifts (Event 3)
(3, 'Setup Crew', '2025-11-15 08:00:00', '2025-11-15 10:00:00',
 8, 4, 'Physical Labor', 'Set up tables, tents, and equipment'),
(3, 'Health Screening Station', '2025-11-15 10:00:00', '2025-11-15 14:00:00',
 6, 3, 'Medical Training', 'Conduct blood pressure and glucose screenings'),
(3, 'Breakdown Crew', '2025-11-15 14:00:00', '2025-11-15 16:00:00',
 8, 4, 'Physical Labor', 'Pack up equipment and clean area');

-- Insert event assignments
INSERT INTO event_assignments (
    event_id, volunteer_id, shift_id, status, assigned_by, assigned_at
) VALUES
-- Assign volunteers to vaccination clinic
(1, 1, 3, 'confirmed', 3, '2025-11-01 10:00:00'),  -- Jane to medical morning
(1, 2, 4, 'confirmed', 3, '2025-11-01 10:30:00'),  -- John to medical afternoon

-- Assign volunteers to health fair
(3, 3, 6, 'confirmed', 4, '2025-11-02 14:00:00'),  -- Maria to screening station
(3, 4, 5, 'pending', 4, '2025-11-02 14:30:00');    -- Robert to setup (pending)

-- Insert sample audit logs
INSERT INTO audit_logs (
    user_id, tenant_id, action, resource_type, resource_id,
    description, status
) VALUES
(1, 1, 'user.login', 'user', 1, 'System admin logged in', 'success'),
(3, 2, 'volunteer.approved', 'volunteer', 1, 'Approved volunteer Jane Doe', 'success'),
(4, 3, 'event.created', 'event', 3, 'Created Community Health Fair event', 'success'),
(3, 2, 'event.published', 'event', 1, 'Published COVID-19 Vaccination Clinic', 'success');

-- Reset sequences to ensure IDs continue correctly
SELECT setval('tenants_id_seq', (SELECT MAX(id) FROM tenants));
SELECT setval('users_id_seq', (SELECT MAX(id) FROM users));
SELECT setval('volunteers_id_seq', (SELECT MAX(id) FROM volunteers));
SELECT setval('events_id_seq', (SELECT MAX(id) FROM events));
SELECT setval('shifts_id_seq', (SELECT MAX(id) FROM shifts));
SELECT setval('event_assignments_id_seq', (SELECT MAX(id) FROM event_assignments));
SELECT setval('audit_logs_id_seq', (SELECT MAX(id) FROM audit_logs));

-- Grant permissions (optional, for security)
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO vvhs;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO vvhs;

UPDATE users SET 
  role = LOWER(role),
  status = LOWER(status)
WHERE role != LOWER(role) OR status != LOWER(status);

INSERT INTO users (
    tenant_id, username, email, hashed_password,
    first_name, last_name,
    role, status,
    can_view_data
) VALUES (
    15, 
    'test@example.com',
    'test@example.com',
    '$2b$12$EImfq5A648cjQzk5djSQxeYO5a/Tic/KWOyVnJdXKkpuCBK/kTGFq',
    'Test',
    'User',
    'sub_unit_staff',
    'active',
    true
);


-- Display summary of created data
DO $$
BEGIN
    RAISE NOTICE '';
    RAISE NOTICE '=== VVHS Database Initialized Successfully ===';
    RAISE NOTICE '';
    RAISE NOTICE 'Created:';
    RAISE NOTICE '  - 4 Tenants (Organizations)';
    RAISE NOTICE '  - 8 Users (Staff/Admins)';
    RAISE NOTICE '  - 5 Volunteers';
    RAISE NOTICE '  - 5 Events';
    RAISE NOTICE '  - 7 Shifts';
    RAISE NOTICE '  - 4 Event Assignments';
    RAISE NOTICE '';
    RAISE NOTICE 'Login Credentials (all passwords: admin123):';
    RAISE NOTICE '  System Admin: admin@vdh.virginia.gov';
    RAISE NOTICE '  Org Admin: coordinator@richmond-mrc.org';
    RAISE NOTICE '  Coordinator: events@richmond-mrc.org';
    RAISE NOTICE '  Volunteer: jane.doe@email.com';
    RAISE NOTICE '';
    RAISE NOTICE '==============================================';
END $$;