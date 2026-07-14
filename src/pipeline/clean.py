import pandas as pd

def clean_projects(raw: list) -> pd.DataFrame:
    df = pd.DataFrame(raw)
    df.dropna(subset=["project_id", "project_name"], inplace=True)
    df["budget_consumed_pct"] = df["budget_consumed_pct"].clip(0, 150)
    df["completion_pct"] = df["completion_pct"].clip(0, 100)
    return df

def clean_employees(raw: list) -> pd.DataFrame:
    df = pd.DataFrame(raw)
    df.dropna(subset=["employee_id", "full_name"], inplace=True)
    df["total_allocation_pct"] = df["total_allocation_pct"].fillna(0)
    return df

def clean_survey_responses(raw: list) -> pd.DataFrame:
    df = pd.DataFrame(raw)
    df["score"] = pd.to_numeric(df["score"], errors="coerce")
    df.dropna(subset=["score"], inplace=True)
    return df
