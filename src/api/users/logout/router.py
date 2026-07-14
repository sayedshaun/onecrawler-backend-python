import time

import jwt
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.security.dependencies import CurrentUser, get_current_user
from src.api.users.logout.schema import LogoutOut, LogoutRequest
from src.core.pool import get_arq_pool
from src.core.security import decode_access_token
from src.core.sessions import revoke_refresh_session
from src.db.pg import get_db

router = APIRouter()


@router.post("/logout", response_model=LogoutOut)
async def logout(
    payload: LogoutRequest | None = None,
    db: AsyncSession = Depends(get_db),
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
        is_own_refresh_token = (
            claims is not None
            and claims.get("type") == "refresh"
            and claims.get("sub") == current_user.id
        )
        if is_own_refresh_token:
            await revoke_refresh_session(db, jti=claims["jti"])
            await db.commit()

    return LogoutOut(detail="Logged out")
