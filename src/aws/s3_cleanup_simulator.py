import os
from pathlib import Path

from src.db.connection import get_db_connection


def cleanup_latest_processed_file():
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT file_id, s3_path, file_size_mb
                FROM observability.file_processing_log
                WHERE file_status = 'PROCESSED'
                ORDER BY file_id DESC
                LIMIT 1;
            """)
            row = cur.fetchone()

            if not row:
                print("No PROCESSED file found for cleanup.")
                return {"status": "NO_FILE"}

            file_id, s3_path, file_size_mb = row
            local_path = s3_path.replace("local://", "")

            deleted = False
            if os.path.exists(local_path):
                os.remove(local_path)
                deleted = True

            estimated_saving = round((float(file_size_mb or 0) / 1024) * 0.023, 6)

            cur.execute("""
                UPDATE observability.file_processing_log
                SET file_status = 'DELETED',
                    processed_at = CURRENT_TIMESTAMP
                WHERE file_id = %s;
            """, (file_id,))

            cur.execute("""
                INSERT INTO finops.cost_savings_log (
                    dag_run_id,
                    file_path,
                    file_size_mb,
                    deleted_successfully,
                    estimated_storage_cost_saved_usd
                ) VALUES (%s, %s, %s, %s, %s);
            """, (
                "manual_cleanup",
                s3_path,
                file_size_mb,
                deleted,
                estimated_saving,
            ))

            cur.execute("""
                INSERT INTO finops.system_metrics_log (
                    service_name,
                    operation_name,
                    request_count,
                    bytes_processed,
                    estimated_cost_usd
                ) VALUES (%s, %s, %s, %s, %s);
            """, (
                "LOCAL_S3_SIMULATION",
                "DELETE",
                1,
                int(float(file_size_mb or 0) * 1024 * 1024),
                estimated_saving,
            ))

        conn.commit()

    result = {
        "file_id": file_id,
        "path": s3_path,
        "deleted_from_disk": deleted,
        "file_size_mb": float(file_size_mb or 0),
        "estimated_saving_usd": estimated_saving,
        "status": "DELETED",
    }
    print(result)
    return result


if __name__ == "__main__":
    cleanup_latest_processed_file()
