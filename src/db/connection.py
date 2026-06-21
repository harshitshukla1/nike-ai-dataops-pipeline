import os
import psycopg2


def get_secret(name: str, default=None):
    value = os.getenv(name)
    if value:
        return value

    try:
        import streamlit as st
        if name in st.secrets:
            return str(st.secrets[name])
    except Exception:
        pass

    return default


def get_db_connection():
    database_url = get_secret("DATABASE_URL")

    if database_url and database_url.startswith("postgresql://"):
        return psycopg2.connect(database_url)

    return psycopg2.connect(
        host=get_secret("DB_HOST", get_secret("POSTGRES_HOST", "postgres")),
        port=int(get_secret("DB_PORT", get_secret("POSTGRES_PORT", "5432"))),
        dbname=get_secret("DB_NAME", get_secret("POSTGRES_DB", "airflow")),
        user=get_secret("DB_USER", get_secret("POSTGRES_USER", "airflow")),
        password=get_secret("DB_PASSWORD", get_secret("POSTGRES_PASSWORD", "airflow")),
    )
