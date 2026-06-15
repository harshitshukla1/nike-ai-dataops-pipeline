from __future__ import annotations

from datetime import datetime

from airflow import DAG
from airflow.operators.empty import EmptyOperator
from airflow.operators.python import PythonOperator


def check_environment() -> None:
    """Small smoke-test task to verify Airflow can run project DAGs."""
    print("Nike AI DataOps Airflow environment is working.")
    print("Next steps: DB schemas, mock Nike metadata, SLA predictor, and nested JSON pipeline.")


with DAG(
    dag_id="nike_omni_inventory_ai_pipeline",
    description="Nike AI-driven SLA prediction and self-healing DataOps pipeline",
    start_date=datetime(2026, 1, 1),
    schedule="0 3 * * *",
    catchup=False,
    tags=["nike", "ai", "dataops", "sla", "self-healing"],
) as dag:
    start = EmptyOperator(task_id="start")

    airflow_smoke_test = PythonOperator(
        task_id="airflow_smoke_test",
        python_callable=check_environment,
    )

    finish = EmptyOperator(task_id="finish")

    start >> airflow_smoke_test >> finish
