import os
import psycopg2


def get_db_connection():
    return psycopg2.connect(
        host=os.getenv("DB_HOST", os.getenv("POSTGRES_HOST", "postgres")),
        port=int(os.getenv("DB_PORT", os.getenv("POSTGRES_PORT", "5432"))),
        dbname=os.getenv("DB_NAME", os.getenv("POSTGRES_DB", "airflow")),
        user=os.getenv("DB_USER", os.getenv("POSTGRES_USER", "airflow")),
        password=os.getenv("DB_PASSWORD", os.getenv("POSTGRES_PASSWORD", "airflow")),
    )
