-- Crisis Detection Tables
-- For detecting policy-related crises for any policy, bill, or public issue

-- Crisis Signals Table
CREATE TABLE IF NOT EXISTS crisis_signals (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    signal_type VARCHAR(50) NOT NULL, -- 'sentiment_velocity', 'hashtag_trending', 'policy_crisis', 'protest_organizing', 'escalation_prediction'
    severity VARCHAR(20) NOT NULL CHECK (severity IN ('low', 'medium', 'high', 'critical')),
    title VARCHAR(255) NOT NULL,
    description TEXT,
    data JSONB, -- Stores signal-specific data
    recommendation TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    acknowledged BOOLEAN DEFAULT FALSE,
    acknowledged_at TIMESTAMPTZ,
    acknowledged_by UUID REFERENCES users(id)
);

CREATE INDEX IF NOT EXISTS idx_crisis_signals_type ON crisis_signals(signal_type);
CREATE INDEX IF NOT EXISTS idx_crisis_signals_severity ON crisis_signals(severity);
CREATE INDEX IF NOT EXISTS idx_crisis_signals_created ON crisis_signals(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_crisis_signals_acknowledged ON crisis_signals(acknowledged);

-- Government Alerts Table
CREATE TABLE IF NOT EXISTS government_alerts (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    crisis_signal_id UUID REFERENCES crisis_signals(id),
    signal_type VARCHAR(50),
    severity VARCHAR(20),
    stakeholders_notified TEXT[], -- Array of stakeholder IDs
    notification_status VARCHAR(20) DEFAULT 'pending', -- 'pending', 'success', 'failed'
    notified_at TIMESTAMPTZ DEFAULT NOW(),
    metadata JSONB,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_gov_alerts_signal ON government_alerts(crisis_signal_id);
CREATE INDEX IF NOT EXISTS idx_gov_alerts_status ON government_alerts(notification_status);
CREATE INDEX IF NOT EXISTS idx_gov_alerts_notified ON government_alerts(notified_at DESC);

-- Policy Monitoring Table
CREATE TABLE IF NOT EXISTS policy_monitoring (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    policy_name VARCHAR(255) NOT NULL,
    keywords TEXT[] NOT NULL,
    status VARCHAR(20) NOT NULL, -- 'no_data', 'low_risk', 'moderate_risk', 'high_risk', 'critical'
    total_mentions INTEGER DEFAULT 0,
    negative_sentiment_pct DECIMAL(5,2),
    sentiment_velocity JSONB,
    hashtag_intelligence JSONB,
    escalation_probability DECIMAL(5,2),
    recommendation TEXT,
    monitored_at TIMESTAMPTZ DEFAULT NOW(),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_policy_monitoring_name ON policy_monitoring(policy_name);
CREATE INDEX IF NOT EXISTS idx_policy_monitoring_status ON policy_monitoring(status);
CREATE INDEX IF NOT EXISTS idx_policy_monitoring_monitored ON policy_monitoring(monitored_at DESC);

-- Row Level Security (idempotent - safe to run multiple times)
-- Note: ALTER TABLE ... ENABLE ROW LEVEL SECURITY is idempotent in PostgreSQL
-- It won't error if RLS is already enabled
DO $$ 
BEGIN
    -- Enable RLS on tables if they exist (safe to run multiple times)
    IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'crisis_signals') THEN
        ALTER TABLE crisis_signals ENABLE ROW LEVEL SECURITY;
    END IF;
    
    IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'government_alerts') THEN
        ALTER TABLE government_alerts ENABLE ROW LEVEL SECURITY;
    END IF;
    
    IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'policy_monitoring') THEN
        ALTER TABLE policy_monitoring ENABLE ROW LEVEL SECURITY;
    END IF;
EXCEPTION
    WHEN OTHERS THEN
        -- Ignore errors if RLS is already enabled or table doesn't exist
        NULL;
END $$;

-- RLS Policies for crisis_signals (public read, admin write)
DROP POLICY IF EXISTS "Public can view crisis signals" ON crisis_signals;
CREATE POLICY "Public can view crisis signals" ON crisis_signals
    FOR SELECT USING (true);

DROP POLICY IF EXISTS "Service role can insert crisis signals" ON crisis_signals;
CREATE POLICY "Service role can insert crisis signals" ON crisis_signals
    FOR INSERT WITH CHECK (auth.role() = 'service_role');

-- RLS Policies for government_alerts (admin only)
DROP POLICY IF EXISTS "Admins can view government alerts" ON government_alerts;
CREATE POLICY "Admins can view government alerts" ON government_alerts
    FOR SELECT USING (auth.role() = 'service_role' OR EXISTS (
        SELECT 1 FROM users WHERE users.id = auth.uid() AND users.role = 'admin'
    ));

DROP POLICY IF EXISTS "Service role can insert government alerts" ON government_alerts;
CREATE POLICY "Service role can insert government alerts" ON government_alerts
    FOR INSERT WITH CHECK (auth.role() = 'service_role');

-- RLS Policies for policy_monitoring (public read)
DROP POLICY IF EXISTS "Public can view policy monitoring" ON policy_monitoring;
CREATE POLICY "Public can view policy monitoring" ON policy_monitoring
    FOR SELECT USING (true);

DROP POLICY IF EXISTS "Service role can insert policy monitoring" ON policy_monitoring;
CREATE POLICY "Service role can insert policy monitoring" ON policy_monitoring
    FOR INSERT WITH CHECK (auth.role() = 'service_role');

