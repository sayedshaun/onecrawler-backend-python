import time

import jwt
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.users.refresh.schema import RefreshOut, RefreshRequest
from src.core.config import settings
from src.core.security import (
    create_access_token,
    create_refresh_token,
    decode_access_token,
)
from src.core.sessions import record_refresh_session, revoke_refresh_session
from src.db.models import RefreshSession, Users
from src.db.pg import get_db

router = APIRouter()


@router.post("/refresh", response_model=RefreshOut)
async def refresh(payload: RefreshRequest, db: AsyncSession = Depends(get_db)):
    invalid = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid or expired refresh token",
    )

    try:
        claims = decode_access_token(payload.refresh_token)
    except jwt.PyJWTError:
        raise invalid

    if claims.get("type") != "refresh":
        raise invalid

    session = await db.get(RefreshSession, claims["jti"])
    now_ms = int(time.time() * 1000)
    if session is None or session.revoked_at is not None or session.expires_at < now_ms:
        raise invalid

    user = await db.get(Users, claims.get("sub"))
    if user is None or not user.is_active:
        raise invalid

    # Rotate: retiring this refresh token as soon as it's used detects reuse
    # by an attacker who stole an earlier copy of it.
    await revoke_refresh_session(db, jti=session.jti)

    access_token = create_access_token(
        user_id=user.id, email=user.email, user_type=user.user_type, name=user.name
    )
    new_refresh_token, new_jti, new_expires_at = create_refresh_token(user_id=user.id)
    await record_refresh_session(
        db, user_id=user.id, jti=new_jti, expires_at=new_expires_at
    )
    await db.commit()

    return RefreshOut(
        access_token=access_token,
        refresh_token=new_refresh_token,
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    )
