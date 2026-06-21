import json
import os

from src.db.connection import get_db_connection

SLA_LIMIT_MINUTES = 240
SCALED_CLUSTER_NODES = 10


def fetch_history_summary(event_type):
    sql = """
    SELECT COUNT(*) AS total_days,
           ROUND(AVG(actual_runtime_min), 2) AS avg_runtime,
           COALESCE(SUM(CASE WHEN sla_status = 'BREACHED' THEN 1 ELSE 0 END), 0) AS breached_days
    FROM warehouse.etl_execution_history
    WHERE event_type = %s;
    """
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(sql, (event_type,))
            row = cur.fetchone()
    return {
        "total_days": int(row[0] or 0),
        "avg_runtime": float(row[1] or 180),
        "breached_days": int(row[2] or 0),
    }


def log_prediction(run_date, result):
    sql = """
    INSERT INTO ai.ai_prediction_log (
        dag_run_id, run_date, prompt_hash, prediction, confidence,
        predicted_runtime_min, reason, suggested_cluster_nodes,
        remediation_action, raw_response, model_name
    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);
    """
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(sql, (
                f"manual_prediction__{run_date}",
                run_date,
                "ai_prompt_v2",
                result["prediction"],
                int(result["confidence"]),
                float(result["predicted_runtime_min"]),
                result["reason"],
                int(result["suggested_cluster_nodes"]),
                result["remediation_action"],
                json.dumps(result),
                result["model_name"],
            ))
        conn.commit()


def normalize_ai_result(data, model_name):
    data["prediction"] = str(data.get("prediction", "SAFE")).upper()
    data["remediation_action"] = str(data.get("remediation_action", "NONE")).upper()
    conf = float(data.get("confidence", 80))
    data["confidence"] = int(conf * 100) if conf <= 1 else int(conf)
    data["confidence"] = max(70, min(98, data["confidence"]))
    data["predicted_runtime_min"] = float(data.get("predicted_runtime_min", 180))
    data["suggested_cluster_nodes"] = int(data.get("suggested_cluster_nodes", 4))
    data["reason"] = str(data.get("reason", "AI generated SLA prediction."))
    data["model_name"] = model_name
    if data["predicted_runtime_min"] > SLA_LIMIT_MINUTES:
        data["prediction"] = "BREACH"
        data["remediation_action"] = "SCALE_CLUSTER"
        data["suggested_cluster_nodes"] = SCALED_CLUSTER_NODES
    return data


def groq_predict_sla(run_date, event_type, footwear_events, apparel_events, bot_traffic, cluster_nodes=4):
    api_key = os.getenv("GROQ_API_KEY")
    model_name = os.getenv("GROQ_MODEL", "llama-3.1-8b-instant")
    if not api_key:
        return None
    try:
        from groq import Groq
        history = fetch_history_summary(event_type)
        total_events = footwear_events + apparel_events
        prompt = f"""
You are a senior Nike Data Platform SLA prediction engine.
Return ONLY one valid JSON object. No markdown.

Required JSON schema:
{{"prediction":"SAFE or BREACH","confidence":85,"predicted_runtime_min":210,"reason":"specific one sentence","suggested_cluster_nodes":4,"remediation_action":"NONE or SCALE_CLUSTER","model_name":"{model_name}"}}

Business SLA:
- SLA limit = 240 minutes
- Default cluster = 4 nodes
- Scaled cluster = 10 nodes

Historical patterns:
- STANDARD low traffic: 150-180 min, usually SAFE
- PROMO/WEEKEND_SPIKE medium traffic: 205-240 min, borderline
- SEASONAL_CAMPAIGN > 6M events can breach
- SNKRS_DROP high bot traffic > 8M events usually breaches on 4 nodes

Today's metrics:
run_date={run_date}
event_type={event_type}
footwear_events={footwear_events}
apparel_events={apparel_events}
total_events={total_events}
bot_traffic={bot_traffic}
cluster_nodes={cluster_nodes}
historical_summary={history}

Decision rules:
If predicted_runtime_min > 240, use BREACH, SCALE_CLUSTER, 10 nodes.
If <= 240, use SAFE, NONE, 4 nodes.
Reason must mention event type, volume, bot traffic, and SLA risk/safety.
"""
        client = Groq(api_key=api_key)
        resp = client.chat.completions.create(
            model=model_name,
            messages=[
                {"role": "system", "content": "You output strict JSON only."},
                {"role": "user", "content": prompt},
            ],
            temperature=0.1,
        )
        text = resp.choices[0].message.content.strip()
        start = text.find("{")
        end = text.rfind("}")
        if start == -1 or end == -1:
            raise ValueError(text)
        data = json.loads(text[start:end + 1])
        result = normalize_ai_result(data, model_name)
        log_prediction(run_date, result)
        return result
    except Exception as exc:
        print(f"Groq prediction failed, falling back: {exc}")
        return None


def rule_based_prediction(run_date, event_type, footwear_events, apparel_events, bot_traffic, cluster_nodes=4):
    history = fetch_history_summary(event_type)
    total_events = footwear_events + apparel_events
    runtime = history["avg_runtime"]
    if event_type == "SNKRS_DROP":
        runtime += 75
    elif event_type == "SEASONAL_CAMPAIGN":
        runtime += 35
    elif event_type in ("PROMO", "WEEKEND_SPIKE"):
        runtime += 15
    if str(bot_traffic).lower() == "high":
        runtime += 35
    elif str(bot_traffic).lower() == "medium":
        runtime += 12
    if total_events > 8_000_000:
        runtime += 35
    elif total_events > 5_000_000:
        runtime += 20
    runtime = round(runtime, 2)
    if runtime > SLA_LIMIT_MINUTES:
        result = {
            "prediction": "BREACH",
            "confidence": 92,
            "predicted_runtime_min": runtime,
            "reason": f"{event_type} with {total_events:,} events and {bot_traffic} bot traffic is likely to exceed the 240 minute SLA.",
            "suggested_cluster_nodes": 10,
            "remediation_action": "SCALE_CLUSTER",
            "model_name": "rule_based_fallback",
        }
    else:
        result = {
            "prediction": "SAFE",
            "confidence": 82,
            "predicted_runtime_min": runtime,
            "reason": f"{event_type} volume and {bot_traffic} bot traffic are within historical safe processing range.",
            "suggested_cluster_nodes": 4,
            "remediation_action": "NONE",
            "model_name": "rule_based_fallback",
        }
    log_prediction(run_date, result)
    return result


def predict_sla(run_date, event_type, footwear_events, apparel_events, bot_traffic, cluster_nodes=4):
    result = groq_predict_sla(run_date, event_type, footwear_events, apparel_events, bot_traffic, cluster_nodes)
    if result:
        return result
    return rule_based_prediction(run_date, event_type, footwear_events, apparel_events, bot_traffic, cluster_nodes)


def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--run-date", default="2026-06-21")
    parser.add_argument("--event-type", default="SNKRS_DROP")
    parser.add_argument("--footwear-events", type=int, default=8500000)
    parser.add_argument("--apparel-events", type=int, default=900000)
    parser.add_argument("--bot-traffic", default="High")
    parser.add_argument("--cluster-nodes", type=int, default=4)
    args = parser.parse_args()
    print(json.dumps(predict_sla(args.run_date, args.event_type, args.footwear_events, args.apparel_events, args.bot_traffic, args.cluster_nodes), indent=2))


if __name__ == "__main__":
    main()
