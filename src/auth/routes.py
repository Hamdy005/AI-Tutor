import uuid
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional

from src.store import create_user, get_user_by_email

router = APIRouter(prefix="/api/auth", tags=["Auth"])


class LoginRequest(BaseModel):
    email: str
    password: str


class SignupRequest(BaseModel):
    name: str
    email: str
    password: str


class GoogleAuthRequest(BaseModel):
    token: str
    name: Optional[str] = None
    email: Optional[str] = None


@router.post("/login")
async def login(body: LoginRequest):
    user = get_user_by_email(body.email)
    if not user or user.get("password") != body.password:
        raise HTTPException(401, "Invalid email or password")
    token = str(uuid.uuid4())
    return {
        "token": token,
        "user": {
            "id": user["id"],
            "name": user["name"],
            "email": user["email"],
        },
    }


@router.post("/signup")
async def signup(body: SignupRequest):
    try:
        user = create_user(body.name, body.email, body.password)
    except ValueError as e:
        raise HTTPException(400, str(e))
    token = str(uuid.uuid4())
    return {
        "token": token,
        "user": {
            "id": user["id"],
            "name": user["name"],
            "email": user["email"],
        },
    }


@router.post("/google")
async def google_auth(body: GoogleAuthRequest):
    email = body.email or f"google_{uuid.uuid4().hex[:8]}@google.com"
    name = body.name or "Google User"
    user = get_user_by_email(email)
    if not user:
        user = create_user(name, email, "")
    token = str(uuid.uuid4())
    return {
        "token": token,
        "user": {
            "id": user["id"],
            "name": user["name"],
            "email": user["email"],
        },
    }
