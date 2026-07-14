from fastapi import APIRouter, Depends
from api.deps import current_user
from src.db.queries import query_df

router = APIRouter()

@router.get("")
def get_slas(user=Depends(current_user)):
    df = query_df("""
        SELECT sla_id, client_name, sla_type, sla_description,
               target_value, actual_value, compliance_status,
               breach_count, has_penalty, penalty_amount, assigned_owner,
               last_checked::text
        FROM slas
        ORDER BY compliance_status DESC, client_name
    """)
    return df.to_dict(orient="records")

@router.get("/summary")
def get_slas_summary(user=Depends(current_user)):
    df = query_df("""
        SELECT
            COUNT(*) AS total,
            COUNT(*) FILTER (WHERE compliance_status='Met')      AS met,
            COUNT(*) FILTER (WHERE compliance_status='Breached') AS breached,
            ROUND(
                100.0 * COUNT(*) FILTER (WHERE compliance_status='Met') / COUNT(*), 1
            ) AS compliance_pct,
            SUM(penalty_amount) FILTER (WHERE compliance_status='Breached' AND has_penalty=true)
                AS total_penalty_exposure
        FROM slas
    """)
    return df.to_dict(orient="records")[0]
