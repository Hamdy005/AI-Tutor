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

    # 1. Fall back to x-user-id header first (High performance, used by frontend)
    if x_user_id:
        return {
            "id": x_user_id,
            "name": x_user_name,
            "email": x_user_email,
        }

    # 2. If no header, and a Bearer token is present, verify it with Supabase
    if token:
        try:
            verify_client = auth_client if auth_client is not None else client
            response = verify_client.auth.get_user(token)
            user = getattr(response, "user", None) or response
            if user:
                return user
        except Exception:
            pass

    # 3. Last resort: default dev user if everything is missing
    if client is None:
        return DEV_USER

    if token:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Invalid authentication")
    raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Not authenticated")


async def get_current_user_id(current_user=Depends(get_current_user)) -> str:
    user_id = getattr(current_user, "id", None)
    if not user_id and isinstance(current_user, dict):
        user_id = current_user.get("id")
    if not user_id:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Unauthorized")
    return user_id
