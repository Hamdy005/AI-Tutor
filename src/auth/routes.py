import uuid
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from src.database import get_auth_supabase
from src.store import create_user, get_user_by_email, delete_user_data, update_user_profile, get_user_by_id
from src.dependencies import get_current_user_id
from fastapi import Depends
from typing import Optional

router = APIRouter(prefix="/api/auth", tags=["Auth"])


class LoginRequest(BaseModel):
    email: str
    password: str


class SignupRequest(BaseModel):
    name: str
    email: str
    password: str


@router.post("/login")
async def login(body: LoginRequest):
    supabase = get_auth_supabase()

    # Real Supabase auth
    if supabase:
        try:
            res = supabase.auth.sign_in_with_password({"email": body.email, "password": body.password})
            sb_user = res.user
            session = res.session
            if not sb_user or not session:
                raise HTTPException(401, "Invalid email or password")
            # Fetch profile from our table to get custom name/avatar
            user_profile = get_user_by_id(str(sb_user.id))
            if not user_profile:
                # Fallback to metadata if profile doesn't exist yet
                user_profile = {
                    "id": str(sb_user.id),
                    "name": sb_user.user_metadata.get("name", body.email.split("@")[0]),
                    "email": sb_user.email,
                    "avatar": sb_user.user_metadata.get("avatar_url", "")
                }
            
            return {
                "token": session.access_token,
                "user": user_profile,
            }
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(401, f"Invalid email or password: {e}")

    # Dev fallback (no Supabase)
    user = get_user_by_email(body.email)
    if not user or user.get("password") != body.password:
        raise HTTPException(401, "Invalid email or password")
    return {
        "token": str(uuid.uuid4()),
        "user": {"id": user["id"], "name": user["name"], "email": user["email"], "avatar": user.get("avatar", "")},
    }


@router.post("/signup")
async def signup(body: SignupRequest):
    supabase = get_auth_supabase()

    # Real Supabase auth
    if supabase:
        try:
            res = supabase.auth.sign_up({
                "email": body.email,
                "password": body.password,
                "options": {"data": {"name": body.name}},
            })
            sb_user = res.user
            session = res.session
            if not sb_user:
                raise HTTPException(400, "Signup failed")
            # session can be None if email confirmation is required
            token = session.access_token if session else str(uuid.uuid4())
            return {
                "token": token,
                "user": {
                    "id": str(sb_user.id),
                    "name": body.name,
                    "email": sb_user.email,
                    "avatar": "",
                },
            }
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(400, f"Signup failed: {e}")

    # Dev fallback (no Supabase)
    try:
        user = create_user(body.name, body.email, body.password)
    except ValueError as e:
        raise HTTPException(400, str(e))
    return {
        "token": str(uuid.uuid4()),
        "user": {"id": user["id"], "name": user["name"], "email": user["email"], "avatar": user.get("avatar", "")},
    }


@router.delete("/me")
async def delete_account(user_id: str = Depends(get_current_user_id)):
    delete_user_data(user_id)
    return {"status": "success", "message": "Account data deleted"}


class ProfileUpdateRequest(BaseModel):
    name: Optional[str] = None
    avatar_url: Optional[str] = None


@router.get("/profile")
async def get_profile(user_id: str = Depends(get_current_user_id)):
    user = get_user_by_id(user_id)
    if not user:
        raise HTTPException(404, "Profile not found")
    return {"status": "success", "user": user}


@router.patch("/profile")
async def update_profile(body: ProfileUpdateRequest, user_id: str = Depends(get_current_user_id)):
    try:
        updated_user = update_user_profile(user_id, name=body.name, avatar_url=body.avatar_url)
        return {"status": "success", "user": updated_user}
    except ValueError as e:
        raise HTTPException(404, str(e))
    except Exception as e:
        raise HTTPException(500, f"Failed to update profile: {e}")
