import json
import os
import re

from groq import Groq
from src.db.connection import get_db_connection

SCHEMA = """
Tables:
warehouse.etl_execution_history(run_date,event_type,footwear_events,apparel_events,total_events,snkrs_bot_traffic,cluster_nodes,actual_runtime_min,sla_status,ai_prediction,ai_confidence,remediation_action)
warehouse.orders(order_id,event_id,event_timestamp,event_type,channel,customer_id,loyalty_tier,country,state,city,warehouse_id,dispatch_priority,payment_status,currency,order_total_amount)
warehouse.order_items(order_id,sku,product_name,category,quantity,price,color,size,launch_type)
ai.ai_prediction_log(prediction,confidence,predicted_runtime_min,reason,suggested_cluster_nodes,remediation_action,model_name,created_at)
finops.cost_savings_log(file_path,file_size_mb,deleted_successfully,estimated_storage_cost_saved_usd,deleted_at)
observability.file_processing_log(s3_path,file_status,records_count,file_size_mb,processed_at)
"""

BLOCKED = ["drop ", "delete ", "update ", "insert ", "alter ", "truncate ", "create ", "grant ", "revoke "]


def validate_sql(sql: str) -> str:
    s = sql.strip().strip(";")
    low = s.lower()
    if not low.startswith("select"):
        raise ValueError("Only SELECT queries are allowed")
    if any(b in low for b in BLOCKED):
        raise ValueError("Unsafe SQL keyword detected")
    if " limit " not in low:
        s += " LIMIT 100"
    return s + ";"


def english_to_sql(question: str) -> str:
    client = Groq(api_key=os.getenv("GROQ_API_KEY"))
    model = os.getenv("GROQ_MODEL", "llama-3.1-8b-instant")
    prompt = f"""
Convert the English question to PostgreSQL SELECT SQL only. If user asks about SLA predictions, AI predictions, predicted runtime, confidence, or remediation, use ai.ai_prediction_log.
Return JSON only: {{"sql":"SELECT ..."}}

Schema:
{SCHEMA}

Question: {question}
"""
    resp = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": "You generate safe PostgreSQL SELECT SQL only."},
            {"role": "user", "content": prompt},
        ],
        temperature=0,
    )
    text = resp.choices[0].message.content.strip()
    start = text.find("{")
    end = text.rfind("}")
    data = json.loads(text[start:end + 1])
    return validate_sql(data["sql"])


def run_text_to_sql(question: str):
    sql = english_to_sql(question)
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(sql)
            cols = [d[0] for d in cur.description]
            rows = cur.fetchall()
    return sql, cols, rows


if __name__ == "__main__":
    import sys
    q = " ".join(sys.argv[1:]) or "Show latest 5 SLA predictions"
    sql, cols, rows = run_text_to_sql(q)
    print(sql)
    print(cols)
    for r in rows:
        print(r)
