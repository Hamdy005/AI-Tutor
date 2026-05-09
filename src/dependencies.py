from fastapi import Header, HTTPException
from typing import Optional

DEV_USER_ID = "00000000-0000-0000-0000-000000000001"


async def get_current_user_id(x_user_id: Optional[str] = Header(None)) -> str:
    if x_user_id:
        return x_user_id
    return DEV_USER_ID
