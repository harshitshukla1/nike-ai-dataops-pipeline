
CREATE TABLE IF NOT EXISTS finops.system_metrics_log (
    metric_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    metric_date DATE NOT NULL DEFAULT CURRENT_DATE,
    service_name TEXT NOT NULL,
    operation_name TEXT NOT NULL,
    request_count BIGINT NOT NULL DEFAULT 0,
    bytes_processed BIGINT NOT NULL DEFAULT 0,
    estimated_cost_usd NUMERIC(12,6) NOT NULL DEFAULT 0,
    free_tier_limit BIGINT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS finops.cost_savings_log (
    saving_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    dag_run_id TEXT,
    file_path TEXT,
    file_size_mb NUMERIC(12,2),
    deleted_successfully BOOLEAN DEFAULT FALSE,
    estimated_storage_cost_saved_usd NUMERIC(12,6) DEFAULT 0,
    deleted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
