import os
import random
import sys
from pathlib import Path

import pandas as pd
import streamlit as st

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from src.db.connection import get_db_connection
from src.ai.text_to_sql import english_to_sql
from src.ai.sla_predictor import predict_sla
from src.alerts.telegram import send_telegram_alert

def load_local_env():
    env_path = PROJECT_ROOT / ".env"
    if env_path.exists():
        for line in env_path.read_text().splitlines():
            if "=" in line and not line.strip().startswith("#"):
                k, v = line.split("=", 1)
                os.environ.setdefault(k, v)

load_local_env()

st.set_page_config(page_title="Nike AI DataOps", page_icon="⚡", layout="wide")

st.markdown("""
<style>
.stApp {
    background: radial-gradient(circle at top left, #1b1f3b 0%, #050816 35%, #02030a 100%);
    color: white;
}
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, rgba(15,23,42,.95), rgba(2,6,23,.95));
}
.glass {
    padding: 22px;
    border-radius: 24px;
    background: rgba(255,255,255,0.08);
    border: 1px solid rgba(255,255,255,0.18);
    box-shadow: 0 12px 40px rgba(0,0,0,0.35);
    backdrop-filter: blur(18px);
}
.hero {
    padding: 30px;
    border-radius: 30px;
    background: linear-gradient(135deg, rgba(56,189,248,.25), rgba(168,85,247,.20), rgba(34,197,94,.15));
    border: 1px solid rgba(255,255,255,.22);
    box-shadow: 0 20px 60px rgba(56,189,248,.15);
}
.metric-card {
    padding: 18px;
    border-radius: 20px;
    background: rgba(15,23,42,.78);
    border: 1px solid rgba(148,163,184,.28);
}
h1, h2, h3 { color: #f8fafc !important; }
</style>
""", unsafe_allow_html=True)

def query_df(sql):
    with get_db_connection() as conn:
        return pd.read_sql(sql, conn)

def exec_sql(sql, params=None):
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(sql, params or ())
        conn.commit()

def get_count(table):
    return int(query_df(f"SELECT COUNT(*) AS c FROM {table}")["c"][0])

def run_simulation():
    scenarios = [
        ("STANDARD", 1200000, 800000, "Low"),
        ("PROMO", 2800000, 1800000, "Medium"),
        ("WEEKEND_SPIKE", 3500000, 2300000, "Medium"),
        ("SEASONAL_CAMPAIGN", 4200000, 3600000, "Medium"),
        ("SNKRS_DROP", 8500000, 900000, "High"),
    ]
    event_type, footwear, apparel, bot = random.choice(scenarios)
    pred = predict_sla("2026-06-21", event_type, footwear, apparel, bot, 4)
    if pred["prediction"] == "BREACH":
        send_telegram_alert(
            f"🚨 Nike AI DataOps Hosted Alert\\nPrediction: {pred['prediction']}\\n"
            f"Runtime: {pred['predicted_runtime_min']} min\\nAction: {pred['remediation_action']}\\nReason: {pred['reason']}"
        )
    return event_type, pred

page = st.sidebar.radio(
    "⚡ Nike AI DataOps",
    ["Command Center", "AI Query Lab", "Pipeline Monitor", "FinOps", "Project Blueprint"],
)

st.sidebar.markdown("---")
st.sidebar.markdown("### Engineer")
st.sidebar.markdown("""
<div class="glass">
<b>Harshit Shukla</b><br/>
AI/Data Engineering Portfolio<br/><br/>
<a href="https://github.com/harshitshukla1" target="_blank">GitHub: harshitshukla1</a>
</div>
""", unsafe_allow_html=True)

