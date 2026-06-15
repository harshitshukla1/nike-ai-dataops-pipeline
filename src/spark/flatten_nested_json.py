import argparse
import json
import re
from pathlib import Path

from src.db.connection import get_db_connection


def safe_get(dictionary, path, default=None):
    current = dictionary
    for key in path.split('.'):
        if not isinstance(current, dict):
            return default
        current = current.get(key)
        if current is None:
            return default
    return current


def parse_quantity(value):
    if value is None:
        return 0
    if isinstance(value, int):
        return value
    match = re.search(r"\d+", str(value))
    return int(match.group(0)) if match else 0


def flatten_event(event):
    items = safe_get(event, 'order.items', [])
    if isinstance(items, dict):
        items = [items]
    if not isinstance(items, list):
        items = []

    order_id = safe_get(event, 'order.order_id')
    order_total = 0.0
    item_rows = []

    for item in items:
        details = item.get('details') if isinstance(item, dict) else {}
        if not isinstance(details, dict):
            details = {}

        quantity = parse_quantity(item.get('quantity')) if isinstance(item, dict) else 0
        price = float(item.get('price') or 0) if isinstance(item, dict) else 0.0
        order_total += quantity * price

        item_rows.append({
            'order_id': order_id,
            'sku': item.get('sku') if isinstance(item, dict) else None,
            'product_name': item.get('product_name') if isinstance(item, dict) else None,
            'category': item.get('category') if isinstance(item, dict) else None,
            'quantity': quantity,
            'price': price,
            'color': details.get('color'),
            'size': details.get('size'),
            'launch_type': details.get('launch_type'),
        })

    order_row = {
        'order_id': order_id,
        'event_id': event.get('event_id'),
        'event_timestamp': event.get('event_timestamp'),
        'event_type': event.get('event_type'),
        'channel': event.get('channel'),
        'customer_id': safe_get(event, 'customer.customer_id'),
        'loyalty_tier': safe_get(event, 'customer.loyalty_tier'),
        'country': safe_get(event, 'customer.location.country'),
        'state': safe_get(event, 'customer.location.state'),
        'city': safe_get(event, 'customer.location.city'),
        'warehouse_id': safe_get(event, 'fulfillment.warehouse_id'),
        'dispatch_priority': safe_get(event, 'fulfillment.dispatch_priority'),
        'payment_status': safe_get(event, 'order.payment_status'),
        'currency': safe_get(event, 'order.currency'),
        'order_total_amount': round(order_total, 2),
    }
    return order_row, item_rows


def load_rows(order_rows, item_rows):
    order_sql = """
    INSERT INTO warehouse.orders (
        order_id, event_id, event_timestamp, event_type, channel,
        customer_id, loyalty_tier, country, state, city,
        warehouse_id, dispatch_priority, payment_status, currency, order_total_amount
    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    ON CONFLICT (order_id) DO UPDATE SET
        event_id = EXCLUDED.event_id,
        event_timestamp = EXCLUDED.event_timestamp,
        event_type = EXCLUDED.event_type,
        channel = EXCLUDED.channel,
        customer_id = EXCLUDED.customer_id,
        loyalty_tier = EXCLUDED.loyalty_tier,
        country = EXCLUDED.country,
        state = EXCLUDED.state,
        city = EXCLUDED.city,
        warehouse_id = EXCLUDED.warehouse_id,
        dispatch_priority = EXCLUDED.dispatch_priority,
        payment_status = EXCLUDED.payment_status,
        currency = EXCLUDED.currency,
        order_total_amount = EXCLUDED.order_total_amount;
    """

    item_sql = """
    INSERT INTO warehouse.order_items (
        order_id, sku, product_name, category, quantity, price, color, size, launch_type
    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s);
    """

    with get_db_connection() as conn:
        with conn.cursor() as cur:
            order_ids = [row['order_id'] for row in order_rows if row.get('order_id')]
            if order_ids:
                cur.execute('DELETE FROM warehouse.order_items WHERE order_id = ANY(%s);', (order_ids,))

            for row in order_rows:
                cur.execute(order_sql, (
                    row['order_id'], row['event_id'], row['event_timestamp'], row['event_type'], row['channel'],
                    row['customer_id'], row['loyalty_tier'], row['country'], row['state'], row['city'],
                    row['warehouse_id'], row['dispatch_priority'], row['payment_status'], row['currency'], row['order_total_amount'],
                ))

            for row in item_rows:
                cur.execute(item_sql, (
                    row['order_id'], row['sku'], row['product_name'], row['category'], row['quantity'],
                    row['price'], row['color'], row['size'], row['launch_type'],
                ))
        conn.commit()


def update_file_status(file_path, status, records_count=None, error_message=None):
    local_path = 'local://' + str(file_path)
    sql = """
    UPDATE observability.file_processing_log
    SET file_status = %s,
        records_count = COALESCE(%s, records_count),
        error_message = %s,
        processed_at = CURRENT_TIMESTAMP
    WHERE s3_path = %s;
    """
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(sql, (status, records_count, error_message, local_path))
        conn.commit()


def flatten_file(input_file):
    input_path = Path(input_file)
    order_rows = []
    item_rows = []
    bad_records = 0

    with input_path.open('r', encoding='utf-8') as f:
        for line_number, line in enumerate(f, start=1):
            line = line.strip()
            if not line:
                continue
            try:
                event = json.loads(line)
                order_row, rows = flatten_event(event)
                if not order_row.get('order_id'):
                    raise ValueError('Missing order_id')
                order_rows.append(order_row)
                item_rows.extend(rows)
            except Exception as exc:
                bad_records += 1
                print(f'Bad record at line {line_number}: {exc}')

    if bad_records:
        update_file_status(input_path, 'FAILED', len(order_rows), f'{bad_records} bad records')
        raise RuntimeError(f'Flattening failed because {bad_records} bad records were found')

    load_rows(order_rows, item_rows)
    update_file_status(input_path, 'PROCESSED', len(order_rows), None)

    return {
        'input_file': str(input_path),
        'orders_loaded': len(order_rows),
        'items_loaded': len(item_rows),
        'file_status': 'PROCESSED',
    }


def main():
    parser = argparse.ArgumentParser(description='Flatten Nike nested JSONL into warehouse tables')
    parser.add_argument('--input-file', required=True)
    args = parser.parse_args()
    result = flatten_file(args.input_file)
    print('Nested JSON flattening completed successfully')
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
