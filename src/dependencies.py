from fastapi import Depends, HTTPException, Header, status
from fastapi.security import OAuth2PasswordBearer
from typing import Any, Optional

from src.database import get_supabase

DEV_USER_ID = "00000000-0000-0000-0000-000000000001"

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    x_user_id: Optional[str] = Header(None),
) -> Any:
    client = get_supabase()
    if client is None:
        if x_user_id:
            return {"id": x_user_id}
        raise HTTPException(
            status.HTTP_500_INTERNAL_SERVER_ERROR, "Supabase not configured"
        )
    try:
        response = client.auth.get_user(token)
    except Exception:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Invalid authentication")
    user = getattr(response, "user", None) or response
    if not user:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Unauthorized")
    return user


async def get_current_user_id(current_user=Depends(get_current_user)) -> str:
    user_id = getattr(current_user, "id", None)
    if not user_id and isinstance(current_user, dict):
        user_id = current_user.get("id")
    if not user_id:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Unauthorized")
    return user_id
