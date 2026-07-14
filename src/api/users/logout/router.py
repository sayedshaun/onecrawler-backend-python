import time

import jwt
from fastapi import APIRouter, Depends

from src.api.security.dependencies import CurrentUser, get_current_user
from src.api.users.logout.schema import LogoutOut, LogoutRequest
from src.core.pool import get_arq_pool
from src.core.security import decode_access_token

router = APIRouter()


@router.post("/logout", response_model=LogoutOut)
async def logout(
    payload: LogoutRequest | None = None,
    current_user: CurrentUser = Depends(get_current_user),
):
    redis = await get_arq_pool()
    ttl = max(current_user.exp - int(time.time()), 1)
    await redis.setex(f"blocklist:{current_user.jti}", ttl, "1")

    if payload and payload.refresh_token:
        try:
            claims = decode_access_token(payload.refresh_token)
        except jwt.PyJWTError:
            claims = None
        if claims and claims.get("type") == "refresh":
            refresh_ttl = max(claims["exp"] - int(time.time()), 1)
            await redis.setex(f"blocklist:{claims['jti']}", refresh_ttl, "1")

    return LogoutOut(detail="Logged out")
