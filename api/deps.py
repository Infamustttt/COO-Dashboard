from fastapi import Cookie, HTTPException
from api.auth import decode_token

def current_user(coo_auth: str = Cookie(default=None)) -> dict:
    if not coo_auth:
        raise HTTPException(status_code=401, detail="Not authenticated")
    return decode_token(coo_auth)
