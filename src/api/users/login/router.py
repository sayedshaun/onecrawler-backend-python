from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.users.login.schema import LoginRequest, TokenOut
from src.core.config import settings
from src.core.security import create_access_token, create_refresh_token, verify_password
from src.db.models import Users
from src.db.pg import get_db

router = APIRouter()


@router.post("/login", response_model=TokenOut)
async def login(payload: LoginRequest, db: AsyncSession = Depends(get_db)):
    invalid = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password"
    )

    user = await db.scalar(select(Users).where(Users.email == payload.email))
    if user is None or not verify_password(payload.password, user.hashed_password):
        raise invalid

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Account is disabled"
        )

    token = create_access_token(
        user_id=user.id, email=user.email, user_type=user.user_type, name=user.name
    )
    refresh_token = create_refresh_token(user_id=user.id)
    return TokenOut(
        access_token=token,
        refresh_token=refresh_token,
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    )
