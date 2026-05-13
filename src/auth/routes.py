import uuid
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from src.database import get_auth_supabase
from src.store import create_user, get_user_by_email

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
            return {
                "token": session.access_token,
                "user": {
                    "id": str(sb_user.id),
                    "name": sb_user.user_metadata.get("name", body.email.split("@")[0]),
                    "email": sb_user.email,
                },
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
        "user": {"id": user["id"], "name": user["name"], "email": user["email"]},
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
        "user": {"id": user["id"], "name": user["name"], "email": user["email"]},
    }
