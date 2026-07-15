from pydantic import BaseModel, ConfigDict, Field
from pydantic.alias_generators import to_camel

from src.db.models import CrawlMode, CrawlStatus


class OutSchema(BaseModel):
    """Base for response payloads: serializes Python snake_case fields as camelCase so
    the UI's existing `types.ts` interfaces can consume responses as-is."""

    model_config = ConfigDict(
        alias_generator=to_camel, populate_by_name=True, from_attributes=True
    )


class JobCountsOut(OutSchema):
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "queued": 1,
                "running": 2,
                "completed": 14,
                "failed": 1,
                "cancelled": 0,
            }
        }
    )

    queued: int
    running: int
    completed: int
    failed: int
    cancelled: int


class RecentJobOut(OutSchema):
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "id": "6f1c9e2a-9b3d-4b1e-9b3d-6f1c9e2a9b3d",
                "targetUrl": "https://example.com/blog",
                "status": "completed",
                "mode": "crawler",
                "createdAt": 1752480000000,
                "urlsDiscovered": 52,
                "urlsScraped": 50,
            }
        }
    )

    id: str
    target_url: str
    status: CrawlStatus
    mode: CrawlMode
    created_at: int
    urls_discovered: int
    urls_scraped: int


class DashboardOverviewOut(OutSchema):
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "totalJobs": 18,
                "jobCounts": {
                    "queued": 1,
                    "running": 2,
                    "completed": 14,
                    "failed": 1,
                    "cancelled": 0,
                },
                "urlsDiscovered": 940,
                "urlsScraped": 905,
                "urlsFailed": 12,
                "recentJobs": [
                    {
                        "id": "6f1c9e2a-9b3d-4b1e-9b3d-6f1c9e2a9b3d",
                        "targetUrl": "https://example.com/blog",
                        "status": "completed",
                        "mode": "crawler",
                        "createdAt": 1752480000000,
                        "urlsDiscovered": 52,
                        "urlsScraped": 50,
                    }
                ],
            }
        }
    )

    total_jobs: int
    job_counts: JobCountsOut
    urls_discovered: int
    urls_scraped: int
    urls_failed: int
    recent_jobs: list[RecentJobOut] = Field(default_factory=list)
