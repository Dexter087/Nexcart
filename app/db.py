"""Database helpers for the NexCart PostgreSQL application.

The same code supports two modes:
1. Local development using a .env file.
2. Streamlit Community Cloud using st.secrets.
"""

from __future__ import annotations

import os
from contextlib import contextmanager
from typing import Iterator

import pandas as pd
import psycopg2
from dotenv import load_dotenv

load_dotenv()


def _get_streamlit_secret(name: str, default: str | None = None) -> str | None:
    """Read a Streamlit secret when available; otherwise return default.

    This lets the same code run locally from .env and on Streamlit Community Cloud
    from the app's Secrets panel.
    """
    try:
        import streamlit as st  # imported lazily so CLI/API use still works

        if name in st.secrets:
            return str(st.secrets[name])
    except Exception:
        pass
    return default


def get_database_url() -> str | None:
    """Return a full PostgreSQL URL if one was provided.

    Neon and other cloud PostgreSQL providers often provide one complete URL.
    The app checks several common names so deployment is easier.
    """
    return (
        _get_streamlit_secret("DATABASE_URL", os.getenv("DATABASE_URL"))
        or _get_streamlit_secret("CLOUD_DB_URL", os.getenv("CLOUD_DB_URL"))
        or _get_streamlit_secret("DB_URL", os.getenv("DB_URL"))
    )


def get_db_config() -> dict:
    """Read individual database settings from Streamlit secrets, env vars, or .env."""
    host = _get_streamlit_secret("DB_HOST", os.getenv("DB_HOST", "localhost"))
    port = _get_streamlit_secret("DB_PORT", os.getenv("DB_PORT", "5432"))
    dbname = _get_streamlit_secret("DB_NAME", os.getenv("DB_NAME", "nexcart_olist"))
    user = _get_streamlit_secret("DB_USER", os.getenv("DB_USER", "postgres"))
    password = _get_streamlit_secret("DB_PASSWORD", os.getenv("DB_PASSWORD", ""))
    sslmode = _get_streamlit_secret("DB_SSLMODE", os.getenv("DB_SSLMODE", "prefer"))

    return {
        "host": host,
        "port": int(port or 5432),
        "dbname": dbname,
        "user": user,
        "password": password,
        "sslmode": sslmode,
    }


@contextmanager
def get_connection() -> Iterator[psycopg2.extensions.connection]:
    """Open and close a PostgreSQL connection."""
    database_url = get_database_url()
    if database_url:
        conn = psycopg2.connect(database_url)
    else:
        conn = psycopg2.connect(**get_db_config())
    try:
        yield conn
    finally:
        conn.close()


def run_query(query: str, params: tuple | None = None) -> pd.DataFrame:
    """Run a SELECT query and return the result as a pandas DataFrame."""
    with get_connection() as conn:
        return pd.read_sql_query(query, conn, params=params)


def execute_statement(statement: str, params: tuple | None = None) -> None:
    """Run an INSERT/UPDATE/DDL/CALL statement and commit it."""
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(statement, params)
        conn.commit()


def test_connection() -> tuple[bool, str]:
    """Return a friendly connection test result."""
    try:
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT current_database(), current_user, version();")
                db_name, db_user, version = cur.fetchone()
        return True, f"Connected to database '{db_name}' as user '{db_user}'. {version}"
    except Exception as exc:  # pragma: no cover - shown to user in Streamlit
        return False, str(exc)
