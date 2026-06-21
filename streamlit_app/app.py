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
/* Cinematic animated starfield */
.stApp::before {
    content: "";
    position: fixed;
    inset: 0;
    z-index: -3;
    background-image:
      radial-gradient(2px 2px at 20px 30px, rgba(255,255,255,.9), transparent),
      radial-gradient(1px 1px at 90px 80px, rgba(125,211,252,.85), transparent),
      radial-gradient(1.5px 1.5px at 140px 150px, rgba(216,180,254,.85), transparent),
      radial-gradient(1px 1px at 220px 60px, rgba(255,255,255,.7), transparent);
    background-size: 260px 220px;
    animation: starDrift 28s linear infinite;
    opacity: .45;
}

.stApp::after {
    content: "";
    position: fixed;
    inset: -20%;
    z-index: -2;
    background:
      radial-gradient(circle at 20% 20%, rgba(14,165,233,.22), transparent 24%),
      radial-gradient(circle at 80% 10%, rgba(168,85,247,.20), transparent 24%),
      radial-gradient(circle at 50% 85%, rgba(34,197,94,.13), transparent 24%);
    filter: blur(35px);
    animation: oilFloat 16s ease-in-out infinite alternate;
}

@keyframes starDrift {
    from { transform: translate3d(0,0,0); }
    to { transform: translate3d(-260px,220px,0); }
}

@keyframes oilFloat {
    0% { transform: translate(-2%, -1%) scale(1); }
    50% { transform: translate(3%, 2%) scale(1.05); }
    100% { transform: translate(-1%, 4%) scale(1.02); }
}

@keyframes floatCard {
    0% { transform: translateY(0px); }
    50% { transform: translateY(-8px); }
    100% { transform: translateY(0px); }
}

@keyframes glowPulse {
    0% { box-shadow: 0 0 25px rgba(56,189,248,.18); }
    50% { box-shadow: 0 0 55px rgba(168,85,247,.28); }
    100% { box-shadow: 0 0 25px rgba(56,189,248,.18); }
}

.hero, .glass, .feature-card, div[data-testid="stMetric"] {
    animation: floatCard 7s ease-in-out infinite;
}

.hero {
    position: relative;
    overflow: hidden;
    animation: floatCard 8s ease-in-out infinite, glowPulse 5s ease-in-out infinite;
}

.hero::before {
    content: "";
    position: absolute;
    inset: -80px;
    background:
      radial-gradient(circle at 20% 20%, rgba(255,255,255,.18), transparent 20%),
      linear-gradient(120deg, transparent, rgba(255,255,255,.10), transparent);
    animation: shimmerMove 8s linear infinite;
}

@keyframes shimmerMove {
    0% { transform: translateX(-30%) rotate(0deg); }
    100% { transform: translateX(30%) rotate(8deg); }
}

