from fastapi import APIRouter, Depends
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.security.dependencies import CurrentUser, get_current_user
from src.api.v1.dashboard.schema import DashboardOverviewOut, JobCountsOut, RecentJobOut
from src.db.models import CrawlJob, CrawlStatus
from src.db.pg import get_db

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


@router.get("/overview", response_model=DashboardOverviewOut)
async def get_overview(
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user),
):
    status_result = await db.execute(
        select(CrawlJob.status, func.count())
        .where(CrawlJob.user_id == current_user.id)
        .group_by(CrawlJob.status)
    )
    job_counts = {status: 0 for status in CrawlStatus}
    for status, count in status_result.all():
        job_counts[status] = count

    url_row = await db.execute(
        select(
            func.coalesce(func.sum(CrawlJob.urls_discovered), 0),
            func.coalesce(func.sum(CrawlJob.urls_scraped), 0),
            func.coalesce(func.sum(CrawlJob.urls_failed), 0),
        ).where(CrawlJob.user_id == current_user.id)
    )
    urls_discovered, urls_scraped, urls_failed = url_row.one()

    total = await db.scalar(
        select(func.count())
        .select_from(CrawlJob)
        .where(CrawlJob.user_id == current_user.id)
    )

    recent_result = await db.execute(
        select(CrawlJob)
        .where(CrawlJob.user_id == current_user.id)
        .order_by(CrawlJob.created_at.desc())
        .limit(10)
    )
    recent = list(recent_result.scalars().all())

    return DashboardOverviewOut(
        total_jobs=total,
        job_counts=JobCountsOut(**job_counts),
        urls_discovered=int(urls_discovered),
        urls_scraped=int(urls_scraped),
        urls_failed=int(urls_failed),
        recent_jobs=[RecentJobOut.model_validate(job) for job in recent],
    )
