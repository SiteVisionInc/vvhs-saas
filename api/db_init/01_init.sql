-- Initialize VVHS database with dummy tables and data

CREATE TABLE tenants (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    status VARCHAR(50) DEFAULT 'active',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    tenant_id INT REFERENCES tenants(id),
    username VARCHAR(100) UNIQUE NOT NULL,
    email VARCHAR(150) UNIQUE NOT NULL,
    hashed_password VARCHAR(200),
    role VARCHAR(50),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE volunteers (
    id SERIAL PRIMARY KEY,
    tenant_id INT REFERENCES tenants(id),
    user_id INT REFERENCES users(id),
    first_name VARCHAR(100),
    last_name VARCHAR(100),
    phone VARCHAR(30),
    city VARCHAR(100),
    skills TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE events (
    id SERIAL PRIMARY KEY,
    tenant_id INT REFERENCES tenants(id),
    name VARCHAR(200),
    location VARCHAR(200),
    event_date DATE,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Insert dummy tenants
INSERT INTO tenants (name) VALUES
('Virginia Department of Health'),
('Richmond MRC'),
('Fairfax County MRC');

-- Insert dummy users
INSERT INTO users (tenant_id, username, email, hashed_password, role)
VALUES
(1, 'admin_vdh', 'admin@vdh.virginia.gov', '$2y$10$kk54k/fT2pX1bh6reAzPqe.DlHDnjeJlZw5yVzIKrFhk5eDkueV9q', 'SystemAdmin'),
(2, 'coordinator_richmond', 'coord.richmond@vamrc.org', '$2y$10$kk54k/fT2pX1bh6reAzPqe.DlHDnjeJlZw5yVzIKrFhk5eDkueV9q', 'Coordinator'),
(3, 'volunteer_fairfax', 'volunteer@vamrc.org', '$2y$10$kk54k/fT2pX1bh6reAzPqe.DlHDnjeJlZw5yVzIKrFhk5eDkueV9q', 'Volunteer');

-- Insert dummy volunteers
INSERT INTO volunteers (tenant_id, user_id, first_name, last_name, phone, city, skills)
VALUES
(2, 2, 'Jane', 'Doe', '804-555-1111', 'Richmond', 'Logistics, Training'),
(3, 3, 'John', 'Smith', '703-555-2222', 'Fairfax', 'Medical Response');

-- Insert dummy events
INSERT INTO events (tenant_id, name, location, event_date, description)
VALUES
(2, 'Emergency Drill 2025', 'Richmond HQ', '2025-12-15', 'Statewide emergency preparedness drill'),
(3, 'Vaccination Outreach', 'Fairfax Clinic', '2025-11-20', 'Volunteer-led community vaccination event');



