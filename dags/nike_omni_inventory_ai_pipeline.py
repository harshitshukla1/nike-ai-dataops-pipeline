from datetime import datetime
from pprint import pformat

from airflow import DAG
from airflow.operators.empty import EmptyOperator
from airflow.operators.python import BranchPythonOperator, PythonOperator
from airflow.utils.trigger_rule import TriggerRule

from src.ai.sla_predictor import predict_sla


def get_today_source_metrics(**context):
    metrics = {
        "run_date": "2026-06-15",
        "event_type": "SNKRS_DROP",
        "footwear_events": 8500000,
        "apparel_events": 900000,
        "bot_traffic": "High",
        "cluster_nodes": 4,
    }
    print("TODAY METRICS")
    print(pformat(metrics))
    return metrics


def ai_sla_predictor(**context):
    m = context["ti"].xcom_pull(task_ids="get_today_source_metrics")
    result = predict_sla(
        m["run_date"], m["event_type"], m["footwear_events"],
        m["apparel_events"], m["bot_traffic"], m["cluster_nodes"]
    )
    print("AI SLA PREDICTION")
    print(pformat(result))
    return result


def branch_on_prediction(**context):
    result = context["ti"].xcom_pull(task_ids="ai_sla_predictor")
    if result["prediction"] == "BREACH":
        return "send_breach_alert"
    return "standard_processing"


def send_breach_alert(**context):
    result = context["ti"].xcom_pull(task_ids="ai_sla_predictor")
    print("CRITICAL: Nike ETL may breach SLA")
    print(pformat(result))
    print("Telegram alert integration will be added later.")


def simulate_cluster_scale_up(**context):
    result = context["ti"].xcom_pull(task_ids="ai_sla_predictor")
    print(f"Scaling simulation: 4 nodes -> {result['suggested_cluster_nodes']} nodes")


def standard_processing(**context):
    print("SAFE path: running standard ETL processing.")


def process_data_simulation(**context):
    result = context["ti"].xcom_pull(task_ids="ai_sla_predictor")
    if result["prediction"] == "BREACH":
        final = {"simulated_runtime_min": 225, "sla_status": "SAVED_BY_AUTOSCALE"}
    else:
        final = {"simulated_runtime_min": result["predicted_runtime_min"], "sla_status": "MET"}
    print("PROCESSING SIMULATION RESULT")
    print(pformat(final))
    return final


def log_runtime_summary(**context):
    pred = context["ti"].xcom_pull(task_ids="ai_sla_predictor")
    final = context["ti"].xcom_pull(task_ids="process_data_simulation")
    print("FINAL SUMMARY")
    print(pformat({"prediction": pred, "processing_result": final}))


with DAG(
    dag_id="nike_omni_inventory_ai_pipeline",
    description="Nike AI SLA prediction and remediation pipeline",
    start_date=datetime(2026, 1, 1),
    schedule="0 3 * * *",
    catchup=False,
    tags=["nike", "ai", "sla"],
) as dag:
    start = EmptyOperator(task_id="start")
    get_metrics = PythonOperator(task_id="get_today_source_metrics", python_callable=get_today_source_metrics)
    predictor = PythonOperator(task_id="ai_sla_predictor", python_callable=ai_sla_predictor)
    branch = BranchPythonOperator(task_id="branch_on_prediction", python_callable=branch_on_prediction)
    alert = PythonOperator(task_id="send_breach_alert", python_callable=send_breach_alert)
    scale = PythonOperator(task_id="simulate_cluster_scale_up", python_callable=simulate_cluster_scale_up)
    standard = PythonOperator(task_id="standard_processing", python_callable=standard_processing)
    join = EmptyOperator(task_id="join_processing_paths", trigger_rule=TriggerRule.NONE_FAILED_MIN_ONE_SUCCESS)
    process = PythonOperator(task_id="process_data_simulation", python_callable=process_data_simulation)
    log_summary = PythonOperator(task_id="log_runtime_summary", python_callable=log_runtime_summary)
    finish = EmptyOperator(task_id="finish")

    start >> get_metrics >> predictor >> branch
    branch >> standard >> join
    branch >> alert >> scale >> join
    join >> process >> log_summary >> finish
