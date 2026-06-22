"""Database helpers for the NexCart PostgreSQL application."""

from __future__ import annotations

import os
from contextlib import contextmanager
from typing import Iterator

import pandas as pd
import psycopg2
from dotenv import load_dotenv

load_dotenv()


def get_db_config() -> dict:
    """Read database settings from environment variables or .env."""
    return {
        "host": os.getenv("DB_HOST", "localhost"),
        "port": int(os.getenv("DB_PORT", "5432")),
        "dbname": os.getenv("DB_NAME", "nexcart_olist"),
        "user": os.getenv("DB_USER", "postgres"),
        "password": os.getenv("DB_PASSWORD", ""),
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
