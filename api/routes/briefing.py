from fastapi import APIRouter, Depends
from api.deps import current_user
from src.db.queries import query_df
from src.ai.briefing_generator import generate_weekly_briefing

router = APIRouter()

def _count(sql: str) -> int:
    return int(query_df(sql).iloc[0]["c"])

def _avg(sql: str, digits: int = 1) -> float:
    v = query_df(sql).iloc[0]["v"]
    return round(float(v), digits) if v is not None else 0.0

def _fetch_metrics():
    return {
        "total_projects":    _count("SELECT COUNT(*) AS c FROM projects"),
        "red":               _count("SELECT COUNT(*) AS c FROM projects WHERE rag_status='RED'"),
        "amber":             _count("SELECT COUNT(*) AS c FROM projects WHERE rag_status='AMBER'"),
        "green":             _count("SELECT COUNT(*) AS c FROM projects WHERE rag_status='GREEN'"),
        "avg_utilization":   _avg("SELECT AVG(total_allocation_pct) AS v FROM employees WHERE status='Active'"),
        "bench_count":       _count("SELECT COUNT(*) AS c FROM employees WHERE utilization_status='Bench'"),
        "over_allocated":    _count("SELECT COUNT(*) AS c FROM employees WHERE utilization_status='Over-allocated'"),
        "sla_compliance":    _avg("SELECT AVG(CASE WHEN compliance_status='Met' THEN 100.0 ELSE 0 END) AS v FROM slas"),
        "sla_breaches":      _count("SELECT COUNT(*) AS c FROM slas WHERE compliance_status='Breached'"),
        "avg_csat":          _avg("SELECT AVG(score) AS v FROM csat_responses", 2),
        "open_escalations":  _count("SELECT COUNT(*) AS c FROM escalations WHERE status='Open'"),
        "p1_count":          _count("SELECT COUNT(*) AS c FROM escalations WHERE severity='P1' AND status='Open'"),
        "active_employees":  _count("SELECT COUNT(*) AS c FROM employees WHERE status='Active'"),
        "timesheet_compliance": _avg(
            "SELECT 100.0*COUNT(*) FILTER(WHERE submission_status='On Time')/COUNT(*) AS v FROM timesheets"
        ),
    }

def _coo_briefing(m: dict) -> str:
    return (
        f"This week across the portfolio, {m['total_projects']} projects are active. "
        f"{m['red']} are RED, {m['amber']} are AMBER, and {m['green']} are GREEN. "
        f"Of the {m['active_employees']} active employees, {m['bench_count']} are currently on bench "
        f"and {m['over_allocated']} are over-allocated, with an average utilisation of {m['avg_utilization']}%. "
        f"SLA compliance stands at {m['sla_compliance']}% with {m['sla_breaches']} breaches recorded. "
        f"Client satisfaction averaged {m['avg_csat']:.2f} out of 5. "
        f"There are {m['open_escalations']} open escalations, including {m['p1_count']} at P1 severity. "
        f"Timesheet submission compliance this period is {m['timesheet_compliance']}%."
    )

def _dm_briefing(m: dict) -> str:
    return (
        f"Portfolio health this week: {m['red']} RED projects require immediate attention, "
        f"{m['amber']} are at AMBER risk. SLA compliance is at {m['sla_compliance']}% "
        f"with {m['sla_breaches']} active breaches. "
        f"Client CSAT averages {m['avg_csat']:.2f}/5. "
        f"{m['p1_count']} P1 escalations are currently open. "
        f"Resource pool shows {m['bench_count']} bench and {m['over_allocated']} over-allocated staff "
        f"from an average utilisation of {m['avg_utilization']}%."
    )

def _hr_briefing(m: dict) -> str:
    return (
        f"Workforce snapshot: {m['active_employees']} employees active. "
        f"{m['bench_count']} are on bench and {m['over_allocated']} are over-allocated. "
        f"Average utilisation is {m['avg_utilization']}%. "
        f"Timesheet compliance this period is {m['timesheet_compliance']}%. "
        f"People operations and onboarding data are up to date as of this week."
    )

def _template_briefing(role: str, m: dict) -> str:
    if role == "Delivery Manager":
        return _dm_briefing(m)
    if role == "HR Manager":
        return _hr_briefing(m)
    return _coo_briefing(m)

@router.get("")
def get_briefing(user=Depends(current_user)):
    m = _fetch_metrics()
    role = user.get("role", "COO")
    try:
        briefing = generate_weekly_briefing(m)  # dict: {summary, emergencies[]}
        source = "ai"
    except Exception as e:
        print(f"[briefing] AI generation failed ({e}); using template fallback")
        briefing = {"summary": _template_briefing(role, m), "emergencies": []}
        source = "template"
    return {"role": role, "briefing": briefing, "source": source, "metrics": m}
