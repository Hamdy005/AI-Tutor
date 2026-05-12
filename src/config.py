import os
from functools import lru_cache
from pathlib import Path

from dotenv import load_dotenv


ENV_PATH = Path(__file__).resolve().parents[1] / "config.env"
load_dotenv(ENV_PATH)


class Settings:
    openrouter_api_key: str = os.getenv("OPENROUTER_API_KEY", "")
    openrouter_base_url: str = os.getenv(
        "OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1"
    )
    # Accept both plain and NEXT_PUBLIC_ prefixed names (config.env uses NEXT_PUBLIC_)
    supabase_url: str = (
        os.getenv("SUPABASE_URL")
        or os.getenv("NEXT_PUBLIC_SUPABASE_URL", "")
    )
    supabase_key: str = (
        os.getenv("SUPABASE_KEY")
        or os.getenv("NEXT_PUBLIC_SUPABASE_KEY", "")
    )
    supabase_anon_key: str = (
        os.getenv("SUPABASE_ANON_KEY")
        or os.getenv("NEXT_PUBLIC_SUPABASE_ANON_KEY", "")
    )
    groq_api_key: str = os.getenv("GROQ_API_KEY", "")
    model_name: str = os.getenv("MODEL_NAME", "openai/gpt-oss-120b")
    transformers_no_tf: str = os.getenv("TRANSFORMERS_NO_TF", "1")
    cors_allowed_origins: list[str] = [
        origin.strip()
        for origin in os.getenv("CORS_ALLOWED_ORIGINS", "").split(",")
        if origin.strip()
    ]


@lru_cache()
def get_settings() -> Settings:
    s = Settings()
    if s.openrouter_api_key:
        os.environ["OPENROUTER_API_KEY"] = s.openrouter_api_key
    if s.openrouter_base_url:
        os.environ["OPENROUTER_BASE_URL"] = s.openrouter_base_url
    if "TRANSFORMERS_NO_TF" not in os.environ and s.transformers_no_tf:
        os.environ["TRANSFORMERS_NO_TF"] = s.transformers_no_tf
    return s


settings = get_settings()
