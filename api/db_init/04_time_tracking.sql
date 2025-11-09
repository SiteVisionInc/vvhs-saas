-- api/db_init/04_time_tracking.sql
-- Time Tracking & Check-In Schema
-- Implements section 1.5 from roadmap

-- Time Entries (volunteer hours)
CREATE TABLE time_entries (
    id SERIAL PRIMARY KEY,
    tenant_id INTEGER NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    volunteer_id INTEGER NOT NULL REFERENCES volunteers(id) ON DELETE CASCADE,
    event_id INTEGER REFERENCES events(id) ON DELETE SET NULL,
    shift_id INTEGER REFERENCES shifts(id) ON DELETE SET NULL,
    
    -- Time tracking
    check_in_time TIMESTAMP NOT NULL,
    check_out_time TIMESTAMP,
    duration_minutes INTEGER,
    hours_decimal DECIMAL(5,2),
    
    -- Entry method
    entry_method VARCHAR(50) NOT NULL DEFAULT 'manual', -- manual, qr_code, kiosk, geolocation
    
    -- Geolocation (optional)
    check_in_lat DECIMAL(10,8),
    check_in_lng DECIMAL(11,8),
    check_out_lat DECIMAL(10,8),
    check_out_lng DECIMAL(11,8),
    location_verified BOOLEAN DEFAULT FALSE,
    
    -- Approval workflow
    status VARCHAR(50) NOT NULL DEFAULT 'pending', -- pending, approved, rejected, disputed
    submitted_by INTEGER REFERENCES users(id), -- Self-entry or coordinator
    approved_by INTEGER REFERENCES users(id),
    approved_at TIMESTAMP,
    rejection_reason TEXT,
    
    -- Notes
    volunteer_notes TEXT,
    coordinator_notes TEXT,
    dispute_notes TEXT,
    
    -- Timestamps
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Constraints
    CHECK (check_out_time IS NULL OR check_out_time > check_in_time),
    CHECK (hours_decimal >= 0)
);

-- QR Codes for events/shifts
CREATE TABLE event_qr_codes (
    id SERIAL PRIMARY KEY,
    event_id INTEGER REFERENCES events(id) ON DELETE CASCADE,
    shift_id INTEGER REFERENCES shifts(id) ON DELETE CASCADE,
    
    -- QR Code data
    qr_code_hash VARCHAR(255) UNIQUE NOT NULL,
    qr_code_url VARCHAR(500),
    
    -- Validity
    valid_from TIMESTAMP NOT NULL,
    valid_until TIMESTAMP NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    max_uses INTEGER, -- NULL = unlimited
    use_count INTEGER DEFAULT 0,
    
    -- Configuration
    require_photo BOOLEAN DEFAULT FALSE,
    require_signature BOOLEAN DEFAULT FALSE,
    allow_early_checkin_minutes INTEGER DEFAULT 15,
    allow_late_checkout_minutes INTEGER DEFAULT 30,
    
    -- Metadata
    created_by INTEGER REFERENCES users(id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Check-in sessions (for kiosk/mobile)
CREATE TABLE checkin_sessions (
    id SERIAL PRIMARY KEY,
    volunteer_id INTEGER NOT NULL REFERENCES volunteers(id),
    event_id INTEGER REFERENCES events(id),
    qr_code_id INTEGER REFERENCES event_qr_codes(id),
    
    -- Session data
    check_in_time TIMESTAMP NOT NULL,
    check_out_time TIMESTAMP,
    device_info JSONB, -- Device type, browser, etc.
    ip_address VARCHAR(45),
    
    -- Status
    status VARCHAR(50) DEFAULT 'active', -- active, completed, abandoned
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Indexes
CREATE INDEX idx_time_entries_volunteer ON time_entries(volunteer_id, check_in_time);
CREATE INDEX idx_time_entries_event ON time_entries(event_id);
CREATE INDEX idx_time_entries_status ON time_entries(status);
CREATE INDEX idx_time_entries_pending ON time_entries(status, tenant_id) WHERE status = 'pending';
CREATE INDEX idx_event_qr_codes_hash ON event_qr_codes(qr_code_hash);
CREATE INDEX idx_checkin_sessions_volunteer ON checkin_sessions(volunteer_id);

-- Grant permissions
GRANT ALL PRIVILEGES ON time_entries TO vvhs;
GRANT ALL PRIVILEGES ON event_qr_codes TO vvhs;
GRANT ALL PRIVILEGES ON checkin_sessions TO vvhs;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO vvhs;

-- Sample time entries for existing volunteers
INSERT INTO time_entries (tenant_id, volunteer_id, event_id, check_in_time, check_out_time, duration_minutes, hours_decimal, entry_method, status, approved_by) VALUES
-- Alice Anderson (volunteer_id = 1)
(1, 1, 1, '2025-11-01 08:00:00', '2025-11-01 16:00:00', 480, 8.00, 'manual', 'approved', 1),
(1, 1, 1, '2025-11-02 08:00:00', '2025-11-02 16:00:00', 480, 8.00, 'manual', 'approved', 1),
(1, 1, 1, '2025-11-03 09:00:00', '2025-11-03 15:00:00', 360, 6.00, 'qr_code', 'approved', 1),

-- Carol Clark (volunteer_id = 3)
(1, 3, 1, '2025-11-01 10:00:00', '2025-11-01 14:00:00', 240, 4.00, 'manual', 'approved', 1),
(1, 3, 2, '2025-11-05 09:00:00', '2025-11-05 17:00:00', 480, 8.00, 'manual', 'approved', 1),

-- Jane Doe (volunteer_id = 4) - pending approval
(2, 4, NULL, '2025-11-06 08:30:00', '2025-11-06 12:30:00', 240, 4.00, 'manual', 'pending', NULL),
(2, 4, NULL, '2025-11-07 13:00:00', '2025-11-07 17:00:00', 240, 4.00, 'qr_code', 'pending', NULL);

-- Sample QR codes for upcoming events
INSERT INTO event_qr_codes (event_id, qr_code_hash, qr_code_url, valid_from, valid_until, is_active, created_by) VALUES
(1, 'qr_event1_2025', 'https://vvhs.org/checkin/qr_event1_2025', 
 '2025-11-20 07:00:00', '2025-11-20 19:00:00', true, 1),
(2, 'qr_event2_2025', 'https://vvhs.org/checkin/qr_event2_2025',
 '2025-12-05 08:00:00', '2025-12-05 18:00:00', true, 1);

-- Comments
COMMENT ON TABLE time_entries IS 'Volunteer time tracking and hour entries';
COMMENT ON TABLE event_qr_codes IS 'QR codes for event/shift check-in';
COMMENT ON TABLE checkin_sessions IS 'Active check-in sessions for mobile/kiosk';