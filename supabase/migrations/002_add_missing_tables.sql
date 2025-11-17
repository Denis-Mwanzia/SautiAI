-- Additional tables for new features

-- Priority Scores Table
CREATE TABLE IF NOT EXISTS priority_scores (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    feedback_id UUID NOT NULL REFERENCES citizen_feedback(id) ON DELETE CASCADE,
    priority_score DECIMAL(5,2) NOT NULL CHECK (priority_score >= 0 AND priority_score <= 100),
    priority_level VARCHAR(20) NOT NULL CHECK (priority_level IN ('low', 'medium', 'high', 'critical')),
    score_breakdown JSONB,
    calculated_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(feedback_id)
);

CREATE INDEX idx_priority_feedback ON priority_scores(feedback_id);
CREATE INDEX idx_priority_score ON priority_scores(priority_score DESC);
CREATE INDEX idx_priority_level ON priority_scores(priority_level);

-- Pulse Reports Table
CREATE TABLE IF NOT EXISTS pulse_reports (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    report_type VARCHAR(50) NOT NULL DEFAULT 'citizen_pulse',
    period VARCHAR(20) NOT NULL CHECK (period IN ('daily', 'weekly', 'monthly')),
    language VARCHAR(10) NOT NULL CHECK (language IN ('en', 'sw')),
    generated_at TIMESTAMPTZ DEFAULT NOW(),
    data JSONB NOT NULL,
    narrative TEXT NOT NULL,
    summaries JSONB,
    key_findings TEXT[],
    recommendations_summary TEXT,
    status VARCHAR(20) DEFAULT 'generated' CHECK (status IN ('generated', 'delivered', 'archived'))
);

CREATE INDEX idx_pulse_period ON pulse_reports(period);
CREATE INDEX idx_pulse_generated ON pulse_reports(generated_at DESC);
CREATE INDEX idx_pulse_type ON pulse_reports(report_type);

-- RLS Policies for new tables
ALTER TABLE priority_scores ENABLE ROW LEVEL SECURITY;
ALTER TABLE pulse_reports ENABLE ROW LEVEL SECURITY;

-- Allow service role to insert/select
CREATE POLICY "Service role can manage priority scores" ON priority_scores
    FOR ALL USING (auth.role() = 'service_role');

CREATE POLICY "Service role can manage pulse reports" ON pulse_reports
    FOR ALL USING (auth.role() = 'service_role');

-- Allow authenticated users to read
CREATE POLICY "Users can read priority scores" ON priority_scores
    FOR SELECT USING (auth.role() = 'authenticated');

CREATE POLICY "Users can read pulse reports" ON pulse_reports
    FOR SELECT USING (auth.role() = 'authenticated');

