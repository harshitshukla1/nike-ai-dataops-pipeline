import sys
from pathlib import Path

import pandas as pd
import streamlit as st

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from src.db.connection import get_db_connection

st.set_page_config(page_title="Nike DataOps Command Center", layout="wide")
st.title("Nike AI DataOps Command Center")
st.caption("AI SLA Prediction + Nested JSON Pipeline + FinOps Monitoring")

def query_df(sql):
    with get_db_connection() as conn:
        return pd.read_sql(sql, conn)

col1, col2, col3, col4 = st.columns(4)
orders = query_df("SELECT COUNT(*) AS count FROM warehouse.orders;")["count"][0]
items = query_df("SELECT COUNT(*) AS count FROM warehouse.order_items;")["count"][0]
preds = query_df("SELECT COUNT(*) AS count FROM ai.ai_prediction_log;")["count"][0]
files = query_df("SELECT COUNT(*) AS count FROM observability.file_processing_log;")["count"][0]
col1.metric("Orders Loaded", int(orders))
col2.metric("Order Items", int(items))
col3.metric("AI Predictions", int(preds))
col4.metric("Files Tracked", int(files))

st.subheader("Latest AI Predictions")
st.dataframe(query_df("""
SELECT prediction, confidence, predicted_runtime_min, remediation_action, model_name, created_at
FROM ai.ai_prediction_log
ORDER BY prediction_id DESC
LIMIT 10;
"""), use_container_width=True)

st.subheader("File Processing Status")
st.dataframe(query_df("""
SELECT file_id, s3_path, file_status, records_count, file_size_mb, processed_at
FROM observability.file_processing_log
ORDER BY file_id DESC
LIMIT 10;
"""), use_container_width=True)

st.subheader("FinOps Cleanup Savings")
st.dataframe(query_df("""
SELECT file_path, file_size_mb, deleted_successfully, estimated_storage_cost_saved_usd, deleted_at
FROM finops.cost_savings_log
ORDER BY saving_id DESC
LIMIT 10;
"""), use_container_width=True)

st.subheader("Runtime History by Event Type")
st.dataframe(query_df("""
SELECT event_type, sla_status, COUNT(*) AS days, ROUND(AVG(actual_runtime_min),2) AS avg_runtime
FROM warehouse.etl_execution_history
GROUP BY event_type, sla_status
ORDER BY event_type, sla_status;
"""), use_container_width=True)

st.subheader("AI English-to-SQL Query Assistant")
question = st.text_input("Ask your data in English", value="show top 5 orders by order total amount")

if st.button("Generate & Run SQL"):
    try:
        from src.ai.text_to_sql import english_to_sql
        sql = english_to_sql(question)
        st.code(sql, language="sql")
        st.dataframe(query_df(sql), use_container_width=True)
    except Exception as e:
        st.error(str(e))
