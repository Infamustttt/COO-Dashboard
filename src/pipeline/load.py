import pandas as pd
from sqlalchemy import text
from src.db.connection import get_engine

def load_df(df: pd.DataFrame, table: str):
    """Truncate the table and insert fresh data. Safer than replace with foreign keys."""
    engine = get_engine()
    with engine.begin() as conn:
        conn.execute(text(f"TRUNCATE TABLE {table} RESTART IDENTITY CASCADE"))
    df.to_sql(table, engine, if_exists="append", index=False)
    print(f"Loaded {len(df)} rows into {table}")
