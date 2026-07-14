import os, datetime
from fastapi import APIRouter, HTTPException, Response, Cookie
from pydantic import BaseModel
from jose import jwt, JWTError

router = APIRouter()

SECRET = os.getenv("COO_JWT_SECRET", "coo-ops-jwt-secret-2025")
ALGO   = "HS256"
EXPIRY = datetime.timedelta(hours=24)

USERS = {
    "aarush":       {"name": "Aarush",            "password": "coo123", "role": "COO"},
    "delivery_mgr": {"name": "Delivery Manager",  "password": "del123", "role": "Delivery Manager"},
    "muskaan":      {"name": "Muskaan",            "password": "hr123",  "role": "HR Manager"},
}

ROLE_PAGES = {
    "COO": [
        "Executive Summary", "Project Delivery", "Resource Utilization",
        "SLA Compliance", "Client Satisfaction", "Escalations",
        "Timesheets", "People Ops", "SOP Library",
    ],
    "Delivery Manager": [
        "Executive Summary", "Project Delivery", "Resource Utilization",
        "SLA Compliance", "Client Satisfaction", "Escalations", "SOP Library",
    ],
    "HR Manager": [
        "Executive Summary", "Resource Utilization",
        "Timesheets", "People Ops", "SOP Library",
    ],
}

class LoginRequest(BaseModel):
    username: str
    password: str

def make_token(username: str) -> str:
    user = USERS[username]
    payload = {
        "sub": username,
        "name": user["name"],
        "role": user["role"],
        "exp": datetime.datetime.utcnow() + EXPIRY,
    }
    return jwt.encode(payload, SECRET, algorithm=ALGO)

def decode_token(token: str) -> dict:
    try:
        return jwt.decode(token, SECRET, algorithms=[ALGO])
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

@router.post("/login")
def login(body: LoginRequest, response: Response):
    user = USERS.get(body.username.lower())
    if not user or user["password"] != body.password:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    token = make_token(body.username.lower())
    response.set_cookie(
        "coo_auth", token,
        httponly=True, samesite="lax", max_age=86400,
    )
    return {
        "username": body.username.lower(),
        "name": user["name"],
        "role": user["role"],
        "pages": ROLE_PAGES[user["role"]],
    }

@router.post("/logout")
def logout(response: Response):
    response.delete_cookie("coo_auth")
    return {"ok": True}

@router.get("/me")
def me(coo_auth: str = Cookie(default=None)):
    if not coo_auth:
        raise HTTPException(status_code=401, detail="Not authenticated")
    payload = decode_token(coo_auth)
    role = payload["role"]
    return {
        "username": payload["sub"],
        "name": payload["name"],
        "role": role,
        "pages": ROLE_PAGES[role],
    }
