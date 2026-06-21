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

# ---------- FINAL FUTURISTIC UI FX ----------
st.markdown("""
<style>
/* Hide default Streamlit branding */
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}

/* Global cinematic cyber background */
.stApp {
    background:
      radial-gradient(circle at 15% 15%, rgba(0, 229, 255, 0.18), transparent 28%),
      radial-gradient(circle at 85% 10%, rgba(168, 85, 247, 0.22), transparent 30%),
      radial-gradient(circle at 50% 95%, rgba(34, 197, 94, 0.12), transparent 28%),
      linear-gradient(135deg, #020617 0%, #050816 40%, #020617 100%) !important;
    color: #e5e7eb !important;
}

/* Moving star field */
.stApp::before {
    content: "";
    position: fixed;
    inset: 0;
    z-index: -5;
    background-image:
      radial-gradient(1px 1px at 20px 30px, #ffffff, transparent),
      radial-gradient(1px 1px at 120px 80px, #38bdf8, transparent),
      radial-gradient(2px 2px at 180px 160px, #a855f7, transparent),
      radial-gradient(1px 1px at 260px 200px, #22c55e, transparent);
    background-size: 300px 260px;
    animation: starsMove 35s linear infinite;
    opacity: 0.45;
}
@keyframes starsMove {
    from { transform: translate(0,0); }
    to { transform: translate(-300px,260px); }
}

/* Liquid neon layer */
.stApp::after {
    content: "";
    position: fixed;
    inset: -25%;
    z-index: -4;
    background:
      radial-gradient(circle at 20% 30%, rgba(56,189,248,.22), transparent 26%),
      radial-gradient(circle at 80% 20%, rgba(168,85,247,.22), transparent 26%),
      radial-gradient(circle at 50% 80%, rgba(34,197,94,.15), transparent 26%);
    filter: blur(42px);
    animation: liquidMove 18s ease-in-out infinite alternate;
}
@keyframes liquidMove {
    0% { transform: translate(-2%, -2%) scale(1); }
    50% { transform: translate(3%, 2%) scale(1.05); }
    100% { transform: translate(-1%, 4%) scale(1.02); }
}

/* Sidebar premium */
[data-testid="stSidebar"] {
    background:
      linear-gradient(180deg, rgba(2,6,23,.98), rgba(15,23,42,.96)) !important;
    border-right: 1px solid rgba(56,189,248,.25);
    box-shadow: 12px 0 40px rgba(0,0,0,.35);
}
[data-testid="stSidebar"] * {
    color: #e5e7eb !important;
}

/* Main container */
.block-container {
    padding-top: 2rem;
    padding-bottom: 3rem;
}

/* Headings */
h1, h2, h3 {
    color: #f8fafc !important;
    letter-spacing: -0.03em;
}

/* Neon title */
.neon-title {
    font-size: clamp(42px, 5vw, 72px);
    line-height: 1.02;
    font-weight: 950;
    background: linear-gradient(90deg, #38bdf8, #a855f7, #22c55e, #38bdf8);
    background-size: 300% auto;
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    animation: neonFlow 5s linear infinite;
}
@keyframes neonFlow {
    to { background-position: 300% center; }
}

/* Hero card */
.hero {
    position: relative;
    overflow: hidden;
    padding: 38px !important;
    border-radius: 34px !important;
    background:
      linear-gradient(135deg, rgba(15,23,42,.70), rgba(30,41,59,.45)),
      radial-gradient(circle at 10% 10%, rgba(56,189,248,.28), transparent 35%),
      radial-gradient(circle at 90% 20%, rgba(168,85,247,.25), transparent 35%) !important;
    border: 1px solid rgba(255,255,255,.22) !important;
    box-shadow:
      0 24px 80px rgba(0,0,0,.45),
      0 0 80px rgba(56,189,248,.12);
    backdrop-filter: blur(22px);
    animation: cardFloat 7s ease-in-out infinite;
}
.hero::before {
    content: "";
    position: absolute;
    inset: -120px;
    background: linear-gradient(120deg, transparent, rgba(255,255,255,.16), transparent);
    transform: rotate(12deg);
    animation: shimmer 6s linear infinite;
}
@keyframes shimmer {
    from { transform: translateX(-40%) rotate(12deg); }
    to { transform: translateX(40%) rotate(12deg); }
}

/* Glass cards */
.glass, .feature-card, div[data-testid="stMetric"] {
    background: linear-gradient(135deg, rgba(255,255,255,.11), rgba(255,255,255,.045)) !important;
    border: 1px solid rgba(255,255,255,.20) !important;
    border-radius: 26px !important;
    box-shadow:
      0 18px 55px rgba(0,0,0,.38),
      inset 0 1px 0 rgba(255,255,255,.10);
    backdrop-filter: blur(22px);
    animation: cardFloat 8s ease-in-out infinite;
}
@keyframes cardFloat {
    0% { transform: translateY(0px); }
    50% { transform: translateY(-7px); }
    100% { transform: translateY(0px); }
}

/* Metric cards */
div[data-testid="stMetric"] {
    padding: 20px;
}
div[data-testid="stMetricValue"] {
    color: #38bdf8 !important;
    font-size: 34px !important;
    font-weight: 900 !important;
}
div[data-testid="stMetricLabel"] {
    color: #cbd5e1 !important;
    font-weight: 700 !important;
}

/* Buttons */
.stButton > button {
    border-radius: 999px !important;
    border: 1px solid rgba(56,189,248,.45) !important;
    background: linear-gradient(90deg, #0ea5e9, #8b5cf6, #22c55e) !important;
    color: white !important;
    font-weight: 900 !important;
    padding: 0.75rem 1.35rem !important;
    box-shadow: 0 14px 40px rgba(56,189,248,.22);
    transition: all .25s ease;
}
.stButton > button:hover {
    transform: translateY(-3px) scale(1.02);
    box-shadow: 0 20px 60px rgba(168,85,247,.32);
}

/* Badges */
.badge, .badge-blue, .badge-purple {
    display:inline-block;
    padding:8px 15px;
    margin:5px 7px 5px 0;
    border-radius:999px;
    font-weight:900;
    letter-spacing:.02em;
}
.badge {
    background:rgba(34,197,94,.15);
    border:1px solid rgba(34,197,94,.42);
    color:#bbf7d0;
}
.badge-blue {
    background:rgba(56,189,248,.16);
    border:1px solid rgba(56,189,248,.45);
    color:#bae6fd;
}
.badge-purple {
    background:rgba(168,85,247,.16);
    border:1px solid rgba(168,85,247,.45);
    color:#e9d5ff;
}

/* Dataframes */
[data-testid="stDataFrame"] {
    border-radius: 22px;
    overflow: hidden;
    border: 1px solid rgba(148,163,184,.22);
    box-shadow: 0 16px 45px rgba(0,0,0,.25);
}

/* Loading overlay */
.loader-screen {
    position: fixed;
    inset: 0;
    z-index: 999999;
    display: flex;
    align-items: center;
    justify-content: center;
    background:
      radial-gradient(circle at 20% 20%, rgba(56,189,248,.28), transparent 25%),
      radial-gradient(circle at 80% 20%, rgba(168,85,247,.28), transparent 25%),
      linear-gradient(135deg, #020617, #0f172a);
    animation: splashFade 2.2s ease forwards;
    pointer-events: none;
}
.loader-box {
    padding: 38px 52px;
    border-radius: 34px;
    background: rgba(255,255,255,.09);
    border: 1px solid rgba(255,255,255,.24);
    backdrop-filter: blur(24px);
    text-align: center;
    color: white;
    box-shadow: 0 22px 90px rgba(56,189,248,.22);
}
.loader-ring {
    width: 78px;
    height: 78px;
    margin: 0 auto 20px;
    border-radius: 50%;
    border: 5px solid rgba(255,255,255,.16);
    border-top-color: #38bdf8;
    border-right-color: #a855f7;
    animation: spin 1s linear infinite;
}
@keyframes spin { to { transform: rotate(360deg); } }
@keyframes splashFade {
    0%, 70% { opacity: 1; visibility: visible; }
    100% { opacity: 0; visibility: hidden; }
}

/* Footer */
.footer {
    margin-top: 40px;
    padding: 22px;
    text-align: center;
    color: #94a3b8;
    border-top: 1px solid rgba(148,163,184,.20);
}
</style>

<div class="loader-screen">
  <div class="loader-box">
    <div class="loader-ring"></div>
    <h2>Launching Nike AI DataOps</h2>
    <p>Initializing AI Predictor • Neon Warehouse • FinOps Console</p>
  </div>
</div>
""", unsafe_allow_html=True)
# ---------- END FINAL FUTURISTIC UI FX ----------



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

