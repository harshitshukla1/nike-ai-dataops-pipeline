<div align="center">

# ⚡ Nike AI DataOps Command Center

### AI-Powered SLA Prediction • Nested JSON Pipeline • Telegram Alerts • English-to-SQL • FinOps Dashboard

<p>
  <a href="https://nike-ai-dataops-pipeline-npwpriqyrpwuagkdfqum6q.streamlit.app/">
    <img src="https://img.shields.io/badge/Live%20Demo-Streamlit-ff4b4b?style=for-the-badge&logo=streamlit&logoColor=white" />
  </a>
  <a href="https://github.com/harshitshukla1/nike-ai-dataops-pipeline">
    <img src="https://img.shields.io/badge/GitHub-Repository-181717?style=for-the-badge&logo=github" />
  </a>
  <img src="https://img.shields.io/badge/AI-Groq-00C7B7?style=for-the-badge" />
  <img src="https://img.shields.io/badge/Database-Neon%20PostgreSQL-00E599?style=for-the-badge" />
  <img src="https://img.shields.io/badge/Orchestration-Airflow-017CEE?style=for-the-badge&logo=apacheairflow&logoColor=white" />
</p>

<h3>Designed and Built by <b>Harshit Shukla</b></h3>

<p>
  <a href="https://github.com/harshitshukla1">GitHub Profile</a> •
  <a href="https://nike-ai-dataops-pipeline-npwpriqyrpwuagkdfqum6q.streamlit.app/">Live Project Demo</a>
</p>

</div>

---

## 🌐 Live Demo

> Open the hosted app directly. No local setup required.

### 🔗 Public Streamlit App