/* Splash loading overlay */
.loader-screen {
    position: fixed;
    z-index: 999999;
    inset: 0;
    display: flex;
    align-items: center;
    justify-content: center;
    background:
      radial-gradient(circle at 20% 20%, rgba(56,189,248,.28), transparent 28%),
      radial-gradient(circle at 80% 30%, rgba(168,85,247,.25), transparent 30%),
      linear-gradient(135deg, #020617, #0f172a, #020617);
    animation: splashFade 2.6s ease forwards;
    pointer-events: none;
}

.loader-box {
    padding: 34px 46px;
    border-radius: 30px;
    background: rgba(255,255,255,.08);
    border: 1px solid rgba(255,255,255,.22);
    backdrop-filter: blur(22px);
    text-align: center;
    color: white;
    box-shadow: 0 20px 80px rgba(56,189,248,.20);
}

.loader-ring {
    width: 74px;
    height: 74px;
    margin: 0 auto 18px;
    border-radius: 50%;
    border: 4px solid rgba(255,255,255,.18);
    border-top-color: #38bdf8;
    border-right-color: #a855f7;
    animation: spin 1s linear infinite;
}

@keyframes spin { to { transform: rotate(360deg); } }

@keyframes splashFade {
    0% { opacity: 1; visibility: visible; }
    70% { opacity: 1; visibility: visible; }
    100% { opacity: 0; visibility: hidden; }
}

.neon-title {
    font-size: 56px;
    line-height: 1.05;
    font-weight: 900;
    background: linear-gradient(90deg, #38bdf8, #a855f7, #22c55e);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}

.arch-node {
    padding: 16px 18px;
    margin: 8px;
    border-radius: 18px;
    display: inline-block;
    background: rgba(15,23,42,.75);
    border: 1px solid rgba(56,189,248,.25);
    box-shadow: 0 12px 35px rgba(0,0,0,.25);
}
</style>

<div class="loader-screen">
  <div class="loader-box">
    <div class="loader-ring"></div>
    <h2>Booting Nike AI DataOps</h2>
    <p>Loading AI SLA Engine • Neon Warehouse • FinOps Console</p>
  </div>
</div>
""", unsafe_allow_html=True)

AUTO_REFRESH_SECONDS = 30

st.markdown("""
<style>
.stApp {
    background:
      radial-gradient(circle at 10% 10%, rgba(56,189,248,.18), transparent 25%),
      radial-gradient(circle at 90% 0%, rgba(168,85,247,.20), transparent 28%),
      linear-gradient(135deg, #020617 0%, #070b1f 50%, #020617 100%);
    color: #e5e7eb;
}
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, rgba(2,6,23,.98), rgba(15,23,42,.94));
    border-right: 1px solid rgba(148,163,184,.18);
}
.block-container { padding-top: 2rem; }
.glass {
    padding: 24px;
    border-radius: 26px;
    background: linear-gradient(135deg, rgba(255,255,255,.10), rgba(255,255,255,.04));
    border: 1px solid rgba(255,255,255,.20);
    box-shadow: 0 18px 55px rgba(0,0,0,.42);
    backdrop-filter: blur(20px);
}
.hero {
    padding: 34px;
    border-radius: 34px;
    background:
      linear-gradient(135deg, rgba(56,189,248,.25), rgba(168,85,247,.20), rgba(34,197,94,.14));
    border: 1px solid rgba(255,255,255,.24);
    box-shadow: 0 22px 70px rgba(56,189,248,.18);
}
.badge {
    display:inline-block;
    padding:8px 14px;
    margin:4px 6px 4px 0;
    border-radius:999px;
    background:rgba(34,197,94,.14);
    border:1px solid rgba(34,197,94,.35);
    color:#bbf7d0;
    font-weight:700;
}
.badge-blue {
    background:rgba(56,189,248,.14);
    border:1px solid rgba(56,189,248,.35);
    color:#bae6fd;
}
.badge-purple {
    background:rgba(168,85,247,.14);
    border:1px solid rgba(168,85,247,.35);
    color:#e9d5ff;
}
div[data-testid="stMetric"] {
    background: rgba(15,23,42,.72);
    border: 1px solid rgba(148,163,184,.25);
    padding: 18px;
    border-radius: 20px;
    box-shadow: 0 12px 30px rgba(0,0,0,.25);
}
h1, h2, h3 { color: #f8fafc !important; }
a { color:#38bdf8 !important; }

.floating-grid {
    display:grid;
    grid-template-columns: repeat(3, minmax(0,1fr));
    gap:18px;
    margin-top:18px;
}
.feature-card {
    padding:20px;
    border-radius:22px;
    background:rgba(15,23,42,.68);
    border:1px solid rgba(148,163,184,.22);
    box-shadow:0 12px 35px rgba(0,0,0,.28);
}
.small-muted { color:#94a3b8; font-size:14px; }
.footer {
    margin-top:35px;
    padding:20px;
    text-align:center;
    color:#94a3b8;
    border-top:1px solid rgba(148,163,184,.2);
}
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
    <meta http-equiv="refresh" content="30">
    <div class="hero">
      <div class="small-muted">Designed by Harshit Shukla • AI Data Engineering Portfolio</div>
      <div class="neon-title">⚡ Nike AI DataOps</div><h2>Command Center</h2>
      <p style="font-size:18px;line-height:1.7;">
        A futuristic AI-powered DataOps platform for Nike-scale omnichannel fulfillment pipelines.
        It predicts SLA breaches, triggers Telegram alerts, processes nested JSON events, tracks FinOps,
        and lets users query data using natural language.
      </p>
      <span class="badge">Live Hosted Demo</span>
      <span class="badge-blue">Groq AI</span>
      <span class="badge-purple">Neon PostgreSQL</span>
      <span class="badge">Telegram Alerts</span>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="floating-grid">
      <div class="feature-card">
        <h3>Problem</h3>
        <p>Nike SNKRS drops, promo campaigns and bot traffic can suddenly increase data volume, causing the morning inventory ETL to breach SLA.</p>
      </div>
      <div class="feature-card">
        <h3>Solution</h3>
        <p>AI predicts whether the pipeline is SAFE or BREACH before heavy processing starts and recommends scaling when needed.</p>
      </div>
      <div class="feature-card">
        <h3>Business Value</h3>
        <p>Supply-chain teams get early warnings, fewer dashboard delays, better dispatch planning and transparent DataOps visibility.</p>
      </div>
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
    st.markdown("""
    <div class="hero">
      <div class="small-muted">Designed by Harshit Shukla</div>
      <h1>🏗️ Project Blueprint</h1>
      <p style="font-size:18px;line-height:1.7;">
        Complete engineering story of the Nike AI DataOps platform: problem, architecture,
        workflow, AI layers, DataOps decisions and business impact.
      </p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="glass">
    <h2>1. Problem Statement</h2>
    <p>
    Nike-style omnichannel commerce pipelines process SNKRS app drops, Nike.com orders,
    retail sync data, bot traffic, inventory movement and fulfillment signals.
    On normal days the ETL pipeline finishes within SLA, but during limited sneaker drops,
    promo campaigns or high bot traffic, data volume spikes and the morning inventory dashboard
    can be delayed.
    </p>

    <h2>2. Business SLA</h2>
    <ul>
      <li>Pipeline: <b>nike_omni_inventory_etl</b></li>
      <li>Start time: <b>3:00 AM</b></li>
      <li>Deadline: <b>7:00 AM</b></li>
      <li>SLA limit: <b>240 minutes</b></li>
      <li>Impact of breach: delayed dashboard, dispatch delays, supply-chain planning risk.</li>
    </ul>

    <h2>3. What This Project Solves</h2>
    <p>
    The system predicts SLA risk before heavy processing starts. If the run is risky,
    it sends a Telegram alert and recommends scale-up. It also processes nested JSON
    order events, loads clean relational tables, tracks FinOps metrics and exposes
    everything in a hosted Streamlit command center.
    </p>

    <h2>4. Architecture</h2>
        <div>
          <span class="arch-node">Random Nike Events</span>
          <span class="arch-node">Groq AI Predictor</span>
          <span class="arch-node">Telegram Alert</span>
          <span class="arch-node">Nested JSON</span>
          <span class="arch-node">Neon PostgreSQL</span>
          <span class="arch-node">English-to-SQL</span>
        </div>
    <pre>
    Random Nike Event Simulation
          |
          v
    Groq AI SLA Predictor
          |
          |--- SAFE   -> standard processing
          |--- BREACH -> Telegram alert + scale-up recommendation
          |
          v
    Nested JSON Order Events
          |
          v
    Flattening Layer
          |
          v
    Neon PostgreSQL Warehouse
          |
          v
    Streamlit Command Center + English-to-SQL
    </pre>

    <h2>5. AI Implementation Levels</h2>
    <ol>
      <li><b>SLA Prediction AI:</b> Groq predicts SAFE/BREACH, runtime, confidence, reason and remediation.</li>
      <li><b>English-to-SQL AI:</b> Users ask questions in English and Groq generates safe PostgreSQL SELECT queries.</li>
      <li><b>Fallback Intelligence:</b> If AI fails, rule-based prediction keeps the system reliable.</li>
      <li><b>Alert Intelligence:</b> Telegram alert triggers only for predicted breach scenarios.</li>
    </ol>

    <h2>6. Data Engineering Features</h2>
    <ul>
      <li>Airflow orchestration for enterprise workflow design.</li>
      <li>Nested JSON generation and flattening.</li>
      <li>PostgreSQL warehouse tables for orders, order items, predictions, file logs and FinOps.</li>
      <li>Hosted Neon PostgreSQL for public Streamlit access.</li>
      <li>CI/CD validation with GitHub Actions.</li>
    </ul>

    <h2>7. FinOps and Cloud Health</h2>
    <p>
    The project tracks processed files, cleanup status, request-like operations and estimated
    storage savings. This demonstrates cost-aware engineering and free-tier friendly design.
    </p>

    <h2>8. Engineer</h2>
    <p>
      <b>Designed and built by Harshit Shukla</b><br/>
      GitHub: <a href="https://github.com/harshitshukla1" target="_blank">github.com/harshitshukla1</a>
    </p>
    </div>
    """, unsafe_allow_html=True)

st.markdown("""
<div class="footer">
Designed by Harshit Shukla • Nike AI DataOps Command Center • Built with Airflow, Groq, Neon, Telegram and Streamlit
</div>
""", unsafe_allow_html=True)
