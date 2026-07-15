from pydantic import BaseModel, ConfigDict, EmailStr, Field
from pydantic.alias_generators import to_camel

from src.api.v1.dashboard.schema import JobCountsOut


class InSchema(BaseModel):
    """Base for request payloads: accepts the UI's snake_case fields as-is."""

    model_config = ConfigDict(extra="ignore")


class OutSchema(BaseModel):
    """Base for response payloads: serializes Python snake_case fields as camelCase so
    the UI's existing `types.ts` interfaces can consume responses as-is."""

    model_config = ConfigDict(
        alias_generator=to_camel, populate_by_name=True, from_attributes=True
    )


class RenameRequest(InSchema):
    model_config = ConfigDict(json_schema_extra={"example": {"name": "Jane Doe"}})

    name: str = Field(min_length=1)


class ChangeEmailRequest(InSchema):
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "email": "jane.new@example.com",
                "password": "correct-horse-battery-staple",
            }
        }
    )

    email: EmailStr
    password: str


class ChangePasswordRequest(InSchema):
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "current_password": "correct-horse-battery-staple",
                "new_password": "another-strong-password-1",
            }
        }
    )

    current_password: str
    new_password: str = Field(min_length=8)


class ChangePasswordOut(OutSchema):
    model_config = ConfigDict(
        json_schema_extra={"example": {"detail": "Password changed successfully"}}
    )

    detail: str


class UsageOut(OutSchema):
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
                "jobsThisMonth": 6,
                "urlsScrapedThisMonth": 310,
            }
        }
    )

    total_jobs: int
    job_counts: JobCountsOut
    urls_discovered: int
    urls_scraped: int
    urls_failed: int
    jobs_this_month: int
    urls_scraped_this_month: int