```text
https://nike-ai-dataops-pipeline-npwpriqyrpwuagkdfqum6q.streamlit.app/
📌 Project Summary
This project is a Nike-style AI-powered DataOps platform that predicts whether a daily inventory and fulfillment data pipeline will breach its SLA before heavy processing starts.

It simulates a real-world Data Engineering scenario where high traffic events such as SNKRS drops, weekend spikes, promo campaigns, and seasonal campaigns can suddenly increase data volume and delay business-critical dashboards.

The system uses:

Groq AI for SLA prediction
Telegram Bot API for real-time breach alerts
Nested JSON processing for realistic e-commerce event data
PostgreSQL / Neon as the warehouse
Streamlit as the hosted command center
English-to-SQL AI for natural language analytics
FinOps simulation for storage cleanup and cost awareness
Apache Airflow for orchestration design
🧠 Problem Statement
Nike-style global retail platforms run daily data pipelines to support:

inventory visibility
warehouse dispatch planning
fulfillment prioritization
product demand analysis
order and item-level reporting
The main pipeline must complete before business users start their morning operations.

Business SLA
Item	Value
Pipeline Name	nike_omni_inventory_etl
Start Time	3:00 AM
Deadline	7:00 AM
SLA Limit	240 minutes
Normal Runtime	150-180 minutes
Spike Runtime	240+ minutes
Why SLA Breach Happens
SLA risk increases when events like these happen:

limited sneaker drops
high SNKRS bot traffic
weekend traffic spikes
promo campaigns
seasonal launches
sudden order volume increase
If the pipeline breaches SLA, business teams may face:

delayed dashboards
late dispatch planning
warehouse bottlenecks
poor operational visibility
revenue-impacting fulfillment delays
✅ Solution
This project solves the problem by building an AI DataOps Command Center.

Before the heavy processing starts, the system:

generates or receives event metadata
checks historical runtime patterns
uses AI to predict SLA risk
classifies the run as SAFE or BREACH
sends Telegram alert if risk is high
recommends cluster scale-up
processes nested JSON data
loads clean data into PostgreSQL
exposes results in a hosted UI
allows users to ask questions using English-to-SQL
🏗️ End-to-End Architecture
mermaid

flowchart TD
    A[User Opens Hosted Streamlit App] --> B[Run New Nike Simulation]
    B --> C[Random Event Scenario Generator]

    C --> D{Event Type}
    D --> D1[STANDARD]
    D --> D2[PROMO]
    D --> D3[WEEKEND_SPIKE]
    D --> D4[SEASONAL_CAMPAIGN]
    D --> D5[SNKRS_DROP]

    D1 --> E[Groq AI SLA Predictor]
    D2 --> E
    D3 --> E
    D4 --> E
    D5 --> E

    E --> F{AI Prediction}

    F -->|SAFE| G[Normal Processing Status]
    F -->|BREACH| H[Telegram Alert + Scale-Up Recommendation]

    G --> I[Nested JSON Event Data]
    H --> I

    I --> J[JSON Flattening Layer]
    J --> K[Neon PostgreSQL Warehouse]

    K --> L[Streamlit Dashboard]
    K --> M[English-to-SQL AI Query Lab]
    K --> N[FinOps Monitor]
🧩 Core Features
Feature	Status	Description
Hosted Streamlit UI	✅	Public web dashboard
Groq AI SLA Predictor	✅	Predicts SAFE/BREACH
Telegram Alerts	✅	Sends alert on breach
Random Simulation	✅	Generates different event scenarios
Nested JSON Data	✅	Realistic e-commerce event format
JSON Flattening	✅	Converts nested events into relational tables
PostgreSQL Warehouse	✅	Stores orders, items, predictions, logs
Neon Cloud DB	✅	Hosted database for Streamlit
English-to-SQL	✅	Converts business questions into SQL
FinOps Tracking	✅	Tracks cleanup/cost simulation
Airflow DAG	✅	Local orchestration layer
CI/CD	✅	GitHub Actions validation
Project Blueprint Page	✅	Explains full system in UI
🤖 AI Implementation Layers
<details open> <summary><b>Layer 1: SLA Prediction AI</b></summary>
The system uses Groq LLM to predict whether the pipeline will breach SLA.

Input features include:

event type
footwear event volume
apparel event volume
total event count
bot traffic level
cluster node count
historical runtime pattern
Output:

JSON

{
  "prediction": "BREACH",
  "confidence": 85,
  "predicted_runtime_min": 250,
  "reason": "PROMO event type with 4.6M total events and Medium bot traffic poses SLA risk.",
  "suggested_cluster_nodes": 10,
  "remediation_action": "SCALE_CLUSTER",
  "model_name": "llama-3.1-8b-instant"
}
</details><details> <summary><b>Layer 2: English-to-SQL AI</b></summary>
The dashboard has an AI Query Lab where users can ask questions like:

text

show top 5 orders by order total amount
The AI converts it into PostgreSQL:

SQL

SELECT *
FROM warehouse.orders
ORDER BY order_total_amount DESC
LIMIT 5;
Safety rules:

only SELECT queries allowed
destructive SQL is blocked
results are shown directly in the UI
</details><details> <summary><b>Layer 3: Fallback Intelligence</b></summary>
If Groq API fails, the project uses a rule-based fallback predictor.

This prevents the platform from breaking if:

AI API quota is exhausted
model response is invalid
network call fails
</details><details> <summary><b>Layer 4: Alert Intelligence</b></summary>
Telegram alerts are sent only when the AI predicts a breach.

Example alert:

text

🚨 Nike DataOps SLA Alert
Prediction: BREACH
Confidence: 85%
Predicted Runtime: 250 min
Action: SCALE_CLUSTER
Reason: PROMO traffic may exceed SLA.
</details>
🔄 Workflow
<details open> <summary><b>Step-by-Step Runtime Flow</b></summary>
1. User clicks simulation button
The hosted Streamlit UI provides:

text

Run New AI Pipeline Simulation
2. Random scenario is generated
Possible scenarios:

STANDARD
PROMO
WEEKEND_SPIKE
SEASONAL_CAMPAIGN
SNKRS_DROP
3. AI predicts SLA status
The AI returns:

SAFE or BREACH
confidence score
predicted runtime
reason
remediation action
4. Alerting branch
If prediction is BREACH:

Telegram alert is sent
scale-up recommendation is shown
If prediction is SAFE:

no alert is sent
dashboard logs safe run
5. Data warehouse is updated
Prediction logs and simulated pipeline status are written to PostgreSQL.

6. Dashboard updates
The hosted UI shows:

latest AI predictions
file logs
warehouse counts
FinOps metrics
query results
</details>
📦 Nested JSON Data
The project uses nested JSON because real e-commerce APIs often send hierarchical data.

Example:

JSON

{
  "event_id": "evt_123",
  "event_type": "SNKRS_DROP",
  "customer": {
    "customer_id": "CUST-10001",
    "location": {
      "country": "US",
      "city": "Los Angeles"
    }
  },
  "order": {
    "order_id": "NK-20260615-000001",
    "items": [
      {
        "sku": "AJ1-TRAVIS-LOW",
        "product_name": "Travis Scott Air Jordan 1 Low",
        "category": "Footwear",
        "quantity": 1,
        "price": 180,
        "details": {
          "color": "Mocha",
          "size": "10 US"
        }
      }
    ]
  }
}
Flattened into:

warehouse.orders
warehouse.order_items
🗄️ Database Design
Schemas
Schema	Purpose
warehouse	Clean business tables
ai	AI prediction and query logs
observability	File and processing logs
finops	Cleanup and cost metrics
Important Tables
Table	Description
warehouse.etl_execution_history	Historical runtime and SLA data
warehouse.orders	Flattened order-level data
warehouse.order_items	Flattened item-level data
ai.ai_prediction_log	AI prediction history
observability.file_processing_log	File processing status
finops.cost_savings_log	Cleanup and cost saving log
finops.system_metrics_log	Request/cost telemetry
🖥️ Streamlit Pages
Page	Purpose
Command Center	Main KPI dashboard and simulation
AI Query Lab	English-to-SQL assistant
Pipeline Monitor	Orders, files and processing status
FinOps	Cleanup and storage-saving metrics
Project Blueprint	Full project explanation
⚙️ Tech Stack
Tool	Used For	Why
Streamlit	Hosted frontend	Fast public dashboard
Neon PostgreSQL	Cloud DB	Free hosted PostgreSQL
Groq	AI inference	Fast free LLM API
Telegram Bot API	Alerts	Free real-time notifications
Apache Airflow	Orchestration	Enterprise workflow design
Docker Compose	Local infra	Reproducible development
PostgreSQL	Warehouse	Relational analytics
Python	ETL and AI logic	Data engineering control layer
GitHub Actions	CI/CD	Automated validation
GitHub	Code hosting	Portfolio and version control
🚀 Hosted Demo Usage
Open:

text

https://nike-ai-dataops-pipeline-npwpriqyrpwuagkdfqum6q.streamlit.app/
Try:

Simulation
Click:

text

Run New AI Pipeline Simulation
Expected:

random event scenario
AI prediction
Telegram alert if breach
English-to-SQL
Ask:

text

show top 5 orders by order total amount
Expected:

SQL generated
result table shown
🧪 Local Development
Bash

git clone https://github.com/harshitshukla1/nike-ai-dataops-pipeline.git
cd nike-ai-dataops-pipeline

cp .env.example .env
echo "AIRFLOW_UID=$(id -u)" >> .env

docker compose up -d postgres
docker compose up airflow-init
docker compose up -d airflow-webserver airflow-scheduler
Run Airflow DAG test:

Bash

docker compose exec airflow-webserver airflow dags test nike_omni_inventory_ai_pipeline 2026-06-21
Run dashboard locally:

Bash

python -m streamlit run streamlit_app/app.py
🔐 Required Secrets
For hosted deployment, configure these in Streamlit Cloud Secrets:

toml

DATABASE_URL="your_neon_postgres_url"
GROQ_API_KEY="your_groq_key"
GROQ_MODEL="llama-3.1-8b-instant"
TELEGRAM_BOT_TOKEN="your_telegram_bot_token"
TELEGRAM_CHAT_ID="your_chat_id"
Never commit secrets to GitHub.

✅ CI/CD
GitHub Actions validates:

Python code compilation
Streamlit app import
SQL file presence
repository health on push and pull request
📈 Future Enhancements
AI Medic auto-healing for bad JSON
Real AWS S3 ingestion
PySpark cluster integration
Kafka/Kinesis streaming mode
dbt transformations
Great Expectations data quality
Slack alerting
advanced FinOps cost forecasting
👨‍💻 Engineer
Designed and built by:

text

Harshit Shukla
GitHub:

text

https://github.com/harshitshukla1
⚠️ Disclaimer
This is an educational portfolio project inspired by Nike-scale retail and e-commerce data engineering scenarios. It is not affiliated with Nike, Inc.





