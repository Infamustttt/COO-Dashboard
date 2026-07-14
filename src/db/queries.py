import pandas as pd
from sqlalchemy import text
from src.db.connection import get_engine

def query_df(sql: str, params: dict = None) -> pd.DataFrame:
    """Run a SQL query and return a DataFrame."""
    with get_engine().connect() as conn:
        return pd.read_sql_query(text(sql), conn, params=params)

def execute(sql: str, params: dict = None):
    """Run a write query (INSERT, UPDATE, DELETE)."""
    with get_engine().begin() as conn:
        conn.execute(text(sql), params or {})

def fetch_one(sql: str, params: dict = None) -> dict | None:
    """Run a query and return the first row as a dict (or None)."""
    df = query_df(sql, params)
    return df.to_dict(orient="records")[0] if len(df) else None
