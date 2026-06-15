
CREATE TABLE IF NOT EXISTS observability.file_processing_log (
    file_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    s3_path TEXT NOT NULL,
    file_size_mb NUMERIC(12,2) DEFAULT 0,
    file_status TEXT NOT NULL DEFAULT 'NEW',
    records_count BIGINT DEFAULT 0,
    error_message TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    processed_at TIMESTAMP
);

CREATE TABLE IF NOT EXISTS observability.quarantine_log (
    quarantine_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    original_s3_path TEXT,
    quarantine_s3_path TEXT,
    failure_reason TEXT,
    healing_attempts INT DEFAULT 0,
    manual_action_required BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
