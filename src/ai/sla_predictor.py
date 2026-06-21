import json
from src.db.connection import get_db_connection

SLA_LIMIT_MINUTES = 240
DEFAULT_CLUSTER_NODES = 4
SCALED_CLUSTER_NODES = 10


def fetch_history_summary(event_type):
    sql = """
    SELECT
        COUNT(*) AS total_days,
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


def groq_predict_sla(run_date, event_type, footwear_events, apparel_events, bot_traffic, cluster_nodes=4):
    import os, json
    api_key=os.getenv("GROQ_API_KEY")
    model_name=os.getenv("GROQ_MODEL","llama-3.1-8b-instant")
    if not api_key:
        return None
    try:
        from groq import Groq
        history=fetch_history_summary(event_type)
        total_events=footwear_events+apparel_events
        prompt=f"""
Return ONLY JSON:
{{"prediction":"SAFE or BREACH","confidence":80,"predicted_runtime_min":123,"reason":"short","suggested_cluster_nodes":4,"remediation_action":"NONE or SCALE_CLUSTER","model_name":"{model_name}"}}

Nike SLA limit 240 min.
Today: event_type={event_type}, footwear={footwear_events}, apparel={apparel_events}, total={total_events}, bot_traffic={bot_traffic}, cluster_nodes={cluster_nodes}
History: {history}
If runtime > 240 use BREACH and SCALE_CLUSTER with 10 nodes.
"""
        client=Groq(api_key=api_key)
        resp=client.chat.completions.create(
            model=model_name,
            messages=[{"role":"system","content":"You output strict JSON only."},{"role":"user","content":prompt}],
            temperature=0.1,
        )
        text=resp.choices[0].message.content.strip()
        start=text.find("{"); end=text.rfind("}")
        data=json.loads(text[start:end+1])
        data["prediction"]=str(data["prediction"]).upper()
        data["remediation_action"]=str(data["remediation_action"]).upper()
        data["confidence"]=float(data.get("confidence",80))
        data["confidence"]=int(data["confidence"]*100) if data["confidence"]<=1 else int(data["confidence"])
        data["predicted_runtime_min"]=float(data["predicted_runtime_min"])
        data["suggested_cluster_nodes"]=int(data["suggested_cluster_nodes"])
        data["model_name"]=model_name
        log_prediction(run_date,data)
        return data
    except Exception as exc:
        print(f"Groq prediction failed, falling back: {exc}")
        return None


def predict_sla(run_date, event_type, footwear_events, apparel_events, bot_traffic, cluster_nodes=4):
    groq_result = groq_predict_sla(run_date, event_type, footwear_events, apparel_events, bot_traffic, cluster_nodes)
    if groq_result:
        return groq_result

    history = fetch_history_summary(event_type)
    total_events = footwear_events + apparel_events
    total_millions = total_events / 1000000

    predicted_runtime = history["avg_runtime"]

    if event_type == "SNKRS_DROP":
        predicted_runtime += 40
    elif event_type == "SEASONAL_CAMPAIGN":
        predicted_runtime += 20
    elif event_type in ("PROMO", "WEEKEND_SPIKE"):
        predicted_runtime += 8

    if bot_traffic.upper() == "HIGH":
        predicted_runtime += 35
    elif bot_traffic.upper() == "MEDIUM":
        predicted_runtime += 12

    if total_millions > 8:
        predicted_runtime += 35
    elif total_millions > 5:
        predicted_runtime += 20
    elif total_millions > 3:
        predicted_runtime += 10

    if cluster_nodes >= SCALED_CLUSTER_NODES:
        predicted_runtime *= 0.65

    predicted_runtime = round(predicted_runtime, 2)

    if predicted_runtime > SLA_LIMIT_MINUTES:
        result = {
            "prediction": "BREACH",
            "confidence": 92 if event_type == "SNKRS_DROP" else 86,
            "predicted_runtime_min": predicted_runtime,
            "reason": f"{event_type} with {total_events:,} events and {bot_traffic} bot traffic is likely to exceed {SLA_LIMIT_MINUTES} minutes on {cluster_nodes} nodes.",
            "suggested_cluster_nodes": SCALED_CLUSTER_NODES,
            "remediation_action": "SCALE_CLUSTER",
            "model_name": "rule_based_ai_ready_predictor"
        }
    else:
        result = {
            "prediction": "SAFE",
            "confidence": 82,
            "predicted_runtime_min": predicted_runtime,
            "reason": f"{event_type} volume is within historical safe range for {cluster_nodes} nodes.",
            "suggested_cluster_nodes": cluster_nodes,
            "remediation_action": "NONE",
            "model_name": "rule_based_ai_ready_predictor"
        }

    log_prediction(run_date, result)
    return result


def log_prediction(run_date, result):
    sql = """
    INSERT INTO ai.ai_prediction_log (
        dag_run_id, run_date, prompt_hash, prediction, confidence,
        predicted_runtime_min, reason, suggested_cluster_nodes,
        remediation_action, raw_response, model_name
    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);
    """
    raw_response = json.dumps(result)
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(sql, (
                f"manual_prediction__{run_date}",
                run_date,
                "local_rule_based_prompt",
                result["prediction"],
                result["confidence"],
                result["predicted_runtime_min"],
                result["reason"],
                result["suggested_cluster_nodes"],
                result["remediation_action"],
                raw_response,
                result["model_name"],
            ))
        conn.commit()


def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--run-date", default="2026-06-15")
    parser.add_argument("--event-type", default="SNKRS_DROP")
    parser.add_argument("--footwear-events", type=int, default=8500000)
    parser.add_argument("--apparel-events", type=int, default=900000)
    parser.add_argument("--bot-traffic", default="High")
    parser.add_argument("--cluster-nodes", type=int, default=4)
    args = parser.parse_args()

    result = predict_sla(
        args.run_date, args.event_type, args.footwear_events,
        args.apparel_events, args.bot_traffic, args.cluster_nodes
    )
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
