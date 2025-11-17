-- Sauti AI Database Schema
-- Production-ready schema for civic intelligence platform

-- Enable necessary extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm"; -- For text search

-- Citizen Feedback Table
CREATE TABLE IF NOT EXISTS citizen_feedback (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    source VARCHAR(50) NOT NULL,
    source_id VARCHAR(255) NOT NULL,
    text TEXT NOT NULL,
    language VARCHAR(10) NOT NULL CHECK (language IN ('en', 'sw', 'mixed', 'sheng')),
    author VARCHAR(255),
    location VARCHAR(255),
    timestamp TIMESTAMPTZ NOT NULL,
    raw_data JSONB,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(source, source_id)
);

-- Create index for faster queries
CREATE INDEX idx_feedback_source ON citizen_feedback(source);
CREATE INDEX idx_feedback_timestamp ON citizen_feedback(timestamp DESC);
CREATE INDEX idx_feedback_language ON citizen_feedback(language);
CREATE INDEX idx_feedback_location ON citizen_feedback(location);
CREATE INDEX idx_feedback_text_search ON citizen_feedback USING gin(to_tsvector('english', text));

-- Sentiment Scores Table
CREATE TABLE IF NOT EXISTS sentiment_scores (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    feedback_id UUID NOT NULL REFERENCES citizen_feedback(id) ON DELETE CASCADE,
    sentiment VARCHAR(20) NOT NULL CHECK (sentiment IN ('positive', 'negative', 'neutral')),
    confidence DECIMAL(3,2) NOT NULL CHECK (confidence >= 0 AND confidence <= 1),
    scores JSONB,
    analyzed_at TIMESTAMPTZ DEFAULT NOW(),
    model_used VARCHAR(100)
);

CREATE INDEX idx_sentiment_feedback ON sentiment_scores(feedback_id);
CREATE INDEX idx_sentiment_analyzed ON sentiment_scores(analyzed_at DESC);
CREATE INDEX idx_sentiment_type ON sentiment_scores(sentiment);

-- Sector Classification Table
CREATE TABLE IF NOT EXISTS sector_classification (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    feedback_id UUID NOT NULL REFERENCES citizen_feedback(id) ON DELETE CASCADE,
    primary_sector VARCHAR(50) NOT NULL CHECK (primary_sector IN (
        'health', 'education', 'transport', 'governance', 
        'corruption', 'infrastructure', 'economy', 'security', 'other'
    )),
    secondary_sectors VARCHAR(50)[],
    confidence DECIMAL(3,2) NOT NULL CHECK (confidence >= 0 AND confidence <= 1),
    classified_at TIMESTAMPTZ DEFAULT NOW(),
    model_used VARCHAR(100)
);

CREATE INDEX idx_sector_feedback ON sector_classification(feedback_id);
CREATE INDEX idx_sector_primary ON sector_classification(primary_sector);
CREATE INDEX idx_sector_classified ON sector_classification(classified_at DESC);

-- AI Summary Batches Table
CREATE TABLE IF NOT EXISTS ai_summary_batches (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    batch_id VARCHAR(255) NOT NULL,
    summary_text TEXT NOT NULL,
    key_points TEXT[],
    language VARCHAR(10) NOT NULL CHECK (language IN ('en', 'sw', 'mixed', 'sheng')),
    generated_at TIMESTAMPTZ DEFAULT NOW(),
    model_used VARCHAR(100),
    feedback_ids UUID[]
);

CREATE INDEX idx_summary_batch ON ai_summary_batches(batch_id);
CREATE INDEX idx_summary_generated ON ai_summary_batches(generated_at DESC);

-- Policy Recommendations Table
CREATE TABLE IF NOT EXISTS policy_recommendations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    sector VARCHAR(50) NOT NULL CHECK (sector IN (
        'health', 'education', 'transport', 'governance', 
        'corruption', 'infrastructure', 'economy', 'security', 'other'
    )),
    title VARCHAR(255) NOT NULL,
    description TEXT NOT NULL,
    rationale TEXT,
    priority VARCHAR(20) NOT NULL CHECK (priority IN ('low', 'medium', 'high', 'critical')),
    affected_counties VARCHAR(100)[],
    generated_at TIMESTAMPTZ DEFAULT NOW(),
    confidence DECIMAL(3,2) NOT NULL CHECK (confidence >= 0 AND confidence <= 1),
    model_used VARCHAR(100),
    status VARCHAR(20) DEFAULT 'pending' CHECK (status IN ('pending', 'reviewed', 'implemented', 'rejected'))
);

