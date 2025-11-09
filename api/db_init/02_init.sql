-- api/db_init/02_init.sql (ENHANCED - Advanced Scheduling)
-- Advanced Scheduling & Shift Management Tables
-- Implements section 1.2 from the roadmap

-- Shift Templates for recurring shift creation
CREATE TABLE shift_templates (
    id SERIAL PRIMARY KEY,
    tenant_id INTEGER NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    
    -- Recurrence pattern
    recurrence_pattern JSONB,
    duration_minutes INTEGER NOT NULL,
    
    -- Capacity
    max_volunteers INTEGER,
    min_volunteers INTEGER DEFAULT 1,
    
    -- Requirements
    required_skills JSONB,
    required_training JSONB,
    
    -- Configuration
    is_active BOOLEAN DEFAULT TRUE,
    allow_self_signup BOOLEAN DEFAULT FALSE,
    enable_waitlist BOOLEAN DEFAULT TRUE,
    
    -- Metadata
    created_by INTEGER REFERENCES users(id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Shift Waitlist Queue
CREATE TABLE shift_waitlists (
    id SERIAL PRIMARY KEY,
    shift_id INTEGER NOT NULL REFERENCES shifts(id) ON DELETE CASCADE,
    volunteer_id INTEGER NOT NULL REFERENCES volunteers(id) ON DELETE CASCADE,
    
    -- Queue management
    position INTEGER NOT NULL,
    priority_score INTEGER DEFAULT 0,
    
    -- Status tracking
    status VARCHAR(50) NOT NULL DEFAULT 'waiting',
    joined_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    promoted_at TIMESTAMP,
    notified_at TIMESTAMP,
    
    -- Metadata
    notes TEXT,
    auto_accept BOOLEAN DEFAULT FALSE,
    
    -- Constraints
    UNIQUE(shift_id, volunteer_id),
    CHECK (position > 0)
);

-- Volunteer Availability Tracking
CREATE TABLE volunteer_availability (
    id SERIAL PRIMARY KEY,
    volunteer_id INTEGER NOT NULL REFERENCES volunteers(id) ON DELETE CASCADE,
    
    -- Date range
    start_date DATE NOT NULL,
    end_date DATE NOT NULL,
    
    -- Time of day (optional)
    start_time TIME,
    end_time TIME,
    
    -- Recurrence pattern for recurring availability
    recurrence_pattern JSONB,
    
    -- Type
    availability_type VARCHAR(50) DEFAULT 'general',
    event_id INTEGER REFERENCES events(id) ON DELETE CASCADE,
    
    -- Status
    is_active BOOLEAN DEFAULT TRUE,
    
    -- Metadata
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Constraints
    CHECK (start_date <= end_date),
    CHECK (start_time IS NULL OR end_time IS NULL OR start_time < end_time)
);

-- Shift Swap Requests
CREATE TABLE shift_swap_requests (
    id SERIAL PRIMARY KEY,
    
    -- Original assignment
    original_assignment_id INTEGER NOT NULL REFERENCES event_assignments(id),
    requesting_volunteer_id INTEGER NOT NULL REFERENCES volunteers(id),
    
    -- Target volunteer (optional)
    target_volunteer_id INTEGER REFERENCES volunteers(id),
    
    -- Status
    status VARCHAR(50) NOT NULL DEFAULT 'pending',
    
    -- Approval workflow
    approved_by INTEGER REFERENCES users(id),
    approved_at TIMESTAMP,
    rejection_reason TEXT,
    
    -- Metadata
    reason TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Enhanced Shifts Table
ALTER TABLE shifts ADD COLUMN IF NOT EXISTS template_id INTEGER REFERENCES shift_templates(id);
ALTER TABLE shifts ADD COLUMN IF NOT EXISTS allow_self_signup BOOLEAN DEFAULT FALSE;
ALTER TABLE shifts ADD COLUMN IF NOT EXISTS enable_waitlist BOOLEAN DEFAULT TRUE;
ALTER TABLE shifts ADD COLUMN IF NOT EXISTS waitlist_capacity INTEGER DEFAULT 10;
ALTER TABLE shifts ADD COLUMN IF NOT EXISTS required_skills JSONB;
ALTER TABLE shifts ADD COLUMN IF NOT EXISTS conflict_detection BOOLEAN DEFAULT TRUE;

-- Indexes
CREATE INDEX idx_shift_templates_tenant ON shift_templates(tenant_id);
CREATE INDEX idx_shift_waitlists_shift ON shift_waitlists(shift_id, position);
CREATE INDEX idx_shift_waitlists_volunteer ON shift_waitlists(volunteer_id);
CREATE INDEX idx_volunteer_availability_dates ON volunteer_availability(volunteer_id, start_date, end_date);
CREATE INDEX idx_shift_swap_status ON shift_swap_requests(status, created_at);

-- Update existing shifts to have sensible defaults
UPDATE shifts SET 
    allow_self_signup = FALSE,
    enable_waitlist = TRUE,
    waitlist_capacity = 10,
    conflict_detection = TRUE
WHERE allow_self_signup IS NULL;

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_shifts_self_signup ON shifts(allow_self_signup) WHERE allow_self_signup = TRUE;
CREATE INDEX IF NOT EXISTS idx_shifts_template ON shifts(template_id);

COMMENT ON COLUMN shifts.allow_self_signup IS 'Whether volunteers can self-signup for this shift';
COMMENT ON COLUMN shifts.enable_waitlist IS 'Whether to enable waitlist when shift is full';
COMMENT ON COLUMN shifts.waitlist_capacity IS 'Maximum number of volunteers on waitlist';
COMMENT ON COLUMN shifts.required_skills IS 'JSON array of required skills';
COMMENT ON COLUMN shifts.conflict_detection IS 'Whether to prevent double-booking';

-- Grant permissions
GRANT ALL PRIVILEGES ON shift_templates TO vvhs;
GRANT ALL PRIVILEGES ON shift_waitlists TO vvhs;
GRANT ALL PRIVILEGES ON volunteer_availability TO vvhs;
GRANT ALL PRIVILEGES ON shift_swap_requests TO vvhs;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO vvhs;

-- Sample shift template data (2x more)
INSERT INTO shift_templates (tenant_id, name, description, recurrence_pattern, duration_minutes, max_volunteers, allow_self_signup, enable_waitlist, created_by) VALUES
(1, 'Weekly Vaccine Clinic - Morning', 'Standard morning vaccine clinic shift', 
 '{"frequency": "weekly", "days": [2, 4], "interval": 1}'::jsonb, 
 240, 10, true, true, 1),
(1, 'Weekly Vaccine Clinic - Afternoon', 'Standard afternoon vaccine clinic shift',
 '{"frequency": "weekly", "days": [2, 4], "interval": 1}'::jsonb,
 240, 8, true, true, 1),
(1, 'Weekend Emergency Response', 'Weekend on-call emergency response', 
 '{"frequency": "weekly", "days": [6, 0], "interval": 1}'::jsonb, 
 480, 5, false, true, 1),
(1, 'Monthly Training Session', 'Monthly volunteer training and updates',
 '{"frequency": "monthly", "interval": 1, "day_of_month": 15}'::jsonb,
 180, 30, false, false, 1);

-- Sample volunteer availability (for active volunteers)
INSERT INTO volunteer_availability (volunteer_id, start_date, end_date, availability_type, notes) VALUES
(1, '2025-11-01', '2025-12-31', 'general', 'Available weekends and evenings'),
(2, '2025-11-01', '2025-12-31', 'general', 'Flexible schedule'),
(3, '2025-11-01', '2025-12-31', 'general', 'Weekday evenings after 5pm'),
(4, '2025-11-15', '2025-12-31', 'general', 'Available most weekdays'),
(5, '2025-11-01', '2025-12-31', 'general', 'Weekend preferred'),
(7, '2025-11-01', '2025-12-31', 'general', 'Flexible, prefer weekdays'),
(8, '2025-11-01', '2025-12-31', 'general', 'Night shifts and weekends'),
(9, '2025-11-01', '2025-12-31', 'general', 'Weekday evenings only');

-- Sample waitlist entries (for full shifts)
INSERT INTO shift_waitlists (shift_id, volunteer_id, position, status, notes) VALUES
(1, 6, 1, 'waiting', 'Interested in morning shift'),
(1, 9, 2, 'waiting', 'Can provide pharmaceutical support'),
(2, 10, 1, 'waiting', 'Available for learning experience');

COMMENT ON TABLE shift_templates IS 'Templates for creating recurring shifts';
COMMENT ON TABLE shift_waitlists IS 'Waitlist queue for fully-booked shifts';
COMMENT ON TABLE volunteer_availability IS 'Volunteer availability calendar and preferences';
COMMENT ON TABLE shift_swap_requests IS 'Volunteer-initiated shift swap requests';

-- populates shift sign up page, non-tennanted
UPDATE shifts SET allow_self_signup = TRUE WHERE allow_self_signup = FALSE;