if page == "Command Center":
    st.markdown("""
    <div class="hero">
      <h1>⚡ Nike AI DataOps Command Center</h1>
      <p>AI-powered SLA prediction, nested JSON processing, Telegram alerting, English-to-SQL and FinOps monitoring.</p>
    </div>
    """, unsafe_allow_html=True)

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Orders", get_count("warehouse.orders"))
    c2.metric("Items", get_count("warehouse.order_items"))
    c3.metric("AI Predictions", get_count("ai.ai_prediction_log"))
    c4.metric("Tracked Files", get_count("observability.file_processing_log"))

    st.markdown("### 🚀 Real-Time Simulation")
    if st.button("Run New AI Pipeline Simulation", type="primary"):
        event_type, pred = run_simulation()
        st.success(f"Scenario: {event_type} | Prediction: {pred['prediction']} | Model: {pred['model_name']}")
        st.json(pred)

    st.markdown("### Latest AI Predictions")
    st.dataframe(query_df("""
        SELECT prediction, confidence, predicted_runtime_min, remediation_action, model_name, created_at
        FROM ai.ai_prediction_log
        ORDER BY prediction_id DESC LIMIT 10
    """), use_container_width=True)

elif page == "AI Query Lab":
    st.title("🧠 AI English-to-SQL Lab")
    q = st.text_input("Ask your data", "show top 5 orders by order total amount")
    if st.button("Generate SQL + Run"):
        try:
            sql = english_to_sql(q)
            st.code(sql, language="sql")
            st.dataframe(query_df(sql), use_container_width=True)
        except Exception as e:
            st.error(e)

elif page == "Pipeline Monitor":
    st.title("📡 Pipeline Monitor")
    st.dataframe(query_df("""
        SELECT file_id, s3_path, file_status, records_count, file_size_mb, processed_at
        FROM observability.file_processing_log
        ORDER BY file_id DESC LIMIT 20
    """), use_container_width=True)
    st.dataframe(query_df("""
        SELECT order_id, event_type, channel, customer_id, city, warehouse_id, order_total_amount
        FROM warehouse.orders
        ORDER BY created_at DESC LIMIT 20
    """), use_container_width=True)

elif page == "FinOps":
    st.title("💰 Cloud Health & FinOps")
    st.dataframe(query_df("""
        SELECT service_name, operation_name, request_count, bytes_processed, estimated_cost_usd, created_at
        FROM finops.system_metrics_log
        ORDER BY metric_id DESC LIMIT 20
    """), use_container_width=True)
    st.dataframe(query_df("""
        SELECT file_path, file_size_mb, deleted_successfully, estimated_storage_cost_saved_usd, deleted_at
        FROM finops.cost_savings_log
        ORDER BY saving_id DESC LIMIT 20
    """), use_container_width=True)

elif page == "Project Blueprint":
    st.title("🏗️ Project Blueprint")
    st.markdown("""
    <div class="glass">
    <h2>Problem Statement</h2>
    <p>Nike-scale omnichannel pipelines can breach morning SLA during SNKRS drops, promotions, bot traffic spikes and seasonal campaigns.</p>
    <h2>Solution</h2>
    <p>An AI DataOps platform that predicts SLA risk, alerts via Telegram, simulates remediation, processes nested JSON, stores clean data in PostgreSQL and exposes a futuristic Streamlit command center.</p>
    <h2>Architecture</h2>
    <pre>
    Random Nike Scenario
        -> AI SLA Prediction (Groq)
        -> SAFE/BREACH Branch
        -> Telegram Alert on BREACH
        -> Nested JSON Generation
        -> JSON Flattening
        -> PostgreSQL Warehouse
        -> Streamlit Dashboard + English-to-SQL
    </pre>
    <h2>AI Implementation Levels</h2>
    <ul>
      <li>Groq AI SLA prediction</li>
      <li>Rule-based production fallback</li>
      <li>AI English-to-SQL query generation</li>
      <li>Gemini fallback-ready design</li>
    </ul>
    <h2>Engineering Features</h2>
    <ul>
      <li>Airflow orchestration</li>
      <li>PostgreSQL warehouse</li>
      <li>Nested JSON flattening</li>
      <li>Telegram alerting</li>
      <li>FinOps tracking</li>
      <li>Hosted Streamlit UI ready</li>
      <li>CI/CD ready</li>
    </ul>
    </div>
    """, unsafe_allow_html=True)