def log_finops_for_simulation(event_type, prediction):
    file_size_mb = random.choice([35, 48, 62, 80, 120])
    cleaned_mb = file_size_mb if prediction["prediction"] == "SAFE" else round(file_size_mb * 0.35, 2)
    estimated_saving = round((cleaned_mb / 1024) * 0.023, 6)

    with get_db_connection() as conn:
        with conn.cursor() as cur:
            # Simulated object storage requests
            for operation, count in [
                ("PUT", 1),
                ("GET", random.randint(2, 6)),
                ("DELETE", 1 if prediction["prediction"] == "SAFE" else 0),
                ("AI_CALL", 1),
                ("TELEGRAM", 1 if prediction["prediction"] == "BREACH" else 0),
            ]:
                cur.execute("""
                    INSERT INTO finops.system_metrics_log (
                        service_name,
                        operation_name,
                        request_count,
                        bytes_processed,
                        estimated_cost_usd,
                        free_tier_limit
                    ) VALUES (%s, %s, %s, %s, %s, %s);
                """, (
                    "HOSTED_SIMULATION",
                    operation,
                    count,
                    int(file_size_mb * 1024 * 1024),
                    estimated_saving if operation == "DELETE" else 0,
                    20000 if operation == "GET" else 2000
                ))

            cur.execute("""
                INSERT INTO finops.cost_savings_log (
                    dag_run_id,
                    file_path,
                    file_size_mb,
                    deleted_successfully,
                    estimated_storage_cost_saved_usd
                ) VALUES (%s, %s, %s, %s, %s);
            """, (
                "hosted_streamlit_simulation",
                f"simulated://nike/events/{event_type.lower()}_raw.jsonl",
                cleaned_mb,
                prediction["prediction"] == "SAFE",
                estimated_saving,
            ))

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

    log_finops_for_simulation(event_type, pred)
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


