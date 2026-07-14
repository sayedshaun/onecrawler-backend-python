import time
from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncSession

from src.db.models import RefreshSession


async def record_refresh_session(
    db: AsyncSession, user_id: str, jti: str, expires_at: datetime
) -> None:
    db.add(
        RefreshSession(
            jti=jti,
            user_id=user_id,
            created_at=int(time.time() * 1000),
            expires_at=int(expires_at.timestamp() * 1000),
        )
    )


async def revoke_refresh_session(db: AsyncSession, jti: str) -> None:
    session = await db.get(RefreshSession, jti)
    if session is not None and session.revoked_at is None:
        session.revoked_at = int(time.time() * 1000)
