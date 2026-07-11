"""Add user_id to crawl_jobs so each job is scoped to its owner.

Revision ID: 0007
Revises: 0006
Create Date: 2026-07-11

NOTE: this adds a NOT NULL foreign key with no default. If crawl_jobs
already has rows, this migration will fail — there is no way to attribute
existing jobs to a user after the fact. Truncate crawl_jobs (cascades to
discovered_urls/crawl_result_items/log_lines) or backfill user_id by hand
before running this against a database with existing crawl history.
"""

from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

revision: str = "0007"
down_revision: str | None = "0006"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        "crawl_jobs",
        sa.Column("user_id", postgresql.UUID(as_uuid=False), nullable=False),
    )
    op.create_foreign_key(
        "fk_crawl_jobs_user_id_users",
        "crawl_jobs",
        "users",
        ["user_id"],
        ["id"],
        ondelete="CASCADE",
    )


def downgrade() -> None:
    op.drop_constraint("fk_crawl_jobs_user_id_users", "crawl_jobs", type_="foreignkey")
    op.drop_column("crawl_jobs", "user_id")
