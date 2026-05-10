from fastapi import Depends, HTTPException, Header, status
from fastapi.security import OAuth2PasswordBearer
from typing import Any, Optional

from src.database import get_supabase, get_auth_supabase

DEV_USER_ID = "00000000-0000-0000-0000-000000000001"
DEV_USER = {"id": DEV_USER_ID, "email": "dev@studymate.ai", "name": "Dev User"}

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token", auto_error=False)


async def get_current_user(
    token: Optional[str] = Depends(oauth2_scheme),
    x_user_id: Optional[str] = Header(None),
    x_user_name: Optional[str] = Header(None),
    x_user_email: Optional[str] = Header(None),
) -> Any:
    auth_client = get_auth_supabase()
    client = get_supabase()

    # Dev mode: no Supabase configured
    if client is None:
        if x_user_id:
            return {
                "id": x_user_id,
                "name": x_user_name or "User",
                "email": x_user_email or f"user{x_user_id}@studymate.ai",
            }
        return DEV_USER

    # Real Supabase auth - use anon key client for token verification
    if auth_client is not None:
        if not token:
            raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Not authenticated")
        try:
            response = auth_client.auth.get_user(token)
        except Exception:
            raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Invalid authentication")
        user = getattr(response, "user", None) or response
        if not user:
            raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Unauthorized")
        return user

    # Fallback to service_role client if anon key not available
    if not token:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Not authenticated")
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
