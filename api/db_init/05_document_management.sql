-- Add to db_init/05_document_management.sql

-- Policy Documents Library
CREATE TABLE policy_documents (
    id SERIAL PRIMARY KEY,
    tenant_id INTEGER NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    
    -- Document info
    title VARCHAR(255) NOT NULL,
    description TEXT,
    document_type VARCHAR(100) NOT NULL, -- waiver, policy, guideline, etc.
    version VARCHAR(50) NOT NULL,
    
    -- File storage
    file_url VARCHAR(500) NOT NULL,
    file_size_bytes INTEGER,
    file_hash VARCHAR(255), -- SHA-256 for integrity
    
    -- Status
    is_active BOOLEAN DEFAULT TRUE,
    requires_signature BOOLEAN DEFAULT FALSE,
    
    -- Metadata
    created_by INTEGER REFERENCES users(id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    effective_date DATE,
    expiration_date DATE,
    
    -- Track superseded documents
    supersedes_document_id INTEGER REFERENCES policy_documents(id),
    
    CONSTRAINT unique_active_policy UNIQUE(tenant_id, document_type, version) WHERE is_active = TRUE
);

-- Electronic Signatures
CREATE TABLE electronic_signatures (
    id SERIAL PRIMARY KEY,
    
    -- Who signed
    volunteer_id INTEGER REFERENCES volunteers(id) ON DELETE CASCADE,
    user_id INTEGER REFERENCES users(id), -- Staff can also sign
    
    -- What was signed
    policy_document_id INTEGER REFERENCES policy_documents(id),
    custom_document_id INTEGER REFERENCES volunteer_documents(id), -- For uploaded docs
    
    -- Signature data
    signature_data TEXT, -- Base64 encoded signature image or typed name
    signature_method VARCHAR(50) NOT NULL, -- drawn, typed, click_through
    
    -- Legal requirements for non-repudiation
    ip_address VARCHAR(45) NOT NULL,
    user_agent TEXT,
    geolocation JSONB, -- {lat, lng, accuracy}
    timestamp TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    
    -- Consent acknowledgment
    consent_text TEXT NOT NULL, -- Exact text shown to signer
    acknowledged_terms BOOLEAN DEFAULT TRUE,
    
    -- Verification
    verified BOOLEAN DEFAULT FALSE,
    verification_method VARCHAR(100),
    verified_at TIMESTAMP,
    verified_by INTEGER REFERENCES users(id)
);

-- Volunteer Documents (enhanced)
CREATE TABLE volunteer_documents (
    id SERIAL PRIMARY KEY,
    volunteer_id INTEGER NOT NULL REFERENCES volunteers(id) ON DELETE CASCADE,
    tenant_id INTEGER NOT NULL REFERENCES tenants(id),
    
    -- Document classification
    document_type VARCHAR(100) NOT NULL, -- photo_id, license, certification, insurance, waiver
    document_category VARCHAR(100), -- identity, credential, legal
    title VARCHAR(255) NOT NULL,
    description TEXT,
    
    -- File storage
    file_url VARCHAR(500) NOT NULL,
    file_name VARCHAR(255),
    file_size_bytes INTEGER,
    file_type VARCHAR(50), -- pdf, jpg, png
    file_hash VARCHAR(255), -- SHA-256
    
    -- Expiration tracking
    issue_date DATE,
    expiration_date DATE,
    expires BOOLEAN DEFAULT FALSE,
    
    -- Verification workflow
    verification_status VARCHAR(50) DEFAULT 'pending', -- pending, approved, rejected, expired
    verified_by INTEGER REFERENCES users(id),
    verified_at TIMESTAMP,
    rejection_reason TEXT,
    
    -- Access control
    visibility VARCHAR(50) DEFAULT 'private', -- private, tenant_admins, public
    
    -- Notifications
    expiration_notified BOOLEAN DEFAULT FALSE,
    last_notification_date DATE,
    
    -- Metadata
    uploaded_by INTEGER REFERENCES users(id),
    uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Audit
    download_count INTEGER DEFAULT 0,
    last_accessed_at TIMESTAMP
);

-- Document Access Log (audit trail)
CREATE TABLE document_access_log (
    id BIGSERIAL PRIMARY KEY,
    
    -- What was accessed
    document_id INTEGER,
    document_type VARCHAR(100), -- policy_document, volunteer_document
    
    -- Who accessed
    user_id INTEGER REFERENCES users(id),
    volunteer_id INTEGER REFERENCES volunteers(id),
    
    -- How accessed
    action VARCHAR(50) NOT NULL, -- view, download, upload, delete, sign
    ip_address VARCHAR(45),
    user_agent TEXT,
    
    -- When
    accessed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Context
    metadata JSONB
);

-- Indexes
CREATE INDEX idx_policy_docs_tenant ON policy_documents(tenant_id, is_active);
CREATE INDEX idx_policy_docs_type ON policy_documents(document_type);
CREATE INDEX idx_signatures_volunteer ON electronic_signatures(volunteer_id);
CREATE INDEX idx_signatures_policy ON electronic_signatures(policy_document_id);
CREATE INDEX idx_volunteer_docs_volunteer ON volunteer_documents(volunteer_id);
CREATE INDEX idx_volunteer_docs_expiration ON volunteer_documents(expiration_date) WHERE expires = TRUE;
CREATE INDEX idx_volunteer_docs_status ON volunteer_documents(verification_status);
CREATE INDEX idx_doc_access_log ON document_access_log(document_type, document_id, accessed_at);

-- Permissions
GRANT ALL PRIVILEGES ON policy_documents TO vvhs;
GRANT ALL PRIVILEGES ON electronic_signatures TO vvhs;
GRANT ALL PRIVILEGES ON volunteer_documents TO vvhs;
GRANT ALL PRIVILEGES ON document_access_log TO vvhs;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO vvhs;