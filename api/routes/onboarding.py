from fastapi import APIRouter, Depends
from api.deps import current_user
from src.db.queries import query_df

router = APIRouter()

@router.get("")
def get_onboarding(user=Depends(current_user)):
    df = query_df("""
        SELECT o.employee_id, e.full_name, e.designation, e.department,
               o.joining_date::text, o.assigned_buddy, o.assigned_manager,
               o.laptop_issued, o.email_created, o.induction_done,
               o.policies_signed, o.first_project_assigned,
               o.checklist_pct, o.onboarding_score, o.status
        FROM onboarding o
        JOIN employees e ON o.employee_id = e.employee_id
        ORDER BY o.checklist_pct ASC
    """)
    return df.to_dict(orient="records")

@router.get("/summary")
def get_onboarding_summary(user=Depends(current_user)):
    df = query_df("""
        SELECT
            COUNT(*) AS total,
            COUNT(*) FILTER (WHERE status='Completed')   AS completed,
            COUNT(*) FILTER (WHERE status='In Progress') AS in_progress,
            COUNT(*) FILTER (WHERE checklist_pct < 60)   AS needs_attention,
            ROUND(AVG(checklist_pct)::numeric, 1)         AS avg_completion,
            ROUND(AVG(onboarding_score)::numeric, 2)      AS avg_score
        FROM onboarding
    """)
    return df.to_dict(orient="records")[0]
