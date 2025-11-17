-- Migration: Add validation fields for mandatory data flow
-- Ensures all data meets strict requirements

-- Add validation fields to citizen_feedback table
ALTER TABLE citizen_feedback
ADD COLUMN IF NOT EXISTS category_validated BOOLEAN DEFAULT FALSE,
ADD COLUMN IF NOT EXISTS pii_removed BOOLEAN DEFAULT FALSE,
ADD COLUMN IF NOT EXISTS category VARCHAR(50),
ADD COLUMN IF NOT EXISTS urgency VARCHAR(20) DEFAULT 'low',
ADD COLUMN IF NOT EXISTS source_validated BOOLEAN DEFAULT FALSE;

-- Add index for category validation
CREATE INDEX IF NOT EXISTS idx_citizen_feedback_category_validated 
ON citizen_feedback(category_validated, category);

-- Add index for urgency
CREATE INDEX IF NOT EXISTS idx_citizen_feedback_urgency 
ON citizen_feedback(urgency);

-- Update ai_summary_batches to support bilingual summaries
ALTER TABLE ai_summary_batches
ADD COLUMN IF NOT EXISTS summary_text_swahili TEXT,
ADD COLUMN IF NOT EXISTS key_points_swahili JSONB,
ADD COLUMN IF NOT EXISTS language VARCHAR(20) DEFAULT 'en';

-- Add constraint to ensure only valid categories
ALTER TABLE citizen_feedback
ADD CONSTRAINT check_valid_category 
CHECK (category IS NULL OR category IN (
    'healthcare',
    'education',
    'governance',
    'public_services',
    'infrastructure',
    'security'
));

-- Add constraint for urgency levels
ALTER TABLE citizen_feedback
ADD CONSTRAINT check_valid_urgency 
CHECK (urgency IN ('low', 'medium', 'high', 'critical'));

-- Add comment
COMMENT ON COLUMN citizen_feedback.category_validated IS 'MANDATORY: Must be true for data to be stored';
COMMENT ON COLUMN citizen_feedback.pii_removed IS 'MANDATORY: Must be true - all PII removed';
COMMENT ON COLUMN citizen_feedback.category IS 'MANDATORY: Must be one of 6 valid categories';
COMMENT ON COLUMN citizen_feedback.urgency IS 'Urgency level: low, medium, high, critical';

