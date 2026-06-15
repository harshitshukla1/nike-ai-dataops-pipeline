
CREATE TABLE IF NOT EXISTS warehouse.etl_execution_history (
    id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    run_date DATE NOT NULL,
    dag_run_id TEXT,
    pipeline_name TEXT NOT NULL DEFAULT 'nike_omni_inventory_etl',
    event_type TEXT NOT NULL,
    footwear_events BIGINT NOT NULL DEFAULT 0,
    apparel_events BIGINT NOT NULL DEFAULT 0,
    total_events BIGINT NOT NULL DEFAULT 0,
    snkrs_bot_traffic TEXT NOT NULL DEFAULT 'Low',
    cluster_nodes INT NOT NULL DEFAULT 4,
    source_file_count INT NOT NULL DEFAULT 0,
    source_data_size_mb NUMERIC(12,2) NOT NULL DEFAULT 0,
    predicted_runtime_min NUMERIC(10,2),
    actual_runtime_min NUMERIC(10,2),
    sla_limit_min INT NOT NULL DEFAULT 240,
    sla_status TEXT,
    ai_prediction TEXT,
    ai_confidence INT,
    ai_reason TEXT,
    remediation_action TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS warehouse.orders (
    order_id TEXT PRIMARY KEY,
    event_id TEXT NOT NULL,
    event_timestamp TIMESTAMP,
    event_type TEXT,
    channel TEXT,
    customer_id TEXT,
    loyalty_tier TEXT,
    country TEXT,
    state TEXT,
    city TEXT,
    warehouse_id TEXT,
    dispatch_priority TEXT,
    payment_status TEXT,
    currency TEXT,
    order_total_amount NUMERIC(12,2),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS warehouse.order_items (
    order_item_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    order_id TEXT NOT NULL,
    sku TEXT,
    product_name TEXT,
    category TEXT,
    quantity INT,
    price NUMERIC(12,2),
    color TEXT,
    size TEXT,
    launch_type TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
