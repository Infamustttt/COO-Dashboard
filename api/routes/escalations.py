from fastapi import APIRouter, Depends
from api.deps import current_user
from src.db.queries import query_df

router = APIRouter()

@router.get("")
def get_escalations(user=Depends(current_user)):
    df = query_df("""
        SELECT title, raised_by, raised_date::text, project_id,
               escalation_type, severity, status, assigned_owner,
               resolution_target::text, days_open, root_cause, auto_triggered
        FROM escalations
        ORDER BY
            CASE severity WHEN 'P1' THEN 1 WHEN 'P2' THEN 2 ELSE 3 END,
            days_open DESC
    """)
    return df.to_dict(orient="records")

@router.get("/summary")
def get_escalations_summary(user=Depends(current_user)):
    df = query_df("""
        SELECT
            COUNT(*) FILTER (WHERE status='Open')                           AS open_total,
            COUNT(*) FILTER (WHERE severity='P1' AND status='Open')         AS p1_open,
            COUNT(*) FILTER (WHERE severity='P2' AND status='Open')         AS p2_open,
            COUNT(*) FILTER (WHERE severity='P3' AND status='Open')         AS p3_open,
            COUNT(*) FILTER (WHERE status='Resolved')                       AS resolved,
            ROUND(AVG(days_open) FILTER (WHERE status='Open')::numeric, 1)  AS avg_days_open
        FROM escalations
    """)
    return df.to_dict(orient="records")[0]
