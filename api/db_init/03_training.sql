-- api/db_init/03_training.sql (ENHANCED - Training Management)
-- Training Management Schema
-- Implements section 1.4 from roadmap

-- Training Courses (including TRAIN courses)
CREATE TABLE training_courses (
    id SERIAL PRIMARY KEY,
    tenant_id INTEGER NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    
    -- TRAIN Integration
    train_course_id VARCHAR(100) UNIQUE,
    
    -- Course Information
    name VARCHAR(255) NOT NULL,
    description TEXT,
    course_code VARCHAR(50),
    provider VARCHAR(255),
    category VARCHAR(100),
    
    -- Requirements
    is_required BOOLEAN DEFAULT FALSE,
    validity_period_days INTEGER,
    
    -- Metadata
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Volunteer Training Records
CREATE TABLE volunteer_training (
    id SERIAL PRIMARY KEY,
    volunteer_id INTEGER NOT NULL REFERENCES volunteers(id) ON DELETE CASCADE,
    course_id INTEGER NOT NULL REFERENCES training_courses(id),
    
    -- Completion Details
    completion_date DATE NOT NULL,
    expiration_date DATE,
    score DECIMAL(5,2),
    certificate_number VARCHAR(100),
    certificate_url VARCHAR(500),
    
    -- TRAIN Sync
    train_completion_id VARCHAR(100) UNIQUE,
    synced_from_train BOOLEAN DEFAULT FALSE,
    last_sync_date TIMESTAMP,
    
    -- Status
    status VARCHAR(50) DEFAULT 'active',
    
    -- Timestamps
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    UNIQUE(volunteer_id, course_id, completion_date)
);

-- Professional Certifications
CREATE TABLE certifications (
    id SERIAL PRIMARY KEY,
    volunteer_id INTEGER NOT NULL REFERENCES volunteers(id) ON DELETE CASCADE,
    
    -- Certification Details
    certification_type VARCHAR(100) NOT NULL,
    license_number VARCHAR(100),
    issuing_authority VARCHAR(255),
    
    -- Dates
    issue_date DATE,
    expiration_date DATE,
    
    -- Verification
    verification_status VARCHAR(50) DEFAULT 'pending',
    verification_date DATE,
    verification_method VARCHAR(100),
    verified_by INTEGER REFERENCES users(id),
    
    -- Document
    document_url VARCHAR(500),
    document_type VARCHAR(50),
    
    -- Notes
    notes TEXT,
    
    -- Timestamps
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Training Requirements
CREATE TABLE training_requirements (
    id SERIAL PRIMARY KEY,
    tenant_id INTEGER NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    
    -- Requirement Details
    name VARCHAR(255) NOT NULL,
    description TEXT,
    
    -- Linked Course
    course_id INTEGER REFERENCES training_courses(id),
    
    -- Applicability
    required_for_roles TEXT,
    required_for_event_types TEXT,
    
    -- Grace Period
    grace_period_days INTEGER DEFAULT 0,
    
    -- Timestamps
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Indexes
CREATE INDEX idx_training_courses_tenant ON training_courses(tenant_id);
CREATE INDEX idx_training_courses_train_id ON training_courses(train_course_id);
CREATE INDEX idx_volunteer_training_volunteer ON volunteer_training(volunteer_id);
CREATE INDEX idx_volunteer_training_course ON volunteer_training(course_id);
CREATE INDEX idx_volunteer_training_expiration ON volunteer_training(expiration_date);
CREATE INDEX idx_certifications_volunteer ON certifications(volunteer_id);
CREATE INDEX idx_certifications_expiration ON certifications(expiration_date);

-- Grant permissions
GRANT ALL PRIVILEGES ON training_courses TO vvhs;
GRANT ALL PRIVILEGES ON volunteer_training TO vvhs;
GRANT ALL PRIVILEGES ON certifications TO vvhs;
GRANT ALL PRIVILEGES ON training_requirements TO vvhs;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO vvhs;

-- Insert TRAIN courses (more comprehensive list)
INSERT INTO training_courses (tenant_id, train_course_id, name, description, course_code, provider, category, is_required, validity_period_days) VALUES
-- Emergency Management (FEMA)
(1, 'TRAIN-ICS100', 'ICS 100: Introduction to Incident Command System', 'Basic incident command system training', 'ICS-100', 'FEMA', 'Emergency Management', true, 1460),
(1, 'TRAIN-ICS200', 'ICS 200: ICS for Single Resources', 'Intermediate incident command system', 'ICS-200', 'FEMA', 'Emergency Management', true, 1460),
(1, 'TRAIN-ICS300', 'ICS 300: Intermediate ICS', 'Advanced incident command for supervisors', 'ICS-300', 'FEMA', 'Emergency Management', false, 1460),
(1, 'TRAIN-ICS400', 'ICS 400: Advanced ICS', 'Advanced ICS for command staff', 'ICS-400', 'FEMA', 'Emergency Management', false, 1460),
(1, 'TRAIN-NIMS700', 'IS-700: National Incident Management System', 'NIMS overview', 'IS-700', 'FEMA', 'Emergency Management', true, NULL),
(1, 'TRAIN-NIMS800', 'IS-800: National Response Framework', 'NRF overview', 'IS-800', 'FEMA', 'Emergency Management', true, NULL),

-- Medical Training
(1, 'TRAIN-CPR', 'CPR/AED for Healthcare Providers', 'CPR and AED training', 'CPR-HEALTH', 'American Heart Association', 'Medical', true, 730),
(1, 'TRAIN-BLS', 'Basic Life Support (BLS)', 'Basic life support for healthcare', 'BLS', 'American Heart Association', 'Medical', true, 730),
(1, 'TRAIN-ACLS', 'Advanced Cardiac Life Support', 'Advanced cardiac life support', 'ACLS', 'American Heart Association', 'Medical', false, 730),
(1, 'TRAIN-PALS', 'Pediatric Advanced Life Support', 'Pediatric advanced life support', 'PALS', 'American Heart Association', 'Medical', false, 730),
(1, 'TRAIN-FIRST-AID', 'First Aid Certification', 'Basic first aid', 'FIRST-AID', 'American Red Cross', 'Medical', false, 730),

-- Public Health & Compliance
(1, 'TRAIN-HIPAA', 'HIPAA Privacy and Security', 'HIPAA compliance', 'HIPAA-101', 'VDH', 'Compliance', true, 365),
(1, 'TRAIN-INFECTION', 'Infection Control and Prevention', 'Standard precautions', 'INFECT-PREV', 'CDC', 'Medical', true, 365),
(1, 'TRAIN-VAX', 'Vaccine Administration Training', 'Vaccine administration', 'VAX-ADMIN', 'CDC', 'Medical', false, NULL),
(1, 'TRAIN-VAX-STORAGE', 'Vaccine Storage and Handling', 'Proper vaccine storage', 'VAX-STORE', 'CDC', 'Medical', false, NULL),

-- Specialized Training
(1, 'TRAIN-DISASTER-MED', 'Disaster Medicine', 'Medical response in disasters', 'DM-101', 'NDMS', 'Emergency Management', false, NULL),
(1, 'TRAIN-MENTAL-HEALTH', 'Psychological First Aid', 'Mental health in disasters', 'PFA', 'SAMHSA', 'Behavioral Health', false, NULL),
(1, 'TRAIN-SHELTER-OPS', 'Shelter Operations', 'Emergency shelter management', 'SHELTER-101', 'American Red Cross', 'Emergency Management', false, NULL);

-- Insert volunteer training records (comprehensive for tenant 1 volunteers)
INSERT INTO volunteer_training (volunteer_id, course_id, completion_date, expiration_date, score, train_completion_id, synced_from_train, status) VALUES
-- Alice Anderson (volunteer 1) - Fully trained senior volunteer
(1, 1, '2023-01-15', '2027-01-15', 95.0, 'TRAIN-COMP-1-1', true, 'active'),
(1, 2, '2023-02-20', '2027-02-20', 92.0, 'TRAIN-COMP-1-2', true, 'active'),
(1, 5, '2023-03-10', NULL, 98.0, 'TRAIN-COMP-1-5', true, 'active'),
(1, 6, '2023-03-15', NULL, 96.0, 'TRAIN-COMP-1-6', true, 'active'),
(1, 7, '2024-01-10', '2026-01-10', 100.0, 'TRAIN-COMP-1-7', true, 'active'),
(1, 8, '2024-01-10', '2026-01-10', 98.0, 'TRAIN-COMP-1-8', true, 'active'),
(1, 9, '2024-02-15', '2026-02-15', 97.0, 'TRAIN-COMP-1-9', true, 'active'),
(1, 10, '2024-03-01', '2026-03-01', 99.0, 'TRAIN-COMP-1-10', true, 'active'),
(1, 12, '2025-01-01', '2026-01-01', 100.0, 'TRAIN-COMP-1-12', true, 'active'),
(1, 13, '2024-12-01', '2025-12-01', 95.0, 'TRAIN-COMP-1-13', true, 'active'),

-- Bob Brown (volunteer 2) - Some expired
(2, 1, '2021-03-15', '2025-03-15', 88.0, 'TRAIN-COMP-2-1', true, 'expired'),
(2, 7, '2022-06-01', '2024-06-01', 90.0, 'TRAIN-COMP-2-7', true, 'expired'),
(2, 12, '2024-01-01', '2025-01-01', 95.0, 'TRAIN-COMP-2-12', true, 'active'),

-- Carol Clark (volunteer 3) - Medical professional, comprehensive
(3, 1, '2024-05-10', '2028-05-10', 100.0, 'TRAIN-COMP-3-1', true, 'active'),
(3, 2, '2024-06-01', '2028-06-01', 100.0, 'TRAIN-COMP-3-2', true, 'active'),
(3, 5, '2024-05-15', NULL, 100.0, 'TRAIN-COMP-3-5', true, 'active'),
(3, 7, '2024-11-01', '2026-11-01', 100.0, 'TRAIN-COMP-3-7', true, 'active'),
(3, 8, '2024-11-01', '2026-11-01', 100.0, 'TRAIN-COMP-3-8', true, 'active'),
(3, 9, '2024-09-15', '2026-09-15', 100.0, 'TRAIN-COMP-3-9', true, 'active'),
(3, 12, '2025-01-15', '2026-01-15', 100.0, 'TRAIN-COMP-3-12', true, 'active'),
(3, 13, '2025-01-20', '2026-01-20', 100.0, 'TRAIN-COMP-3-13', true, 'active'),
(3, 16, '2024-08-10', NULL, 98.0, 'TRAIN-COMP-3-16', true, 'active'),

-- David Davis (volunteer 4) - Paramedic
(4, 1, '2024-03-01', '2028-03-01', 94.0, 'TRAIN-COMP-4-1', true, 'active'),
(4, 7, '2024-02-10', '2026-02-10', 96.0, 'TRAIN-COMP-4-7', true, 'active'),
(4, 8, '2024-02-10', '2026-02-10', 95.0, 'TRAIN-COMP-4-8', true, 'active'),
(4, 9, '2024-03-15', '2026-03-15', 97.0, 'TRAIN-COMP-4-9', true, 'active'),
(4, 10, '2024-03-20', '2026-03-20', 98.0, 'TRAIN-COMP-4-10', true, 'active'),
(4, 12, '2024-11-01', '2025-11-01', 100.0, 'TRAIN-COMP-4-12', true, 'active'),

-- Emma Evans (volunteer 5) - RN Pediatric
(5, 1, '2024-05-01', '2028-05-01', 92.0, 'TRAIN-COMP-5-1', true, 'active'),
(5, 7, '2024-06-15', '2026-06-15', 95.0, 'TRAIN-COMP-5-7', true, 'active'),
(5, 8, '2024-06-15', '2026-06-15', 94.0, 'TRAIN-COMP-5-8', true, 'active'),
(5, 10, '2024-07-01', '2026-07-01', 98.0, 'TRAIN-COMP-5-10', true, 'active'),
(5, 12, '2024-10-15', '2025-10-15', 96.0, 'TRAIN-COMP-5-12', true, 'active'),
(5, 14, '2024-08-20', NULL, 94.0, 'TRAIN-COMP-5-14', true, 'active'),

-- Frank Foster (volunteer 6) - EMT
(6, 1, '2024-06-01', '2028-06-01', 89.0, 'TRAIN-COMP-6-1', true, 'active'),
(6, 7, '2024-08-10', '2026-08-10', 91.0, 'TRAIN-COMP-6-7', true, 'active'),
(6, 12, '2024-09-15', '2025-09-15', 93.0, 'TRAIN-COMP-6-12', true, 'active'),

-- Grace Garcia (volunteer 7) - PA
(7, 1, '2024-06-20', '2028-06-20', 96.0, 'TRAIN-COMP-7-1', true, 'active'),
(7, 5, '2024-07-01', NULL, 97.0, 'TRAIN-COMP-7-5', true, 'active'),
(7, 7, '2024-05-10', '2026-05-10', 98.0, 'TRAIN-COMP-7-7', true, 'active'),
(7, 8, '2024-05-10', '2026-05-10', 97.0, 'TRAIN-COMP-7-8', true, 'active'),
(7, 9, '2024-06-05', '2026-06-05', 99.0, 'TRAIN-COMP-7-9', true, 'active'),
(7, 12, '2024-11-10', '2025-11-10', 95.0, 'TRAIN-COMP-7-12', true, 'active'),

-- Henry Harris (volunteer 8) - ICU RN
(8, 1, '2024-07-15', '2028-07-15', 93.0, 'TRAIN-COMP-8-1', true, 'active'),
(8, 7, '2024-03-20', '2026-03-20', 96.0, 'TRAIN-COMP-8-7', true, 'active'),
(8, 8, '2024-03-20', '2026-03-20', 95.0, 'TRAIN-COMP-8-8', true, 'active'),
(8, 9, '2024-04-10', '2026-04-10', 98.0, 'TRAIN-COMP-8-9', true, 'active'),
(8, 12, '2024-10-05', '2025-10-05', 97.0, 'TRAIN-COMP-8-12', true, 'active'),
(8, 13, '2024-09-20', '2025-09-20', 96.0, 'TRAIN-COMP-8-13', true, 'active'),

-- Isabel Ingram (volunteer 9) - Pharmacist
(9, 1, '2024-08-10', '2028-08-10', 91.0, 'TRAIN-COMP-9-1', true, 'active'),
(9, 7, '2024-07-01', '2026-07-01', 93.0, 'TRAIN-COMP-9-7', true, 'active'),
(9, 12, '2024-10-20', '2025-10-20', 95.0, 'TRAIN-COMP-9-12', true, 'active'),
(9, 14, '2024-08-25', NULL, 97.0, 'TRAIN-COMP-9-14', true, 'active'),
(9, 15, '2024-09-05', NULL, 96.0, 'TRAIN-COMP-9-15', true, 'active'),

-- Jack Jackson (volunteer 10) - Student
(10, 7, '2024-09-01', '2026-09-01', 88.0, 'TRAIN-COMP-10-7', true, 'active'),
(10, 8, '2024-09-01', '2026-09-01', 87.0, 'TRAIN-COMP-10-8', true, 'active'),
(10, 12, '2024-10-10', '2025-10-10', 90.0, 'TRAIN-COMP-10-12', true, 'active');

-- Insert certifications (comprehensive for all volunteers)
INSERT INTO certifications (volunteer_id, certification_type, license_number, issuing_authority, issue_date, expiration_date, verification_status, verified_by) VALUES
-- Alice Anderson
(1, 'Registered Nurse (RN)', 'RN123456', 'Virginia Board of Nursing', '2020-01-15', '2027-01-15', 'verified', 1),
(1, 'Basic Life Support (BLS)', 'BLS-987654', 'American Heart Association', '2024-01-10', '2026-01-10', 'verified', 1),
(1, 'Advanced Cardiovascular Life Support (ACLS)', 'ACLS-456789', 'American Heart Association', '2024-02-15', '2026-02-15', 'verified', 1),
(1, 'Pediatric Advanced Life Support (PALS)', 'PALS-123789', 'American Heart Association', '2024-03-01', '2026-03-01', 'verified', 1),

-- Bob Brown
(2, 'Emergency Medical Technician (EMT)', 'EMT789012', 'Virginia Office of EMS', '2022-06-01', '2025-06-01', 'verified', 1),
(2, 'CPR/AED', 'CPR-112233', 'American Red Cross', '2024-03-15', '2026-03-15', 'verified', 1),

-- Carol Clark
(3, 'Medical Doctor (MD)', 'MD456789', 'Virginia Board of Medicine', '2015-07-01', '2027-12-31', 'verified', 1),
(3, 'Board Certified - Internal Medicine', 'ABIM-789012', 'American Board of Internal Medicine', '2016-01-01', NULL, 'verified', 1),
(4, 'Registered Nurse (RN)', 'RN654321', 'Virginia Board of Nursing', '2018-05-15', '2026-05-15', 'verified', 1),
(4, 'CPR/BLS', 'BLS-445566', 'American Heart Association', '2024-10-15', '2026-10-15', 'verified', 1);

-- Comments
COMMENT ON TABLE training_courses IS 'Catalog of training courses including TRAIN courses';
COMMENT ON TABLE volunteer_training IS 'Training completion records for volunteers';
COMMENT ON TABLE certifications IS 'Professional licenses and certifications';
COMMENT ON TABLE training_requirements IS 'Training requirements for specific roles/events';