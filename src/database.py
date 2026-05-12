from typing import Optional
from supabase import Client, create_client
from src.config import settings


def get_supabase() -> Optional[Client]:
    if not settings.supabase_url or not settings.supabase_key:
        return None
    return create_client(settings.supabase_url, settings.supabase_key)


def get_auth_supabase() -> Optional[Client]:
    if not settings.supabase_url or not settings.supabase_anon_key:
        return None
    return create_client(settings.supabase_url, settings.supabase_anon_key)