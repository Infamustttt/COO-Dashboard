from fastapi import APIRouter, Depends
from api.deps import current_user
from src.db.queries import query_df

router = APIRouter()

@router.get("")
def get_csat(user=Depends(current_user)):
    df = query_df("""
        SELECT client_name, project_id, survey_date::text, survey_type,
               score, nps_category, feedback_text, sentiment,
               key_themes, follow_up_required, follow_up_status, account_manager
        FROM csat_responses
        ORDER BY survey_date DESC
    """)
    return df.to_dict(orient="records")

@router.get("/summary")
def get_csat_summary(user=Depends(current_user)):
    df = query_df("""
        SELECT
            ROUND(AVG(score)::numeric, 2)                                        AS avg_score,
            COUNT(*) FILTER (WHERE nps_category='Promoter')                      AS promoters,
            COUNT(*) FILTER (WHERE nps_category='Passive')                       AS passives,
            COUNT(*) FILTER (WHERE nps_category='Detractor')                     AS detractors,
            COUNT(*) FILTER (WHERE sentiment='Positive')                         AS positive,
            COUNT(*) FILTER (WHERE sentiment='Neutral')                          AS neutral,
            COUNT(*) FILTER (WHERE sentiment='Negative')                         AS negative,
            COUNT(*) FILTER (WHERE follow_up_required=true AND follow_up_status='Open') AS open_followups
        FROM csat_responses
    """)
    return df.to_dict(orient="records")[0]

@router.get("/by-client")
def get_csat_by_client(user=Depends(current_user)):
    df = query_df("""
        SELECT client_name, ROUND(AVG(score)::numeric, 2) AS avg_score, COUNT(*) AS responses
        FROM csat_responses
        GROUP BY client_name ORDER BY avg_score DESC
    """)
    return df.to_dict(orient="records")