CREATE INDEX idx_recommendations_sector ON policy_recommendations(sector);
CREATE INDEX idx_recommendations_priority ON policy_recommendations(priority);
CREATE INDEX idx_recommendations_generated ON policy_recommendations(generated_at DESC);

-- Alerts Table
CREATE TABLE IF NOT EXISTS alerts (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    alert_type VARCHAR(50) NOT NULL,
    severity VARCHAR(20) NOT NULL CHECK (severity IN ('low', 'medium', 'high', 'critical')),
    title VARCHAR(255) NOT NULL,
    description TEXT NOT NULL,
    sector VARCHAR(50) CHECK (sector IN (
        'health', 'education', 'transport', 'governance', 
        'corruption', 'infrastructure', 'economy', 'security', 'other'
    )),
    affected_counties VARCHAR(100)[],
    metadata JSONB,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    acknowledged BOOLEAN DEFAULT FALSE,
    acknowledged_at TIMESTAMPTZ,
    acknowledged_by UUID
);

CREATE INDEX idx_alerts_severity ON alerts(severity);
CREATE INDEX idx_alerts_created ON alerts(created_at DESC);
CREATE INDEX idx_alerts_acknowledged ON alerts(acknowledged);
CREATE INDEX idx_alerts_sector ON alerts(sector);

-- Users Table (extends Supabase Auth)
CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,
    email VARCHAR(255) NOT NULL,
    full_name VARCHAR(255),
    role VARCHAR(50) DEFAULT 'user' CHECK (role IN ('user', 'admin', 'analyst')),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_role ON users(role);

-- Audit Logs Table
CREATE TABLE IF NOT EXISTS audit_logs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id) ON DELETE SET NULL,
    action VARCHAR(100) NOT NULL,
    resource_type VARCHAR(50),
    resource_id UUID,
    details JSONB,
    ip_address INET,
    user_agent TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_audit_user ON audit_logs(user_id);
CREATE INDEX idx_audit_action ON audit_logs(action);
CREATE INDEX idx_audit_created ON audit_logs(created_at DESC);
CREATE INDEX idx_audit_resource ON audit_logs(resource_type, resource_id);

-- Row Level Security (RLS) Policies

-- Enable RLS on all tables
ALTER TABLE citizen_feedback ENABLE ROW LEVEL SECURITY;
ALTER TABLE sentiment_scores ENABLE ROW LEVEL SECURITY;
ALTER TABLE sector_classification ENABLE ROW LEVEL SECURITY;
ALTER TABLE ai_summary_batches ENABLE ROW LEVEL SECURITY;
ALTER TABLE policy_recommendations ENABLE ROW LEVEL SECURITY;
ALTER TABLE alerts ENABLE ROW LEVEL SECURITY;
ALTER TABLE users ENABLE ROW LEVEL SECURITY;
ALTER TABLE audit_logs ENABLE ROW LEVEL SECURITY;

-- RLS Policies for citizen_feedback (public read, admin write)
CREATE POLICY "Public can view feedback" ON citizen_feedback
    FOR SELECT USING (true);

CREATE POLICY "Service role can insert feedback" ON citizen_feedback
    FOR INSERT WITH CHECK (auth.role() = 'service_role');

-- RLS Policies for sentiment_scores (public read)
CREATE POLICY "Public can view sentiment" ON sentiment_scores
    FOR SELECT USING (true);

-- RLS Policies for sector_classification (public read)
CREATE POLICY "Public can view sectors" ON sector_classification
    FOR SELECT USING (true);

-- RLS Policies for ai_summary_batches (public read)
CREATE POLICY "Public can view summaries" ON ai_summary_batches
    FOR SELECT USING (true);

-- RLS Policies for policy_recommendations (public read)
CREATE POLICY "Public can view recommendations" ON policy_recommendations
    FOR SELECT USING (true);

-- RLS Policies for alerts (public read)
CREATE POLICY "Public can view alerts" ON alerts
    FOR SELECT USING (true);

-- RLS Policies for users (users can view own profile)
CREATE POLICY "Users can view own profile" ON users
    FOR SELECT USING (auth.uid() = id);

-- RLS Policies for audit_logs (admin only)
CREATE POLICY "Admins can view audit logs" ON audit_logs
    FOR SELECT USING (
        EXISTS (
            SELECT 1 FROM users
            WHERE users.id = auth.uid() AND users.role = 'admin'
        )
    );

-- Functions for updated_at timestamps
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Triggers for updated_at
CREATE TRIGGER update_citizen_feedback_updated_at BEFORE UPDATE ON citizen_feedback
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

