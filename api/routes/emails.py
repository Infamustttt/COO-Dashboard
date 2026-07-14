from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from api.deps import current_user
from src.db.queries import query_df, execute

router = APIRouter()

class EmailRequest(BaseModel):
    to: str
    subject: str
    body: str
    related_type: str | None = None   # e.g. "project", "escalation"
    related_id: str | None = None     # e.g. "PROJ-004"

@router.post("")
def send_email(req: EmailRequest, user=Depends(current_user)):
    """Demo outbox: persists the mail and reports it as sent.
    Swap in real SMTP later without touching the frontend."""
    if not req.to or "@" not in req.to:
        raise HTTPException(status_code=422, detail="Invalid recipient address")
    if not req.subject.strip():
        raise HTTPException(status_code=422, detail="Subject is required")
    execute("""
        INSERT INTO sent_emails (to_addr, subject, body, related_type, related_id, sent_by)
        VALUES (:to, :subject, :body, :rtype, :rid, :sender)
    """, {
        "to": req.to, "subject": req.subject, "body": req.body,
        "rtype": req.related_type, "rid": req.related_id,
        "sender": user.get("name", "unknown"),
    })
    return {"ok": True, "message": f"Email sent to {req.to}"}

@router.get("")
def list_emails(user=Depends(current_user)):
    df = query_df("""
        SELECT id, to_addr, subject, related_type, related_id,
               sent_by, sent_at::text
        FROM sent_emails ORDER BY sent_at DESC LIMIT 50
    """)
    return df.to_dict(orient="records")
