from fastapi import APIRouter, Depends
from api.deps import current_user
from src.db.queries import query_df

router = APIRouter()

@router.get("")
def get_projects(user=Depends(current_user)):
    df = query_df("""
        SELECT project_id, project_name, client_name, delivery_unit,
               project_manager, current_phase, rag_status, completion_pct,
               budget_consumed_pct, open_issues, overdue_tasks,
               start_date::text, expected_end_date::text, last_updated::text,
               lower(replace(project_manager, ' ', '.')) || '@company.com' AS pm_email
        FROM projects
        ORDER BY rag_status, project_name
    """)
    return df.to_dict(orient="records")

@router.get("/summary")
def get_projects_summary(user=Depends(current_user)):
    df = query_df("""
        SELECT
            COUNT(*) AS total,
            SUM(CASE WHEN rag_status='RED'   THEN 1 ELSE 0 END) AS red,
            SUM(CASE WHEN rag_status='AMBER' THEN 1 ELSE 0 END) AS amber,
            SUM(CASE WHEN rag_status='GREEN' THEN 1 ELSE 0 END) AS green,
            ROUND(AVG(completion_pct)::numeric, 1)       AS avg_completion,
            ROUND(AVG(budget_consumed_pct)::numeric, 1)  AS avg_budget
        FROM projects
    """)
    return df.to_dict(orient="records")[0]
