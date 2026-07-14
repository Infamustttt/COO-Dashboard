from fastapi import FastAPI, BackgroundTasks
from src.pipeline.run_pipeline import run as run_pipeline
from src.ai.briefing_generator import generate_weekly_briefing
from src.db.queries import query_df

app = FastAPI(title="COO Ops Center API")

@app.post("/api/run-pipeline")
def trigger_pipeline(background_tasks: BackgroundTasks):
    """Called by n8n nightly cron to refresh all data."""
    background_tasks.add_task(run_pipeline)
    return {"status": "pipeline started"}

@app.post("/api/generate-briefing")
def trigger_briefing():
    """Called by n8n weekly cron to generate COO briefing."""
    metrics = {
        "total_projects": query_df("SELECT COUNT(*) as c FROM projects").iloc[0]["c"],
        "red": query_df("SELECT COUNT(*) as c FROM projects WHERE rag_status='RED'").iloc[0]["c"],
        "amber": query_df("SELECT COUNT(*) as c FROM projects WHERE rag_status='AMBER'").iloc[0]["c"],
        "green": query_df("SELECT COUNT(*) as c FROM projects WHERE rag_status='GREEN'").iloc[0]["c"],
        "avg_utilization": query_df("SELECT AVG(total_allocation_pct) as v FROM employees WHERE status='Active'").iloc[0]["v"],
        "bench_count": query_df("SELECT COUNT(*) as c FROM employees WHERE utilization_status='Bench'").iloc[0]["c"],
        "over_allocated": query_df("SELECT COUNT(*) as c FROM employees WHERE utilization_status='Over-allocated'").iloc[0]["c"],
        "sla_compliance": query_df("SELECT AVG(CASE WHEN compliance_status='Met' THEN 100.0 ELSE 0 END) as v FROM slas").iloc[0]["v"],
        "sla_breaches": query_df("SELECT COUNT(*) as c FROM slas WHERE compliance_status='Breached'").iloc[0]["c"],
        "avg_csat": query_df("SELECT AVG(score) as v FROM csat_responses").iloc[0]["v"],
        "open_escalations": query_df("SELECT COUNT(*) as c FROM escalations WHERE status='Open'").iloc[0]["c"],
        "p1_count": query_df("SELECT COUNT(*) as c FROM escalations WHERE severity='P1' AND status='Open'").iloc[0]["c"],
    }
    briefing = generate_weekly_briefing(metrics)
    return {"briefing": briefing}

@app.get("/api/employees/new-joiners-today")
def get_new_joiners():
    """Used by n8n onboarding workflow to detect new hires."""
    df = query_df("SELECT * FROM employees WHERE joining_date = CURRENT_DATE")
    return df.to_dict(orient="records")
