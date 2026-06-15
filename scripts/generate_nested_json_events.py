import argparse
import json
import random
import uuid
from datetime import datetime, timedelta
from pathlib import Path

from src.db.connection import get_db_connection

PRODUCTS = [
    {"sku": "AJ1-TRAVIS-LOW", "name": "Travis Scott Air Jordan 1 Low", "category": "Footwear", "price": 180.0, "launch_type": "Limited Drop"},
    {"sku": "DUNK-PANDA", "name": "Nike Dunk Low Panda", "category": "Footwear", "price": 115.0, "launch_type": "Standard"},
    {"sku": "PEGASUS-41", "name": "Nike Pegasus 41", "category": "Footwear", "price": 140.0, "launch_type": "Standard"},
    {"sku": "NIKE-PRO-TEE-BLK", "name": "Nike Pro Tee", "category": "Apparel", "price": 35.0, "launch_type": "Standard"},
    {"sku": "TECH-FLEECE-JOGGER", "name": "Nike Tech Fleece Jogger", "category": "Apparel", "price": 110.0, "launch_type": "Seasonal"},
]

CITIES = [
    ("US", "CA", "Los Angeles", "WH-LA-01"),
    ("US", "NY", "New York", "WH-NY-02"),
    ("IN", "KA", "Bengaluru", "WH-BLR-01"),
    ("IN", "DL", "Delhi", "WH-DEL-01"),
    ("GB", "LND", "London", "WH-LON-01"),
]


def random_size(category):
    if category == "Footwear":
        return random.choice(["7 US", "8 US", "9 US", "10 US", "11 US"])
    return random.choice(["S", "M", "L", "XL"])


def build_event(run_date, event_type, index, include_bad_record=False):
    country, state, city, warehouse = random.choice(CITIES)
    order_id = f"NK-{run_date.replace('-', '')}-{index:06d}"
    event_time = datetime.fromisoformat(run_date) + timedelta(minutes=random.randint(0, 180))

    if event_type == "SNKRS_DROP":
        channel = "SNKRS_APP"
        bot_score = round(random.uniform(0.75, 0.99), 2)
        dispatch_priority = "HIGH"
        item_count = random.choice([1, 1, 2])
    else:
        channel = random.choice(["NIKE_APP", "NIKE_DOT_COM", "RETAIL_SYNC"])
        bot_score = round(random.uniform(0.05, 0.45), 2)
        dispatch_priority = random.choice(["NORMAL", "NORMAL", "HIGH"])
        item_count = random.choice([1, 2, 3])

    items = []
    for _ in range(item_count):
        product = random.choice(PRODUCTS)
        item = {
            "sku": product["sku"],
            "product_name": product["name"],
            "category": product["category"],
            "quantity": random.randint(1, 3),
            "price": product["price"],
            "details": {
                "color": random.choice(["Black", "White", "Red", "Mocha", "Blue"]),
                "size": random_size(product["category"]),
                "launch_type": product["launch_type"],
            },
        }
        items.append(item)

    event = {
        "event_id": f"evt_{uuid.uuid4().hex}",
        "event_timestamp": event_time.isoformat(),
        "event_type": event_type,
        "channel": channel,
        "session": {
            "session_id": f"sess_{uuid.uuid4().hex[:12]}",
            "bot_score": bot_score,
            "device": {
                "type": random.choice(["mobile", "desktop", "tablet"]),
                "os": random.choice(["iOS", "Android", "Web"]),
                "app_version": random.choice(["6.20.1", "6.21.0", "6.22.0"]),
            },
        },
        "customer": {
            "customer_id": f"CUST-{random.randint(10000, 99999)}",
            "loyalty_tier": random.choice(["Bronze", "Silver", "Gold", "Platinum"]),
            "location": {
                "country": country,
                "state": state,
                "city": city,
            },
        },
        "order": {
            "order_id": order_id,
            "currency": "USD" if country in ["US", "GB"] else "INR",
            "payment_status": random.choice(["PAID", "PAID", "PAID", "PENDING"]),
            "items": items,
        },
        "fulfillment": {
            "warehouse_id": warehouse,
            "dispatch_priority": dispatch_priority,
            "estimated_dispatch_date": run_date,
        },
    }

    if include_bad_record:
        event["order"]["items"][0]["details"] = None
        event["order"]["items"][0]["quantity"] = "2 units"

    return event


def log_file(file_path, records_count, file_size_mb):
    s3_like_path = "local://" + str(file_path)
    sql = """
    INSERT INTO observability.file_processing_log
        (s3_path, file_size_mb, file_status, records_count)
    VALUES (%s, %s, 'NEW', %s);
    """
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(sql, (s3_like_path, file_size_mb, records_count))
        conn.commit()
    return s3_like_path


def main():
    parser = argparse.ArgumentParser(description="Generate Nike nested JSON mock events")
    parser.add_argument("--run-date", default="2026-06-15")
    parser.add_argument("--event-type", default="SNKRS_DROP")
    parser.add_argument("--records", type=int, default=50)
    parser.add_argument("--output-root", default="scripts/generated_data")
    parser.add_argument("--include-bad-record", action="store_true")
    args = parser.parse_args()

    random.seed(f"{args.run_date}-{args.event_type}-{args.records}")
    out_dir = Path(args.output_root) / "raw" / "nike" / "events" / f"dt={args.run_date}"
    out_dir.mkdir(parents=True, exist_ok=True)
    out_file = out_dir / f"nike_events_{args.run_date}_{args.event_type.lower()}.jsonl"

    with out_file.open("w", encoding="utf-8") as f:
        for i in range(1, args.records + 1):
            include_bad = args.include_bad_record and i == args.records
            event = build_event(args.run_date, args.event_type, i, include_bad_record=include_bad)
            f.write(json.dumps(event) + "\n")

    file_size_mb = round(out_file.stat().st_size / (1024 * 1024), 4)
    logged_path = log_file(out_file, args.records, file_size_mb)

    print("Nested JSON mock data generated successfully")
    print(f"Run date: {args.run_date}")
    print(f"Event type: {args.event_type}")
    print(f"Records: {args.records}")
    print(f"File: {out_file}")
    print(f"File size MB: {file_size_mb}")
    print(f"Logged path: {logged_path}")


if __name__ == "__main__":
    main()
