from fastapi import APIRouter, Depends
from api.deps import current_user
from src.db.queries import query_df

router = APIRouter()

@router.get("")
def get_timesheets(user=Depends(current_user)):
    df = query_df("""
        SELECT t.employee_id, e.full_name, e.department,
               t.week_ending_date::text, t.task_type, t.hours_logged,
               t.is_billable, t.approval_status, t.submission_status
        FROM timesheets t
        JOIN employees e ON t.employee_id = e.employee_id
        ORDER BY t.week_ending_date DESC, e.full_name
    """)
    return df.to_dict(orient="records")

@router.get("/summary")
def get_timesheets_summary(user=Depends(current_user)):
    df = query_df("""
        SELECT
            COUNT(*)                                                             AS total_entries,
            COUNT(*) FILTER (WHERE submission_status='On Time')                 AS on_time,
            COUNT(*) FILTER (WHERE submission_status='Late')                    AS late,
            COUNT(*) FILTER (WHERE approval_status='Approved')                  AS approved,
            COUNT(*) FILTER (WHERE approval_status='Pending')                   AS pending,
            ROUND(AVG(hours_logged)::numeric, 1)                                AS avg_hours,
            ROUND(
                100.0 * COUNT(*) FILTER (WHERE submission_status='On Time') / COUNT(*), 1
            ) AS compliance_pct
        FROM timesheets
    """)
    return df.to_dict(orient="records")[0]
