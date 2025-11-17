-- Migration: Add Transparency and Government Response Tracking
-- Tracks government responsiveness to citizen concerns and alerts

-- Government Responses Table
CREATE TABLE IF NOT EXISTS government_responses (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    alert_id UUID REFERENCES alerts(id) ON DELETE SET NULL,
    feedback_id UUID REFERENCES citizen_feedback(id) ON DELETE SET NULL,
    issue_id UUID, -- Can reference alerts or feedback
    issue_type VARCHAR(50) NOT NULL CHECK (issue_type IN ('alert', 'feedback', 'trending_issue')),
    responding_agency VARCHAR(255) NOT NULL,
    response_text TEXT,
    response_date TIMESTAMPTZ NOT NULL,
    response_time_hours INTEGER, -- Time from issue creation to response
    status VARCHAR(50) NOT NULL DEFAULT 'pending' CHECK (status IN ('pending', 'acknowledged', 'in_progress', 'resolved', 'closed')),
    resolution_details TEXT,
    resolution_date TIMESTAMPTZ,
    affected_counties VARCHAR(100)[],
    sector VARCHAR(50),
    metadata JSONB,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_responses_alert ON government_responses(alert_id);
CREATE INDEX idx_responses_feedback ON government_responses(feedback_id);
CREATE INDEX idx_responses_agency ON government_responses(responding_agency);
CREATE INDEX idx_responses_status ON government_responses(status);
CREATE INDEX idx_responses_date ON government_responses(response_date DESC);
CREATE INDEX idx_responses_sector ON government_responses(sector);

-- Agency Performance Table
CREATE TABLE IF NOT EXISTS agency_performance (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    agency_name VARCHAR(255) NOT NULL,
    sector VARCHAR(50),
    total_issues INTEGER DEFAULT 0,
    acknowledged_count INTEGER DEFAULT 0,
    resolved_count INTEGER DEFAULT 0,
    average_response_time_hours DECIMAL(10,2),
    response_rate DECIMAL(5,2), -- Percentage
    resolution_rate DECIMAL(5,2), -- Percentage
    period_start TIMESTAMPTZ NOT NULL,
    period_end TIMESTAMPTZ NOT NULL,
    metadata JSONB,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(agency_name, sector, period_start, period_end)
);

CREATE INDEX idx_agency_name ON agency_performance(agency_name);
CREATE INDEX idx_agency_sector ON agency_performance(sector);
CREATE INDEX idx_agency_period ON agency_performance(period_start DESC);

-- Issue Resolution Tracking
ALTER TABLE alerts ADD COLUMN IF NOT EXISTS response_id UUID REFERENCES government_responses(id) ON DELETE SET NULL;
ALTER TABLE alerts ADD COLUMN IF NOT EXISTS resolution_status VARCHAR(50) DEFAULT 'unresolved' CHECK (resolution_status IN ('unresolved', 'acknowledged', 'in_progress', 'resolved', 'closed'));
ALTER TABLE alerts ADD COLUMN IF NOT EXISTS resolution_date TIMESTAMPTZ;
ALTER TABLE alerts ADD COLUMN IF NOT EXISTS resolution_notes TEXT;

-- Add response tracking to citizen_feedback
ALTER TABLE citizen_feedback ADD COLUMN IF NOT EXISTS response_id UUID REFERENCES government_responses(id) ON DELETE SET NULL;
ALTER TABLE citizen_feedback ADD COLUMN IF NOT EXISTS response_status VARCHAR(50) DEFAULT 'pending' CHECK (response_status IN ('pending', 'acknowledged', 'in_progress', 'resolved', 'closed'));

-- RLS Policies
ALTER TABLE government_responses ENABLE ROW LEVEL SECURITY;
ALTER TABLE agency_performance ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Public can view government responses" ON government_responses
    FOR SELECT USING (true);

CREATE POLICY "Service role can manage responses" ON government_responses
    FOR ALL USING (auth.role() = 'service_role');

CREATE POLICY "Public can view agency performance" ON agency_performance
    FOR SELECT USING (true);

CREATE POLICY "Service role can manage agency performance" ON agency_performance
    FOR ALL USING (auth.role() = 'service_role');

-- Comments
COMMENT ON TABLE government_responses IS 'Tracks government agency responses to citizen concerns and alerts - supports transparency metrics';
COMMENT ON TABLE agency_performance IS 'Aggregated performance metrics for government agencies - tracks responsiveness and accountability';
COMMENT ON COLUMN government_responses.response_time_hours IS 'Time from issue creation to government response - key transparency metric';
COMMENT ON COLUMN agency_performance.response_rate IS 'Percentage of issues acknowledged by agency - transparency indicator';

