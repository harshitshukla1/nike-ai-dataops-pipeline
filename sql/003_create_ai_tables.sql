
CREATE TABLE IF NOT EXISTS ai.ai_prediction_log (
    prediction_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    dag_run_id TEXT,
    run_date DATE,
    prompt_hash TEXT,
    prediction TEXT,
    confidence INT,
    predicted_runtime_min NUMERIC(10,2),
    reason TEXT,
    suggested_cluster_nodes INT,
    remediation_action TEXT,
    raw_response TEXT,
    model_name TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS ai.auto_healing_log (
    healing_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    dag_run_id TEXT,
    task_id TEXT,
    error_type TEXT,
    error_message TEXT,
    bad_data_sample_s3_path TEXT,
    ai_fix_summary TEXT,
    fix_code_hash TEXT,
    healing_status TEXT,
    attempt_number INT DEFAULT 1,
    started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    ended_at TIMESTAMP
);

CREATE TABLE IF NOT EXISTS ai.text_to_sql_query_log (
    query_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    user_question TEXT,
    generated_sql TEXT,
    execution_status TEXT,
    row_count INT,
    error_message TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
