import json

from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import Response
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.security.dependencies import CurrentUser, get_current_user
from src.api.v1.data.schema import DataItemDetailOut, DataItemOut, DataListOut
from src.db.models import CrawlJob, CrawlResultItem
from src.db.pg import get_db

router = APIRouter(prefix="/data", tags=["Data"])


@router.get("", response_model=DataListOut)
async def list_data(
    job_id: str | None = None,
    format: str | None = None,
    q: str | None = None,
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user),
):
    count_query = (
        select(func.count())
        .select_from(CrawlResultItem)
        .join(CrawlJob, CrawlJob.id == CrawlResultItem.job_id)
        .where(CrawlJob.user_id == current_user.id)
    )
    query = (
        select(CrawlResultItem, CrawlJob.target_url)
        .join(CrawlJob, CrawlJob.id == CrawlResultItem.job_id)
        .where(CrawlJob.user_id == current_user.id)
    )
    if job_id:
        count_query = count_query.where(CrawlResultItem.job_id == job_id)
        query = query.where(CrawlResultItem.job_id == job_id)
    if format:
        count_query = count_query.where(CrawlResultItem.format == format)
        query = query.where(CrawlResultItem.format == format)
    if q:
        like = f"%{q}%"
        search_clause = (
            CrawlResultItem.title.ilike(like)
            | CrawlResultItem.url.ilike(like)
            | CrawlResultItem.preview.ilike(like)
        )
        count_query = count_query.where(search_clause)
        query = query.where(search_clause)

    total = await db.scalar(count_query)
    rows = await db.execute(
        query.order_by(CrawlResultItem.extracted_at.desc()).limit(limit).offset(offset)
    )

    items = [
        DataItemOut(
            id=item.id,
            job_id=item.job_id,
            target_url=target_url,
            url=item.url,
            title=item.title,
            word_count=item.word_count,
            format=item.format,
            extracted_at=item.extracted_at,
            preview=item.preview,
        )
        for item, target_url in rows.all()
    ]

    return DataListOut(items=items, total=total, limit=limit, offset=offset)


@router.get("/{result_id}", response_model=DataItemDetailOut)
async def get_data_item(
    result_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user),
):
    row = await db.execute(
        select(CrawlResultItem, CrawlJob.target_url)
        .join(CrawlJob, CrawlJob.id == CrawlResultItem.job_id)
        .where(CrawlResultItem.id == result_id, CrawlJob.user_id == current_user.id)
    )
    found = row.first()
    if found is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Result not found"
        )

    item, target_url = found

    return DataItemDetailOut(
        id=item.id,
        job_id=item.job_id,
        target_url=target_url,
        url=item.url,
        title=item.title,
        word_count=item.word_count,
        format=item.format,
        extracted_at=item.extracted_at,
        preview=item.preview,
        content=item.content,
    )


@router.get("/{result_id}/download")
async def download_data_item(
    result_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user),
):
    row = await db.execute(
        select(CrawlResultItem)
        .join(CrawlJob, CrawlJob.id == CrawlResultItem.job_id)
        .where(CrawlResultItem.id == result_id, CrawlJob.user_id == current_user.id)
    )
    item = row.scalar_one_or_none()
    if item is None:
        raise HTTPException(status_code=404, detail="Result not found")

    return Response(
        content=json.dumps(item.content, ensure_ascii=False, indent=2),
        media_type="application/json",
        headers={"Content-Disposition": f'attachment; filename="{item.id}.json"'},
    )
