-- Behavioral Health Module Database Schema
-- Part 2.1: Core Data Model
-- Creates all tables for the BH clinical workflow system

-- ==================== PATIENTS ====================

CREATE TABLE bh_patients (
    id SERIAL PRIMARY KEY,
    tenant_id INTEGER NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    
    -- Medical Record Number
    mrn VARCHAR(100),
    
    -- Demographics (PHI - should be encrypted in production)
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    dob DATE,
    gender VARCHAR(50),
    
    -- Contact Information (JSONB for flexibility)
    guardians JSONB,  -- Array of guardian objects
    addresses JSONB,  -- Array of address objects
    phones JSONB,     -- Array of phone objects
    emergency_contacts JSONB,
    
    -- Consent
    consent_flags JSONB,  -- {treatment: true, release_info: false}
    
    -- Clinical
    risk_level VARCHAR(50) DEFAULT 'low',
    notes TEXT,  -- Should be encrypted in production
    
    -- Timestamps
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    created_by INTEGER NOT NULL REFERENCES users(id),
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Indexes
    INDEX idx_bh_patients_tenant (tenant_id),
    INDEX idx_bh_patients_mrn (mrn),
    INDEX idx_bh_patients_risk (risk_level)
);

-- ==================== SCREENINGS ====================

CREATE TABLE bh_screenings (
    id SERIAL PRIMARY KEY,
    patient_id INTEGER NOT NULL REFERENCES bh_patients(id) ON DELETE CASCADE,
    
    -- Instrument
    instrument_type VARCHAR(100) NOT NULL,  -- 'C-SSRS', 'ASAM', 'PHQ-9'
    
    -- Results
    score DECIMAL(5,2),
    details_json JSONB,  -- Full instrument results
    
    -- Clinician
    clinician_id INTEGER NOT NULL REFERENCES bh_users(id),
    screening_date TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    
    -- Timestamps
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    
    -- Indexes
    INDEX idx_bh_screenings_patient (patient_id),
    INDEX idx_bh_screenings_date (screening_date)
);

-- ==================== FACILITIES ====================

CREATE TABLE bh_facilities (
    id SERIAL PRIMARY KEY,
    tenant_id INTEGER NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    
    -- Facility Information
    name VARCHAR(255) NOT NULL,
    facility_type VARCHAR(100) NOT NULL,  -- hospital, detox, residential
    region_id INTEGER,
    
    -- Capabilities
    capabilities JSONB,  -- ['adolescent', 'geriatric', 'SUD', 'detox']
    
    -- Contact
    contact_name VARCHAR(255),
    contact_phone VARCHAR(20),
    contact_email VARCHAR(255),
    address JSONB,
    
    -- Integration
    emr_id VARCHAR(100),  -- External EHR system ID
    
    -- Status
    is_active BOOLEAN DEFAULT TRUE NOT NULL,
    
    -- Timestamps
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Indexes
    INDEX idx_bh_facilities_tenant (tenant_id),
    INDEX idx_bh_facilities_type (facility_type),
    INDEX idx_bh_facilities_region (region_id)
);

-- ==================== BED SNAPSHOTS ====================

CREATE TABLE bh_bed_snapshots (
    id SERIAL PRIMARY KEY,
    facility_id INTEGER NOT NULL REFERENCES bh_facilities(id) ON DELETE CASCADE,
    
    -- Bed Type
    unit_name VARCHAR(100),
    bed_type VARCHAR(100) NOT NULL,  -- general, adolescent, SUD, detox
    
    -- Capacity
    capacity_total INTEGER NOT NULL,
    capacity_available INTEGER NOT NULL,
    
    -- Reporting
    last_reported_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    reported_by INTEGER REFERENCES bh_users(id),
    
    -- Constraints
    constraints JSONB,  -- {age_min: 12, age_max: 17, gender: 'F'}
    
    -- Indexes
    INDEX idx_bh_beds_facility (facility_id),
    INDEX idx_bh_beds_type (bed_type),
    INDEX idx_bh_beds_reported (last_reported_at),
    
    -- Unique constraint
    UNIQUE(facility_id, unit_name, bed_type)
);

-- ==================== REFERRALS ====================

CREATE TABLE bh_referrals (
    id SERIAL PRIMARY KEY,
    patient_id INTEGER NOT NULL REFERENCES bh_patients(id) ON DELETE CASCADE,
    
    -- Referrer
    created_by INTEGER NOT NULL REFERENCES bh_users(id),
    region_id INTEGER,
    
    -- Status
    status VARCHAR(50) NOT NULL DEFAULT 'draft',  -- draft, submitted, accepted, declined, placed, discharged
    priority VARCHAR(50) NOT NULL DEFAULT 'routine',  -- routine, urgent, emergency
    
    -- Dates
    referral_date TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    placement_date TIMESTAMP,
    discharge_date TIMESTAMP,
    
    -- Documents
    attachments JSONB,  -- Array of S3 document URLs
    
    -- Notes
    notes TEXT,
    
    -- Timestamps
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Indexes
    INDEX idx_bh_referrals_patient (patient_id),
    INDEX idx_bh_referrals_status (status),
    INDEX idx_bh_referrals_date (referral_date),
    INDEX idx_bh_referrals_priority (priority)
);

-- ==================== PLACEMENTS ====================