st.markdown("""
<div class="glass" style="margin-top:18px;">
  <span class="badge-blue">Hosted on Streamlit Cloud</span>
  <span class="badge-purple">Neon PostgreSQL Warehouse</span>
  <span class="badge">Groq AI Predictor</span>
  <span class="badge-blue">Telegram Live Alerts</span>
  <span class="badge-purple">English-to-SQL</span>
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
      <div class="small-muted">Designed by Harshit Shukla • AI/Data Engineering Portfolio</div>
      <div class="neon-title">🏗️ Project Blueprint</div>
      <p style="font-size:18px;line-height:1.8;">
        This page explains the complete end-to-end engineering story of the Nike AI DataOps platform:
        what problem it solves, how it works, which tools are used, where AI is implemented, and how
        data flows from raw events to business-ready insights.
      </p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="glass">
      <h2>1. Business Problem</h2>
      <p>
        Large e-commerce and retail brands like Nike depend on daily inventory and fulfillment dashboards.
        These dashboards are used by supply-chain managers, warehouse teams and logistics planners to decide
        how many products need to be dispatched, from which warehouse, and with what priority.
      </p>
      <p>
        The challenge is that traffic is not stable. During SNKRS drops, promo campaigns, weekend spikes,
        seasonal launches or bot-heavy traffic, data volume can suddenly increase. A pipeline that normally
        finishes within SLA can start taking much longer and delay the morning dashboard.
      </p>

      <h3>Business SLA</h3>
      <ul>
        <li><b>Pipeline:</b> nike_omni_inventory_etl</li>
        <li><b>Start time:</b> 3:00 AM</li>
        <li><b>Deadline:</b> 7:00 AM</li>
        <li><b>Maximum allowed runtime:</b> 240 minutes</li>
        <li><b>Business risk:</b> delayed dashboard, late dispatch decisions, poor warehouse planning.</li>
      </ul>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="glass">
      <h2>2. Solution Overview</h2>
      <p>
        This project builds an AI-powered DataOps system that predicts whether the pipeline will breach SLA
        before heavy processing starts. If the run looks risky, the system sends a Telegram alert and recommends
        scaling the processing cluster.
      </p>
      <p>
        The system also generates realistic nested JSON order events, flattens them into relational warehouse
        tables, tracks file processing, logs AI predictions, supports natural-language analytics through
        English-to-SQL, and shows everything in a hosted futuristic Streamlit dashboard.
      </p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="glass">
      <h2>3. End-to-End Architecture</h2>
      <pre>
      User opens hosted Streamlit UI
              |
              v
      Run New Nike Simulation
              |
              v
      Random event scenario generated
      STANDARD / PROMO / WEEKEND_SPIKE / SEASONAL_CAMPAIGN / SNKRS_DROP
              |
              v
      Groq AI SLA Predictor
              |
              |--- SAFE
              |      -> normal processing status
              |
              |--- BREACH
              |      -> Telegram alert
              |      -> scale-up recommendation
              |
              v
      Nested JSON order events
              |
              v
      Flattening layer
              |
              v
      Neon PostgreSQL warehouse
              |
              v
      Streamlit dashboard + English-to-SQL + FinOps monitor
      </pre>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="glass">
      <h2>4. Tech Stack and Why It Is Used</h2>
      <table>
        <tr><th>Tool</th><th>Purpose</th><th>Why Used</th></tr>
        <tr><td><b>Apache Airflow</b></td><td>Workflow orchestration</td><td>Shows enterprise-grade DAG orchestration, branching and pipeline control.</td></tr>
        <tr><td><b>Docker Compose</b></td><td>Local environment</td><td>Runs Airflow and Postgres consistently in Codespaces.</td></tr>
        <tr><td><b>PostgreSQL / Neon</b></td><td>Cloud data warehouse</td><td>Stores clean warehouse tables, AI logs, file logs and FinOps metrics.</td></tr>
        <tr><td><b>Groq AI</b></td><td>LLM inference</td><td>Predicts SLA risk and converts English questions to SQL.</td></tr>
        <tr><td><b>Telegram Bot API</b></td><td>Alerting</td><td>Sends real-time SLA breach alerts to the engineer/business user.</td></tr>
        <tr><td><b>Streamlit</b></td><td>Hosted UI</td><td>Provides public dashboard, AI Query Lab, FinOps and project documentation.</td></tr>
        <tr><td><b>GitHub Actions</b></td><td>CI/CD</td><td>Validates Python code and SQL files on push.</td></tr>
        <tr><td><b>Nested JSON</b></td><td>Source data format</td><td>Represents realistic API/e-commerce event payloads.</td></tr>
      </table>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="glass">
      <h2>5. Data Flow Explained</h2>
      <ol>
        <li><b>Scenario generation:</b> The app randomly creates a Nike-style event scenario such as STANDARD, PROMO or SNKRS_DROP.</li>
        <li><b>AI prediction:</b> Groq receives event volume, bot traffic and historical runtime pattern, then predicts SAFE or BREACH.</li>
        <li><b>Branching:</b> If SAFE, the system continues normally. If BREACH, Telegram alert is triggered and scale-up is recommended.</li>
        <li><b>Nested JSON:</b> Order events are represented as nested JSON with customer, session, fulfillment and item arrays.</li>
        <li><b>Flattening:</b> Nested JSON is converted into relational tables: orders and order_items.</li>
        <li><b>Warehouse load:</b> Clean data is stored in Neon PostgreSQL.</li>
        <li><b>Dashboard:</b> Streamlit reads from Neon and shows KPIs, predictions, files, FinOps and query results.</li>
      </ol>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="glass">
      <h2>6. AI Implementation Layers</h2>
      <h3>Layer 1: SLA Prediction AI</h3>
      <p>
        Groq predicts pipeline SLA status using event type, footwear events, apparel events, total volume,
        bot traffic, cluster size and historical runtime summary.
      </p>

      <h3>Layer 2: English-to-SQL AI</h3>
      <p>
        Users can ask questions like "show top 5 orders by order total amount". The AI converts it into
        safe PostgreSQL SELECT SQL and runs it on the warehouse.
      </p>

      <h3>Layer 3: Fallback Intelligence</h3>
      <p>
        If the AI API fails or returns invalid output, the system uses a deterministic rule-based fallback.
        This keeps the application reliable.
      </p>

      <h3>Layer 4: Alert Intelligence</h3>
      <p>
        Telegram alerting is triggered only for predicted breach scenarios, so users are not spammed for safe runs.
      </p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="glass">
      <h2>7. SAFE vs BREACH Behavior</h2>
      <h3>SAFE Run</h3>
      <ul>
        <li>Prediction: SAFE</li>
        <li>No Telegram alert</li>
        <li>Standard processing continues</li>
        <li>Dashboard logs prediction and status</li>
      </ul>

      <h3>BREACH Run</h3>
      <ul>
        <li>Prediction: BREACH</li>
        <li>Telegram alert is sent</li>
        <li>System recommends scale-up to 10 nodes</li>
        <li>Dashboard logs risk, reason and remediation action</li>
      </ul>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="glass">
      <h2>8. Data Model</h2>
      <p>The warehouse uses multiple schemas:</p>
      <ul>
        <li><b>warehouse:</b> execution history, orders, order_items</li>
        <li><b>ai:</b> AI prediction logs and text-to-SQL logs</li>
        <li><b>observability:</b> file processing and quarantine logs</li>
        <li><b>finops:</b> cleanup, request and cost-saving metrics</li>
      </ul>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="glass">
      <h2>9. FinOps and Free-Tier Design</h2>
      <p>
        The project is designed to run without paid infrastructure. It uses Streamlit Community Cloud,
        Neon PostgreSQL free tier, Groq free API, Telegram Bot API and GitHub Actions.
      </p>
      <p>
        The FinOps section demonstrates how a production system can track storage cleanup,
        request counts and estimated savings.
      </p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="glass">
      <h2>10. Engineering Outcome</h2>
      <p>
        This project demonstrates end-to-end Data Engineering, AI integration, DataOps monitoring,
        alerting, cloud deployment, SQL automation, and business storytelling in one hosted product.
      </p>
      <p>
        <b>Designed and built by Harshit Shukla</b><br/>
        GitHub: <a href="https://github.com/harshitshukla1" target="_blank">github.com/harshitshukla1</a>
      </p>
    </div>
    """, unsafe_allow_html=True)

st.markdown("""
<div class="footer">
  Nike AI DataOps Command Center • Designed by Harshit Shukla • Groq AI + Neon + Streamlit + Telegram
</div>
""", unsafe_allow_html=True)
