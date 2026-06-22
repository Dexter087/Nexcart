"""Database helpers for the NexCart PostgreSQL application."""

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


def get_db_config() -> dict:
    """Read database settings from Streamlit secrets, environment variables, or .env."""
    host = _get_streamlit_secret("DB_HOST", os.getenv("DB_HOST", "localhost"))
    port = _get_streamlit_secret("DB_PORT", os.getenv("DB_PORT", "5432"))
    dbname = _get_streamlit_secret("DB_NAME", os.getenv("DB_NAME", "nexcart_olist"))
    user = _get_streamlit_secret("DB_USER", os.getenv("DB_USER", "postgres"))
    password = _get_streamlit_secret("DB_PASSWORD", os.getenv("DB_PASSWORD", ""))
    return {
        "host": host,
        "port": int(port or 5432),
        "dbname": dbname,
        "user": user,
        "password": password,
    }


@contextmanager
def get_connection() -> Iterator[psycopg2.extensions.connection]:
    """Open and close a PostgreSQL connection."""
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