CREATE TABLE bh_placements (
    id SERIAL PRIMARY KEY,
    referral_id INTEGER NOT NULL REFERENCES bh_referrals(id) ON DELETE CASCADE,
    facility_id INTEGER NOT NULL REFERENCES bh_facilities(id),
    
    -- Placement Details
    bed_type VARCHAR(100) NOT NULL,
    
    -- Decision
    decision_by INTEGER NOT NULL REFERENCES bh_users(id),
    decision_date TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    
    -- Admission/Discharge
    admission_date TIMESTAMP,
    discharge_date TIMESTAMP,
    
    -- Transport
    transport_details JSONB,
    
    -- Outcome
    outcome VARCHAR(100),  -- completed, transfer, AMA, deceased
    length_of_stay INTEGER,  -- Days
    
    -- Notes
    notes TEXT,
    
    -- Timestamps
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Indexes
    INDEX idx_bh_placements_referral (referral_id),
    INDEX idx_bh_placements_facility (facility_id),
    INDEX idx_bh_placements_admission (admission_date),
    INDEX idx_bh_placements_discharge (discharge_date)
);

-- ==================== BH USERS ====================

CREATE TABLE bh_users (
    id SERIAL PRIMARY KEY,
    base_user_id INTEGER NOT NULL UNIQUE REFERENCES users(id) ON DELETE CASCADE,
    
    -- BH Role
    role VARCHAR(100) NOT NULL,  -- clinician, facility_coordinator, mobile_crisis, peer_recovery
    
    -- Credentials
    npi VARCHAR(20),  -- National Provider Identifier
    license_number VARCHAR(50),
    license_type VARCHAR(50),  -- MD, LCSW, RN, etc.
    
    -- Specializations
    specializations JSONB,  -- ['adolescent', 'geriatric', 'SUD', 'trauma']
    
    -- Timestamps
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Indexes
    INDEX idx_bh_users_base (base_user_id),
    INDEX idx_bh_users_role (role)
);

-- ==================== FOLLOW-UPS ====================

CREATE TABLE bh_followups (
    id SERIAL PRIMARY KEY,
    placement_id INTEGER NOT NULL REFERENCES bh_placements(id) ON DELETE CASCADE,
    
    -- Schedule
    scheduled_date DATE NOT NULL,
    followup_type VARCHAR(50),  -- day_30, day_60, day_90
    
    -- Assignment
    assigned_to INTEGER REFERENCES bh_users(id),
    
    -- Completion
    completed_date DATE,
    completed_by INTEGER REFERENCES bh_users(id),
    
    -- Outcome
    outcome_data JSONB,  -- {status: 'stable', housing: 'stable', employment: 'seeking'}
    
    -- Status
    status VARCHAR(50) DEFAULT 'scheduled',  -- scheduled, completed, missed, declined
    
    -- Notes
    notes TEXT,
    
    -- Timestamps
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Indexes
    INDEX idx_bh_followups_placement (placement_id),
    INDEX idx_bh_followups_scheduled (scheduled_date),
    INDEX idx_bh_followups_status (status)
);

-- ==================== GRANTS ====================

GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO vvhs;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO vvhs;

-- ==================== COMMENTS ====================

COMMENT ON TABLE bh_patients IS 'Behavioral health patients - contains PHI';
COMMENT ON TABLE bh_screenings IS 'Clinical screening/assessment results';
COMMENT ON TABLE bh_facilities IS 'Behavioral health treatment facilities';
COMMENT ON TABLE bh_bed_snapshots IS 'Real-time bed availability tracking';
COMMENT ON TABLE bh_referrals IS 'Patient referrals for placement';
COMMENT ON TABLE bh_placements IS 'Actual patient placements at facilities';
COMMENT ON TABLE bh_users IS 'BH-specific user roles and credentials';
COMMENT ON TABLE bh_followups IS 'Post-discharge follow-up tracking';

-- ==================== SAMPLE DATA ====================

-- Insert sample BH users
INSERT INTO bh_users (base_user_id, role, npi, license_number, license_type) VALUES
(1, 'clinician', '1234567890', 'MD123456', 'MD'),
(2, 'facility_coordinator', NULL, NULL, NULL);

-- Insert sample facility
INSERT INTO bh_facilities (tenant_id, name, facility_type, region_id, capabilities, contact_name, contact_phone, is_active) VALUES
(1, 'Central State Hospital', 'hospital', 1, '["adolescent", "adult", "geriatric", "SUD"]'::jsonb, 'Jane Smith', '804-555-1234', true),
(1, 'Riverside Detox Center', 'detox', 1, '["adult", "SUD", "detox"]'::jsonb, 'John Doe', '804-555-5678', true),
(1, 'Hope Residential Treatment', 'residential', 2, '["adolescent", "adult"]'::jsonb, 'Mary Johnson', '757-555-9012', true);

-- Insert sample bed availability
INSERT INTO bh_bed_snapshots (facility_id, unit_name, bed_type, capacity_total, capacity_available, last_reported_at, constraints) VALUES
(1, 'Adult Unit A', 'general', 20, 5, CURRENT_TIMESTAMP, '{"age_min": 18, "age_max": 64}'::jsonb),
(1, 'Adolescent Unit', 'adolescent', 12, 3, CURRENT_TIMESTAMP, '{"age_min": 12, "age_max": 17}'::jsonb),
(2, 'Detox Unit', 'detox', 15, 8, CURRENT_TIMESTAMP, '{"age_min": 18}'::jsonb),
(3, 'Residential A', 'residential', 10, 2, CURRENT_TIMESTAMP, '{"age_min": 18}'::jsonb);

RAISE NOTICE '';
RAISE NOTICE '=== Behavioral Health Module Initialized ===';
RAISE NOTICE '';
RAISE NOTICE 'Created:';
RAISE NOTICE '  - 8 BH tables';
RAISE NOTICE '  - 3 Sample facilities';
RAISE NOTICE '  - 4 Bed availability snapshots';
RAISE NOTICE '';
RAISE NOTICE 'Ready for clinical workflow!';
RAISE NOTICE '';