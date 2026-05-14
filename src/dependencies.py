from fastapi import Depends, HTTPException, Header, status
from fastapi.security import OAuth2PasswordBearer
from typing import Any, Optional

from src.database import get_supabase, get_auth_supabase

DEV_USER_ID = "00000000-0000-0000-0000-000000000001"
DEV_USER = {"id": DEV_USER_ID, "email": "dev@studymate.ai", "name": "Dev User"}

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token", auto_error=False)


async def get_current_user(
    token: Optional[str] = Depends(oauth2_scheme),
    x_auth_token: Optional[str] = Header(None),
    authorization: Optional[str] = Header(None),
) -> Any:
    auth_client = get_auth_supabase()
    client = get_supabase()

    supabase_token = x_auth_token
    if not supabase_token and authorization:
        supabase_token = authorization.replace("Bearer ", "").strip()
    elif not supabase_token and token:
        supabase_token = token

    # If the token is a Hugging Face token (starts with hf_), ignore it for user auth
    if supabase_token and supabase_token.startswith("hf_"):
        supabase_token = None

    # Dev mode: no Supabase configured
    if client is None:
        return DEV_USER

    # 3. Verify the token with Supabase
    if supabase_token:
        try:
            verify_client = auth_client if auth_client is not None else client
            response = verify_client.auth.get_user(supabase_token)
            user = getattr(response, "user", None) or response
            if user:
                return user
        except Exception:
            pass

    raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Not authenticated")


async def get_current_user_id(
    x_auth_token: Optional[str] = Header(None),
    authorization: Optional[str] = Header(None),
) -> str:
    token = x_auth_token

    if not token and authorization:
        token = authorization.replace("Bearer ", "").strip()
    
    if token and token.startswith("hf_"):
        token = None

    client = get_supabase()
    if client is None:
        return DEV_USER_ID

    if not token:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Not authenticated")

    try:
        auth_client = get_auth_supabase()
        supabase = auth_client if auth_client is not None else client
        user = supabase.auth.get_user(token)
        user_obj = getattr(user, "user", None) or user
        return str(user_obj.id)
    except Exception:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Invalid or expired token")
