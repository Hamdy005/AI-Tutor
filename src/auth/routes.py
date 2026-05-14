import uuid
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from src.database import get_auth_supabase
from src.store import create_user, get_user_by_email, delete_user_data, update_user_profile, get_user_by_id
from src.dependencies import get_current_user_id, get_current_user
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
                try:
                    user_profile = create_user(
                        name=sb_user.user_metadata.get("name", body.email.split("@")[0]),
                        email=sb_user.email,
                        password="",
                        user_id=str(sb_user.id)
                    )
                except Exception:
                    pass

                if not user_profile:
                    # Final fallback to metadata
                    user_profile = {
                        "id": str(sb_user.id),
                        "name": sb_user.user_metadata.get("name", body.email.split("@")[0]),
                        "email": sb_user.email,
                        "avatar": sb_user.user_metadata.get("avatar_url", ""),
                        "usage": {"used": 0, "limit": 10, "remaining": 10}
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
        "user": user,
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
            # Create profile in our database
            try:
                create_user(
                    name=body.name,
                    email=sb_user.email,
                    password="",
                    user_id=str(sb_user.id)
                )
            except Exception:
                pass

            return {
                "token": token,
                "user": {
                    "id": str(sb_user.id),
                    "name": body.name,
                    "email": sb_user.email,
                    "avatar": "",
                    "usage": {"used": 0, "limit": 10, "remaining": 10}
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
        "user": user,
    }


@router.delete("/me")
async def delete_account(user_id: str = Depends(get_current_user_id)):
    delete_user_data(user_id)
    return {"status": "success", "message": "Account data deleted"}


class ProfileUpdateRequest(BaseModel):
    name: Optional[str] = None
    avatar_url: Optional[str] = None
    theme: Optional[str] = None


@router.get("/profile")
async def get_profile(
    user_id: str = Depends(get_current_user_id),
    current_user=Depends(get_current_user)
):
    user = get_user_by_id(user_id)
    
    # Identify if the email is a temporary placeholder
    email = user.get("email", "") if user else ""
    is_placeholder = not user or "@placeholder.ai" in email or "@studymate.ai" in email or "user" in email
    
    if is_placeholder:
        # Try to get DEFINITELY REAL data from Supabase Auth using the service role client
        from src.database import get_supabase
        supabase = get_supabase()
        if supabase:
            try:
                # Use admin API to get real user data
                res = supabase.auth.admin.get_user_by_id(user_id)
                if res.user and res.user.email and "@" in res.user.email:
                    real_email = res.user.email
                    real_name = res.user.user_metadata.get("name")
                    
                    # Use upsert to create or update the profile with real data
                    from src.store import _table_supabase, _map_profile
                    data = {"id": user_id, "email": real_email}
                    if real_name:
                        data["display_name"] = real_name
                        
                    try:
                        res_upd = _table_supabase("profiles").upsert(data).execute()
                        if res_upd.data:
                            user = _map_profile(res_upd.data[0])
                    except Exception:
                        pass
            except Exception:
                pass
                
    if not user and isinstance(current_user, dict) and current_user.get("id"):
        # Last resort: return data from headers if DB/Supabase both failed
        # This keeps the UI working even if there's a temporary DB issue
        from src.store import _map_profile
        user = _map_profile({
            "id": current_user["id"],
            "display_name": current_user.get("name") or "User",
            "email": current_user.get("email") or "",
            "avatar_url": "",
            "daily_requests": 0,
            "last_request_date": ""
        })

    if not user:
        raise HTTPException(404, "Profile not found")
    return {"status": "success", "user": user}


@router.patch("/profile")
async def update_profile(body: ProfileUpdateRequest, user_id: str = Depends(get_current_user_id)):
    try:
        updated_user = update_user_profile(
            user_id, 
            name=body.name, 
            avatar_url=body.avatar_url,
            theme=body.theme
        )
        return {"status": "success", "user": updated_user}
    except ValueError as e:
        raise HTTPException(404, str(e))
    except Exception as e:
        raise HTTPException(500, f"Failed to update profile: {e}")
