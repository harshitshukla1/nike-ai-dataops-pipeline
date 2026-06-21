# Nike AI-Driven Self-Healing DataOps Pipeline

## Project Overview

This project is an enterprise-style Data Engineering and AI DataOps pipeline based on a Nike-scale omnichannel inventory and fulfillment scenario.

The pipeline predicts SLA breaches before heavy processing starts, processes deeply nested JSON data from AWS S3, flattens it using PySpark, loads clean data into AWS RDS PostgreSQL, auto-heals common data/schema failures using Gemini AI, cleans up S3 raw files after successful processing, and exposes everything through a Streamlit dashboard.

## Business Scenario

Nike daily omnichannel inventory pipeline processes SNKRS app events, e-commerce orders, footwear demand, apparel demand, bot traffic, warehouse dispatch signals, and fulfillment data.

The business dashboard must be ready every morning for supply-chain and logistics teams.

## SLA

- Pipeline name: nike_omni_inventory_etl
- Start time: 3:00 AM
- SLA deadline: 7:00 AM
- Max runtime: 240 minutes
- Normal runtime: 150-180 minutes
- Spike runtime during SNKRS drops: 300-380+ minutes

## Core Features

- Apache Airflow orchestration
- AWS S3 raw data lake
- AWS RDS PostgreSQL warehouse
- Deeply nested JSON ingestion
- PySpark JSON flattening
- Gemini AI SLA prediction
- AI-driven auto-healing
- Telegram alerting
- S3 auto-cleanup after successful processing
- Quarantine handling for failed files
- AWS free-tier request tracking
- FinOps dashboard
- Streamlit UI
- AI Text-to-SQL
- GitHub Actions CI/CD

## Tech Stack

| Area | Tool |
|---|---|
| Development | GitHub Codespaces |
| Containerization | Docker + Docker Compose |
| Orchestration | Apache Airflow |
| Data Lake | AWS S3 |
| Warehouse | AWS RDS PostgreSQL |
| Transformation | PySpark |
| AI | Google Gemini API |
| Dashboard | Streamlit |
| Alerting | Telegram Bot API |
| CI/CD | GitHub Actions |
| Testing | pytest |

## High-Level Flow

Nested JSON Generator -> AWS S3 Raw Zone -> Apache Airflow DAG -> PySpark Flattening -> AWS RDS PostgreSQL -> Streamlit DataOps Command Center

## Current Build Status

- [x] Project repository created
- [x] Folder structure created
- [x] Basic config files created
- [ ] Docker Compose Airflow setup
- [ ] Database schema creation
- [ ] Mock data generation
- [ ] Gemini SLA predictor
- [ ] Airflow DAG
- [ ] PySpark flattening
- [ ] Auto-healing
- [ ] Streamlit dashboard
- [ ] CI/CD


---

## Live Hosted Demo

Public Streamlit App:

https://nike-ai-dataops-pipeline-npwpriqyrpwuagkdfqum6q.streamlit.app/

## Final Project Capabilities

- Groq-powered AI SLA prediction
- Real-time random Nike event simulation
- SAFE/BREACH prediction paths
- Telegram alerting for breach scenarios
- Nested JSON event generation
- Nested JSON flattening into PostgreSQL warehouse
- Neon PostgreSQL hosted cloud database
- AI English-to-SQL query assistant
- FinOps cleanup and storage-saving simulation
- Futuristic Streamlit command center
- Project Blueprint documentation page
- GitHub Actions CI validation

## AI Implementation Layers

1. SLA Prediction AI: Groq classifies pipeline risk as SAFE or BREACH and returns runtime, confidence, reason, and remediation.
2. English-to-SQL AI: Groq converts natural language questions into safe PostgreSQL SELECT queries.
3. Fallback Intelligence: rule-based fallback keeps the app working if AI API fails.
4. Alert Intelligence: Telegram alert triggers only for predicted breach scenarios.

## Final Hosted Architecture

```text
User opens hosted Streamlit UI
        |
        v
Run random Nike simulation
        |
        v
Groq AI SLA Predictor
        |
        |--- SAFE   -> normal processing status
        |--- BREACH -> Telegram alert + scale-up recommendation
        |
        v
Neon PostgreSQL Cloud Warehouse
        |
        v
Futuristic dashboard + English-to-SQL + FinOps monitor
```

## Engineer

Built by Harshit Shukla  
GitHub: https://github.com/harshitshukla1
