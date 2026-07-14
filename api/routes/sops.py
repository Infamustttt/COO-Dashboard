from fastapi import APIRouter, Depends
from api.deps import current_user
from src.db.queries import query_df

router = APIRouter()

@router.get("")
def get_sops(user=Depends(current_user)):
    df = query_df("""
        SELECT sop_id, title, category, version, owner,
               last_updated::text, applicable_to, document_url, status,
               related_escalation_type
        FROM sops
        ORDER BY category, title
    """)
    return df.to_dict(orient="records")
