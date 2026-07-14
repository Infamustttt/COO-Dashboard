"""
Orchestrates the full data pipeline: fetch -> clean -> calculate -> load.
Set USE_SEED_DATA=true in .env to skip API calls and use local seed data.
"""
import os
import pandas as pd
from dotenv import load_dotenv
from src.pipeline.clean import clean_projects, clean_employees, clean_survey_responses
from src.pipeline.load import load_df
from src.calculators.rag_calculator import calculate_rag
from src.calculators.utilization import calculate_utilization_status
from src.calculators.sla_checker import check_sla_compliance

load_dotenv()

def to_pg_array(val):
    """Convert a Python list string like \"['a','b']\" to postgres format \"{a,b}\"."""
    import ast
    try:
        items = ast.literal_eval(val) if isinstance(val, str) else val
        return "{" + ",".join(str(i) for i in items) + "}"
    except Exception:
        return "{}"

def run():
    use_seed = os.getenv("USE_SEED_DATA", "false").lower() == "true"

    if use_seed:
        projects_df = pd.read_csv("data/seed/projects.csv", parse_dates=["start_date", "expected_end_date"])
        employees_df = pd.read_csv("data/seed/employees.csv", parse_dates=["joining_date", "availability_date", "bench_since"])
        responses_df = pd.read_csv("data/seed/csat_responses.csv", parse_dates=["survey_date"])
        slas_df = pd.read_csv("data/seed/slas.csv", parse_dates=["last_checked"])
        escalations_df = pd.read_csv("data/seed/escalations.csv", parse_dates=["raised_date", "resolution_target"])
        timesheets_df = pd.read_csv("data/seed/timesheets.csv", parse_dates=["week_ending_date", "submission_date"])
        onboarding_df = pd.read_csv("data/seed/onboarding.csv", parse_dates=["joining_date"])
        sops_df = pd.read_csv("data/seed/sops.csv", parse_dates=["last_updated"])

        employees_df["skills"] = employees_df["skills"].apply(to_pg_array)
        responses_df["key_themes"] = responses_df["key_themes"].apply(to_pg_array)
        sops_df["applicable_to"] = sops_df["applicable_to"].apply(to_pg_array)
        slas_df["breach_dates"] = "{}"
    else:
        from src.pipeline.fetch import fetch_all
        raw = fetch_all()
        projects_df = clean_projects(raw["projects"])
        employees_df = clean_employees(raw["employees"])
        responses_df = clean_survey_responses(raw["survey_responses"])
        slas_df = pd.DataFrame()
        escalations_df = pd.DataFrame()
        timesheets_df = pd.DataFrame()
        onboarding_df = pd.DataFrame()
        sops_df = pd.DataFrame()

    projects_df[["rag_status", "risk_flag"]] = projects_df.apply(
        lambda row: calculate_rag(row.to_dict()), axis=1, result_type="expand"
    )

    employees_df["utilization_status"] = employees_df["total_allocation_pct"].apply(
        calculate_utilization_status
    )

    slas_df["compliance_status"] = slas_df.apply(
        lambda row: check_sla_compliance(row.to_dict()), axis=1
    )

    load_df(projects_df, "projects")
    load_df(employees_df, "employees")
    load_df(responses_df, "csat_responses")

    if not slas_df.empty:
        load_df(slas_df, "slas")
    if not escalations_df.empty:
        load_df(escalations_df, "escalations")
    if not timesheets_df.empty:
        load_df(timesheets_df, "timesheets")
    if not onboarding_df.empty:
        load_df(onboarding_df, "onboarding_tracker")
    if not sops_df.empty:
        load_df(sops_df, "sops")

    print("Pipeline complete.")

if __name__ == "__main__":
    run()
