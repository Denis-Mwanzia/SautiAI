-- Performance indexes for common queries
-- This migration adds indexes to improve query performance

-- Citizen feedback indexes
CREATE INDEX IF NOT EXISTS idx_feedback_created_at ON citizen_feedback(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_feedback_location ON citizen_feedback(location);
CREATE INDEX IF NOT EXISTS idx_feedback_source ON citizen_feedback(source);
CREATE INDEX IF NOT EXISTS idx_feedback_location_date ON citizen_feedback(location, created_at DESC);

-- Sentiment scores indexes
CREATE INDEX IF NOT EXISTS idx_sentiment_analyzed_at ON sentiment_scores(analyzed_at DESC);
CREATE INDEX IF NOT EXISTS idx_sentiment_sentiment ON sentiment_scores(sentiment);
CREATE INDEX IF NOT EXISTS idx_sentiment_date_sentiment ON sentiment_scores(analyzed_at DESC, sentiment);

-- Sector classification indexes
CREATE INDEX IF NOT EXISTS idx_sector_classified_at ON sector_classification(classified_at DESC);
CREATE INDEX IF NOT EXISTS idx_sector_primary ON sector_classification(primary_sector);

-- Alerts indexes
CREATE INDEX IF NOT EXISTS idx_alerts_created_at ON alerts(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_alerts_acknowledged ON alerts(acknowledged) WHERE acknowledged = false;
CREATE INDEX IF NOT EXISTS idx_alerts_severity ON alerts(severity);

-- Government responses indexes
CREATE INDEX IF NOT EXISTS idx_responses_created_at ON government_responses(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_responses_agency ON government_responses(responding_agency);

-- Agency performance indexes
CREATE INDEX IF NOT EXISTS idx_agency_perf_period ON agency_performance(period_start DESC);

